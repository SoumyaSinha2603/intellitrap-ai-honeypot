import joblib
import numpy as np
import pandas as pd
from tensorflow.keras.models import load_model
classifier = joblib.load("ml/log_classifier.pkl")
anomaly_model = joblib.load("ml/anomaly_detector.pkl")
lstm_model = load_model("ml/lstm_attack_path_model.h5")
df = pd.read_csv("ml/attacker_dataset.csv")

X = df.drop(columns=["label"])
malicious_prob = classifier.predict_proba(X)[:, 1]
raw_anomaly = anomaly_model.decision_function(X)
# Normalize anomaly score to 0–1
anomaly_score = (raw_anomaly - raw_anomaly.min()) / (
    raw_anomaly.max() - raw_anomaly.min()
)

df["anomaly_score"] = anomaly_score
# heuristic: longer sequences = higher risk
sequence_risk = np.clip(df["request_count"] / df["request_count"].max(), 0, 1)
threat_score = (
    0.5 * malicious_prob +
    0.3 * (1 - df["anomaly_score"]) +
    0.2 * sequence_risk
) * 100
def risk_level(score):
    if score > 70:
        return "HIGH"
    elif score > 40:
        return "MEDIUM"
    else:
        return "LOW"

df["threat_score"] = threat_score
df["risk_level"] = df["threat_score"].apply(risk_level)
print("\nThreat Assessment (Detailed):")
print(df[[
    "request_count",
    "sql_keyword_count",
    "anomaly_score",
    "threat_score",
    "risk_level"
]])
