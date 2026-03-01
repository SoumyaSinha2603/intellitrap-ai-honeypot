import pandas as pd
import joblib
from sklearn.ensemble import IsolationForest
DATASET_PATH = "ml/attacker_dataset.csv"

df = pd.read_csv(DATASET_PATH)

print("Dataset loaded:")
print(df)
X = df.drop(columns=["label"])
model = IsolationForest(
    n_estimators=100,
    contamination=0.3,  # expected anomaly ratio
    random_state=42
)

model.fit(X)

print("Anomaly detection model trained")
df["anomaly_score"] = model.decision_function(X)
df["anomaly_label"] = model.predict(X)
print("\nAnomaly detection results:")
print(df[["request_count", "sql_keyword_count", "anomaly_label", "anomaly_score"]])
joblib.dump(model, "ml/anomaly_detector.pkl")
print("\nAnomaly detector saved")
