import pandas as pd
import joblib

from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report

# Load dataset
DATASET_PATH = "ml/attacker_dataset.csv"
df = pd.read_csv(DATASET_PATH)

print("Dataset loaded successfully")
print(df.head())

# Split features and labels
X = df.drop(columns=["label"])
y = df["label"]

print("\nLabel distribution:")
print(y.value_counts())

# Train-test split
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# Train classifier
clf = LogisticRegression(max_iter=1000)
clf.fit(X_train, y_train)

print("\nClassifier training completed")

# Evaluate
y_pred = clf.predict(X_test)
print("\nClassification Report:")
print(classification_report(y_test, y_pred))

# Save model
joblib.dump(clf, "ml/log_classifier.pkl")
print("\nClassifier model saved as ml/log_classifier.pkl")
