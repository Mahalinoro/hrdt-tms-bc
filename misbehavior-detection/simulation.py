import pandas as pd
import numpy as np
from haversine import haversine
from random import *
import fusion
import dempster_shafer
import ml_classifier
import joblib
import matplotlib.pyplot as plt
from scipy.interpolate import make_interp_spline


np.random.seed(42)

def initialize_vehicle(csv_file):
    vehicles = {}
    df = pd.read_csv(csv_file)
    df['AttackerType'] = df['AttackerType'].apply(lambda x: 1 if x != 0 else 0)
    for index, row in df.iterrows():
        vehicles[int(row['receiver'])] = {
            'pos_x1': row['pos_x1'],
            'pos_y1': row['pos_y1'],
            'spd_x1': row['spd_x1'],
            'spd_y1': row['spd_y1'],
            'acl1': row['acl1'],
            'hed_x1': row['hed_x1'],
            'hed_y1': row['hed_y1'],
            'att': row['AttackerType'],
            't_score': np.random.uniform(0.7, 0.9)
        } 
    return vehicles

def select_neighbors(vehicles, r_vehicle, n_neighbors = 5):    
    distances = []
    for vehicle_id, vehicle_info in vehicles.items():
        if vehicle_id != r_vehicle[0]:
            d = haversine((vehicle_info['pos_x1'], vehicle_info['pos_y1']), (r_vehicle[1]['pos_x1'], r_vehicle[1]['pos_y1']), normalize=True)
            distances.append((vehicle_id, d))
    distances.sort(key=lambda x: x[1])

    neighbors = []
    for i in distances[:n_neighbors]:
        neighbors.append((i[0], vehicles[i[0]]))
    return neighbors

def generate_event(vehicles): 
    event_id = randint(1, 1000) 
    r_vehicle = choice(list(vehicles.items()))
    state = choice([True, False])
    return {'id': event_id, 'state': state, 'reporting_vehicle': r_vehicle}

def collect_judgement(neighbors, event):
    judgements = []
    trust_scores = []
    for n in neighbors:
        if n[1]['att'] == 0:
            if random() > 0.2:
                if event['state'] == True:
                    judgements.append(1)
                else:
                    judgements.append(0)
            else:
                if event['state'] == True:
                    judgements.append(0)
                else:
                    judgements.append(1)
        else:
            if random() > 0.8:
                if event['state'] == True:
                    judgements.append(0)
                else:
                    judgements.append(1)
            else: 
                if event['state'] == True:
                    judgements.append(1)
                else:
                    judgements.append(0)
        trust_scores.append(n[1]['t_score'])

    return [event['id'], judgements, trust_scores]

## Review this classifier with updated features and model from ml_classifier
def rf_classifier(r_vehicle):
    r_vehicle_feature = [r_vehicle[1]['pos_x1'], r_vehicle[1]['pos_y1'], r_vehicle[1]['spd_x1'], r_vehicle[1]['spd_y1'], 
                     r_vehicle[1]['acl1'], r_vehicle[1]['hed_x1'], r_vehicle[1]['hed_y1']]
    r_vehicle_feature = np.array(r_vehicle_feature)
    r_vehicle_feature_scaled = ml_classifier.preprocess_data_point(r_vehicle_feature)
    prediction = ml_classifier.load_and_predict(r_vehicle_feature_scaled)
    return prediction
    
def simulation(vehicles, n_events, time):
    average_trust_scores = {'genuine': [], 'malicious': []}

    for t in range(time):
        print("Start of simulation at time " + str(t))
        print("Generate events:")
        events = [generate_event(vehicles) for i in range(n_events)]

        for event in events:
            r_vehicle = event['reporting_vehicle']
            print(r_vehicle[1]['att'])
            print("Selecting neighbors for vehicle " + str(r_vehicle[0]))
            neighbors = select_neighbors(vehicles, r_vehicle)
            print("Collect judgement for event " + str(event['id']))
            judgement = collect_judgement(neighbors, event)
            print("Perform DST on " + str(event['id']))
            dst = dempster_shafer.dst(judgement[1], judgement[2])
            print(dst)
            print("Classify behavior of " + str(r_vehicle[0]))
            misbehavior_detection = rf_classifier(r_vehicle)
            if misbehavior_detection != 0:
                misbehavior_detection = 1
            print(misbehavior_detection)
            print("Calculate the new trust score of  " + str(r_vehicle[0]))
            t_new = fusion.fuse_observation(r_vehicle[1]['t_score'], misbehavior_detection, dst)
            print("Trust score updated for  " + str(r_vehicle[0]))
            vehicles[r_vehicle[0]]['t_score'] = t_new
            print(vehicles[r_vehicle[0]]['t_score'])
        
        genuine_scores = [v_info['t_score'] for v_id, v_info in vehicles.items() if v_info['att'] == 0]
        malicious_scores = [v_info['t_score'] for v_id, v_info in vehicles.items() if v_info['att'] == 1]

        average_trust_scores['genuine'].append(np.mean(genuine_scores))
        average_trust_scores['malicious'].append(np.mean(malicious_scores))

        print("--------------------------------------")
    
    return vehicles, average_trust_scores

def plot_average_trust_score_time(average_trust_scores, time):
    plt.figure(figsize=(7.30, 3.50))
    
    intervals = [0, 40, 80, 120, 160, 199]
    # print(average_trust_scores['genuine'][200])
    y_genuine_intervals = [average_trust_scores['genuine'][i] for i in intervals]
    y_malicious_intervals = [average_trust_scores['malicious'][i] for i in intervals]
    
    # Plot the smoothed lines
    plt.plot(intervals, y_genuine_intervals, label='Genuine Vehicles (n=400, 50% malicious)', color='palevioletred', marker='o', alpha=0.7)
    plt.plot(intervals, y_malicious_intervals, label='Malicious Vehicles (n=400, 50% malicious)', linestyle='--', color='lightskyblue', marker='o', alpha=0.7)
    
    plt.xlabel('Time')
    plt.ylabel('Average Trust Score')
    plt.legend(loc='lower right')
    plt.margins(x=0)
    plt.ylim(0, 1)
    plt.xlim(0, time)
    plt.grid(color='gray', which='both', linewidth=0.05)
    
    # Customize x-axis ticks to show specific intervals
    plt.xticks(np.arange(0, time + 1, 40))  # Custom x-axis ticks

    plt.tight_layout()
    plt.savefig('Average_Tscore.png', dpi=300)


time = 200
n_events = 10
vehicles = initialize_vehicle('./simulation_data/vehicles_400_50.csv')
v_50, average_trust_scores_50 = simulation(vehicles, n_events, time)
vehicles = initialize_vehicle('./simulation_data/vehicles_400_30.csv')
v_30, average_trust_scores_30 = simulation(vehicles, n_events, time)
vehicles = initialize_vehicle('./simulation_data/vehicles_400_20.csv')
v_20, average_trust_scores_20 = simulation(vehicles, n_events, time)
# plot_average_trust_score_time(average_trust_scores, time)
fig, ax = plt.subplots(layout='constrained')

intervals = [0, 40, 80, 120, 160, 199]
# print(average_trust_scores['genuine'][200])
y_genuine_intervals_50 = [average_trust_scores_50['genuine'][i] for i in intervals]
y_malicious_intervals_50 = [average_trust_scores_50['malicious'][i] for i in intervals]

y_genuine_intervals_30 = [average_trust_scores_30['genuine'][i] for i in intervals]
y_malicious_intervals_30 = [average_trust_scores_30['malicious'][i] for i in intervals]

y_genuine_intervals_20 = [average_trust_scores_20['genuine'][i] for i in intervals]
y_malicious_intervals_20 = [average_trust_scores_20['malicious'][i] for i in intervals]

# Plot the smoothed lines
ax.plot(intervals, y_genuine_intervals_50, label='Genuine Vehicles (n=400, 50% malicious)', color='palevioletred', marker='o', alpha=0.7)
ax.plot(intervals, y_malicious_intervals_50, label='Malicious Vehicles (n=400, 50% malicious)', linestyle='--', color='lightskyblue', marker='o', alpha=0.7)
ax.plot(intervals, y_genuine_intervals_30, label='Genuine Vehicles (n=400, 30% malicious)', color='seagreen', marker='o', alpha=0.7)
ax.plot(intervals, y_malicious_intervals_30, label='Malicious Vehicles (n=400, 30% malicious)', linestyle='--', color='sandybrown', marker='o', alpha=0.7)
ax.plot(intervals, y_genuine_intervals_20, label='Genuine Vehicles (n=400, 20% malicious)', color='slategrey', marker='o', alpha=0.7)
ax.plot(intervals, y_malicious_intervals_20, label='Malicious Vehicles (n=400, 20% malicious)', linestyle='--', color='gold', marker='o', alpha=0.7)

plt.xlabel('Time')
plt.ylabel('Average Trust Score')
plt.legend(loc='lower left')
plt.margins(x=0)
plt.ylim(0, 1)
plt.xlim(0, time)
plt.grid(color='gray', which='both', linewidth=0.05)

# Customize x-axis ticks to show specific intervals
plt.xticks(np.arange(0, time + 1, 40))  # Custom x-axis ticks
plt.savefig('Average_Tscore-v1.png', dpi=300)