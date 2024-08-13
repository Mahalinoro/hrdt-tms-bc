import joblib
import pandas as pd
from sklearn.decomposition import PCA
from sklearn.discriminant_analysis import StandardScaler
from sklearn.neighbors import KNeighborsClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from statistics import mean
from sklearn.inspection import permutation_importance
from matplotlib import pyplot

from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
from sklearn.metrics import confusion_matrix
from sklearn.metrics import accuracy_score
from imblearn.over_sampling import SMOTE
from imblearn.combine import SMOTEENN

from sklearn.calibration import calibration_curve, CalibratedClassifierCV
from sklearn.metrics import log_loss, brier_score_loss, roc_auc_score
import matplotlib.pyplot as plt

data = pd.read_csv('./dataset.csv')
data= data.sample(frac=1).reset_index(drop=True)
data = data[['pos_x1','pos_y1','spd_x1','spd_y1','spd_z1','acl1','hed_x1','hed_y1','AttackerType']]
data = data.drop_duplicates()
data = data.dropna()
#change class apart from 0 to 1
data['AttackerType'] = data['AttackerType'].apply(lambda x: 1 if x != 0 else 0)

X = data[['pos_x1','pos_y1','spd_x1','spd_y1','acl1','hed_x1','hed_y1']]
Y = data['AttackerType']

# smote = SMOTE(sampling_strategy='auto', random_state=42)
# X, Y = smote.fit_resample(X, Y)
# smote_enn = SMOTEENN(sampling_strategy='auto', random_state=42)
# X, Y = smote_enn.fit_resample(X, Y)

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

X_train, X_test, y_train, y_test = train_test_split(X_scaled, Y, test_size=0.3, random_state=42)

rf = RandomForestClassifier(n_estimators=20, random_state=42)

# # Evaluate the model
rf.fit(X_train, y_train)
y_pred = rf.predict(X_test)
model_path = f'rf.pkl'
joblib.dump(rf, model_path)
joblib.dump(scaler, 'rf_scaler.pkl')
accuracy = accuracy_score(y_test, y_pred)
print(f'Random Forest Accuracy: {accuracy:.4f}')
print(classification_report(y_test, y_pred))
print('-' * 40)

# Evaluate model
# y_prob_rf = rf.predict_proba(X_test)[:, 1]
# logloss_rf = log_loss(y_test, y_prob_rf)
# brier_rf = brier_score_loss(y_test, y_prob_rf)
# roc_auc_rf = roc_auc_score(y_test, y_prob_rf)

# print(f'Random Forest Log Loss: {logloss_rf}')
# print(f'Random Forest Brier Score: {brier_rf}')
# print(f'Random Forest ROC AUC: {roc_auc_rf}')

# # Calibration plot for uncalibrated Random Forest
# prob_true_rf, prob_pred_rf = calibration_curve(y_test, y_prob_rf, n_bins=10)

# plt.figure(figsize=(10, 6))
# plt.plot(prob_pred_rf, prob_true_rf, marker='o', linewidth=1, label='Random Forest')
# plt.plot([0, 1], [0, 1], linestyle='--', label='Perfectly Calibrated')
# plt.xlabel('Predicted probability')
# plt.ylabel('True probability')
# plt.legend()
# plt.title('Calibration Plot for Random Forest')
# plt.savefig('calibration_plot.png')

