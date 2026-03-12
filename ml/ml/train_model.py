import pandas as pd
import numpy as np
import json

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, f1_score

from xgboost import XGBClassifier
import joblib


# -----------------------------
# 1 Load Dataset
# -----------------------------
df = pd.read_csv("ml/dataset.csv")

# -----------------------------
# 2 Shuffle Dataset
# -----------------------------
df = df.sample(frac=1, random_state=42).reset_index(drop=True)


# -----------------------------
# 3 Feature Engineering
# -----------------------------
df["typing_error_rate"] = df["backspace_count"] / (df["typing_speed"] + 1)

df["mouse_efficiency"] = df["cursor_path_length"] / (df["mouse_movement_speed"] + 1)

df["network_risk"] = df["ip_address_risk"] + df["vpn_detected"] + df["tor_detected"]

df["behavior_score"] = df["typing_speed"] * df["keystroke_variance"]

df["login_pressure"] = df["failed_attempts_last_10min"] * df["session_request_rate"]


# -----------------------------
# 4 Encode Categorical Columns
# -----------------------------
le_device = LabelEncoder()
le_browser = LabelEncoder()
le_attack = LabelEncoder()

df["device_type"] = le_device.fit_transform(df["device_type"])
df["browser_type"] = le_browser.fit_transform(df["browser_type"])
df["attack"] = le_attack.fit_transform(df["attack"])


# -----------------------------
# 5 Features / Labels
# -----------------------------
X = df.drop(["label", "attack", "is_attacker"], axis=1)
y = df["label"]


# -----------------------------
# 6 Train Test Split
# -----------------------------
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    stratify=y,
    random_state=42
)


# -----------------------------
# 7 Feature Scaling
# -----------------------------
scaler = StandardScaler()

X_train = scaler.fit_transform(X_train)
X_test = scaler.transform(X_test)


# -----------------------------
# 8 Train Final XGBoost Model
# -----------------------------
model = XGBClassifier(
    subsample=0.9,
    n_estimators=200,
    min_child_weight=3,
    max_depth=4,
    learning_rate=0.01,
    gamma=0.1,
    colsample_bytree=0.9,
    scale_pos_weight=2.9,
    tree_method="hist",
    eval_metric="logloss",
    random_state=42
)

model.fit(X_train, y_train)


# -----------------------------
# 9 Prediction Probabilities
# -----------------------------
y_prob = model.predict_proba(X_test)[:, 1]


# -----------------------------
# 10 Find Best Threshold
# -----------------------------
thresholds = np.arange(0.2, 0.6, 0.01)

best_f1 = 0
best_t = 0.5

for t in thresholds:

    pred = (y_prob > t).astype(int)

    f1 = f1_score(y_test, pred)

    if f1 > best_f1:
        best_f1 = f1
        best_t = t


print("\nBest Threshold:", best_t)
print("Best F1 Score:", best_f1)


# Final Predictions
y_pred = (y_prob > best_t).astype(int)


# -----------------------------
# 11 Evaluation
# -----------------------------
print("\nAccuracy:", accuracy_score(y_test, y_pred))

print("\nClassification Report:\n")
print(classification_report(y_test, y_pred))

print("\nConfusion Matrix:\n")
print(confusion_matrix(y_test, y_pred))


# -----------------------------
# 12 Save Model + Scaler + Config
# -----------------------------
joblib.dump(model, "ml/login_attack_model.pkl")
joblib.dump(scaler, "ml/scaler.pkl")

config = {"threshold": float(best_t)}

with open("ml/model_config.json", "w") as f:
    json.dump(config, f)

print("\nModel saved successfully.")