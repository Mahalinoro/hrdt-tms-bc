import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import ml_classifier
from sklearn.metrics import confusion_matrix


# # Data for multiple percentages for each number of vehicles
n_vehicles = [100, 200, 400]
percent_malicious = [20, 30, 50]
precision = []
recall = []

# Process dataset for rf model prediction
for j in range(len(n_vehicles)):
    for i in range(len(percent_malicious)):
        data = pd.read_csv(f'./simulation_data/vehicles_{n_vehicles[j]}_{percent_malicious[i]}.csv')
        data = data[['pos_x1','pos_y1','spd_x1','spd_y1','spd_z1','acl1','hed_x1','hed_y1','AttackerType']]
        data['AttackerType'] = data['AttackerType'].apply(lambda x: 1 if x != 0 else 0)
        X = data[['pos_x1','pos_y1','spd_x1','spd_y1','acl1','hed_x1','hed_y1']]
        Y = data['AttackerType']
        X_scaled = ml_classifier.preprocess_data_point(X)
        y_pred = ml_classifier.load_and_predict(X_scaled)
        # Calculate recall
        cm = confusion_matrix(Y, y_pred)
        TN, FP, FN, TP = cm.ravel()
        TPR = TP / (TP + FN) if (TP + FN) > 0 else 0
        # # calculate precision
        # precision.append(TP / (TP + FP) if (TP + FP) > 0 else 0)
        # binary_true_labels = [1 if label != 0 else 0 for label in Y]
        # binary_pred_labels = [1 if label != 0 else 0 for label in y_pred]
        # # Calculate TP and FN
        # TP = sum(1 for true, pred in zip(binary_true_labels, binary_pred_labels) if true == 1 and pred == 1)
        # FN = sum(1 for true, pred in zip(binary_true_labels, binary_pred_labels) if true == 1 and pred == 0)

        # # Calculate TPR
        # TPR = TP / (TP + FN) if (TP + FN) > 0 else 0
        recall.append(TPR)

n_vehicles = (100, 200, 400)
# precision = {
#     '20% malicious vehicle': (precision[0], precision[1], precision[2]),
#     '30% malicious vehicle': (precision[3], precision[4], precision[5]),
#     '50% malicious vehicle': (precision[6], precision[7], precision[8])
# }

recall = {
    '20% malicious vehicles': (recall[0], recall[1], recall[2]),
    '30% malicious vehicles': (recall[3], recall[4], recall[5]),
    '50% malicious vehicles': (recall[6], recall[7], recall[8])
}

x = np.arange(len(n_vehicles))  # the label locations
width = 0.15  # the width of the bars
multiplier = 0
hatches = ['x', '', '/']
# Create figure and axes
fig, ax = plt.subplots(layout='constrained')

for attribute, measurement in recall.items():
    offset = width * multiplier
    rects = ax.bar(x + offset, measurement, width, label=attribute, hatch=hatches[multiplier % len(hatches)], color=['sandybrown', 'palevioletred', 'seagreen'][multiplier], alpha=0.7, edgecolor='black')
    multiplier += 1
print(recall)
# Add some text for labels, title and custom x-axis tick labels, etc.
ax.set_ylabel('TPR (%)')
ax.set_xlabel('Number of Nodes')
ax.set_xticks(x + width, n_vehicles)
ax.legend(loc='lower right')
ax.set_ylim(0, 1.1)
plt.grid(color='gray', linewidth=0.05)
# Show plot
plt.savefig('TPR.png', dpi=300)
