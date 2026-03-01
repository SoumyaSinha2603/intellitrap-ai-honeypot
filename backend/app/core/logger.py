import json
from datetime import datetime
from pathlib import Path

LOG_PATH = Path("data/logs/events.jsonl")
LOG_PATH.parent.mkdir(parents=True, exist_ok=True)

def log_event(event: dict):
    event["timestamp"] = datetime.utcnow().isoformat()
    with open(LOG_PATH, "a") as f:
        f.write(json.dumps(event) + "\n")
