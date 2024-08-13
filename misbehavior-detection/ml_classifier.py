import joblib
import pandas as pd
import numpy as np
import glob
from sklearn.calibration import LabelEncoder
from sklearn.metrics import classification_report
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier

np.random.seed(42)

# Load the model and scaler
model = joblib.load('./model/rf.pkl')
scaler = joblib.load('./model/rf_scaler.pkl')

def preprocess_data_point(data_point):
    features = ['pos_x1','pos_y1','spd_x1','spd_y1','acl1','hed_x1','hed_y1']
    data = pd.DataFrame([data_point], columns=features)
    data = scaler.transform(data)
    return data

def load_and_predict(X):
    prediction = model.predict(X)
    return prediction

# data = pd.read_csv('./simulation_data/vehicles_400_50.csv')
# data = data[['pos_x1','pos_y1','spd_x1','spd_y1','spd_z1','acl1','hed_x1','hed_y1','AttackerType']]
# data['AttackerType'] = data['AttackerType'].apply(lambda x: 1 if x != 0 else 0)
# X = data[['pos_x1','pos_y1','spd_x1','spd_y1','acl1','hed_x1','hed_y1']]
# Y = data['AttackerType']
# data_point = [866.3108073484117,532.5943374331337,-2.899970757288141,-19.597475058754835,-0.4823920354627124,-0.7455777904376559,-0.666418605987335]
# X_scaled = preprocess_data_point(data_point)
# y_pred = load_and_predict(X_scaled)
# print(y_pred)
# print(classification_report(Y, y_pred))


