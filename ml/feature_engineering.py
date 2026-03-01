import csv
import json
from collections import defaultdict
from datetime import datetime
import math

print("Feature engineering script started")

LOG_FILE = "data/logs/events.jsonl"

def load_events():
    events = []
    with open(LOG_FILE, "r") as f:
        for line in f:
            events.append(json.loads(line))
    return events
def group_by_ip(events):
    grouped = defaultdict(list)
    for event in events:
        grouped[event["ip"]].append(event)
    return grouped
def payload_entropy(payload):
    if not payload:
        return 0
    freq = defaultdict(int)
    for char in payload:
        freq[char] += 1
    entropy = 0
    for count in freq.values():
        p = count / len(payload)
        entropy -= p * math.log2(p)
    return entropy
def extract_features(events):
    features = {}

    timestamps = [
        datetime.fromisoformat(e["timestamp"])
        for e in events
    ]
    timestamps.sort()

    time_gaps = [
        (timestamps[i+1] - timestamps[i]).total_seconds()
        for i in range(len(timestamps)-1)
    ]

    avg_gap = sum(time_gaps)/len(time_gaps) if time_gaps else 0

    endpoints = set(e["endpoint"] for e in events)
    payloads = [e["payload"] for e in events if e["payload"]]

    sql_keywords = ["select", "union", "or", "--", "'"]
    sql_hits = sum(
        any(k in p.lower() for k in sql_keywords)
        for p in payloads
    )

    features["request_count"] = len(events)
    features["unique_endpoints"] = len(endpoints)
    features["avg_time_gap"] = avg_gap
    features["avg_payload_entropy"] = (
        sum(payload_entropy(p) for p in payloads) / len(payloads)
        if payloads else 0
    )
    features["sql_keyword_count"] = sql_hits

    return features
def group_by_time(events, window_seconds=15):
    events.sort(key=lambda e: e["timestamp"])
    sessions = []
    current = []

    start_time = None

    for e in events:
        t = datetime.fromisoformat(e["timestamp"])

        if start_time is None:
            start_time = t

        if (t - start_time).total_seconds() <= window_seconds:
            current.append(e)
        else:
            sessions.append(current)
            current = [e]
            start_time = t

    if current:
        sessions.append(current)

    return sessions

def generate_fingerprints():
    events = load_events()

    # convert timestamps properly
    for e in events:
        e["timestamp"] = e["timestamp"]
    sessions = group_by_time(events)
    print("Total sessions created:", len(sessions))

    fingerprints = {}

    for i, session in enumerate(sessions):
        features = extract_features(session)
        fingerprints[f"session_{i}"] = features

    return fingerprints

def save_to_csv(fingerprints, filename="ml/attacker_dataset.csv"):
    with open(filename, "w", newline="") as f:
        writer = csv.writer(f)

        writer.writerow([
            "request_count",
            "unique_endpoints",
            "avg_time_gap",
            "avg_payload_entropy",
            "sql_keyword_count",
            "label"
        ])

        for ip, features in fingerprints.items():
            # Simple rule-based labeling
            if features["sql_keyword_count"] == 0:
                label = 0  # normal
            else:
                label = 1  # malicious

            writer.writerow([
                features["request_count"],
                features["unique_endpoints"],
                features["avg_time_gap"],
                features["avg_payload_entropy"],
                features["sql_keyword_count"],
                label
            ])
if __name__ == "__main__":
    fingerprints = generate_fingerprints()

    for session_id, fp in fingerprints.items():
        print(f"\n{session_id}")
        for k, v in fp.items():
            print(f"  {k}: {round(v, 3)}")

    save_to_csv(fingerprints)
    print("\nCSV dataset updated successfully")
