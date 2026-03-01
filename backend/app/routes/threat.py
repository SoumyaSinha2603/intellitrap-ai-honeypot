from fastapi import APIRouter
import pandas as pd

router = APIRouter(prefix="/api/threat")

@router.get("/status")
def get_current_threat():
    df = pd.read_csv("ml/attacker_dataset.csv")

    # Use latest session
    latest = df.iloc[-1]

    return {
        "request_count": int(latest["request_count"]),
        "sql_keyword_count": int(latest["sql_keyword_count"]),
        "risk_level": "HIGH" if latest["label"] == 1 else "LOW",
        "message": "Threat assessment generated"
    }
