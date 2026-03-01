import pandas as pd
from app.core.threat_state import set_threat_level

def update_threat_level():
    df = pd.read_csv("ml/attacker_dataset.csv")

    # Use the highest risk session
    highest_risk = df.iloc[df["request_count"].idxmax()]

    if highest_risk["label"] == 1:
        set_threat_level("HIGH")
    else:
        set_threat_level("LOW")
