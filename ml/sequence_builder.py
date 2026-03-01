# ==========================================================
# Day 5 – Part 1
# Robust Session → Sequence Dataset Builder
# ==========================================================

import json
import os
import numpy as np
from collections import defaultdict
from datetime import datetime

# ======================
# CONFIGURATION
# ======================
LOG_FILE = os.path.join("data", "logs", "events.jsonl")
SEQUENCE_LEN = 10
FEATURE_DIM = 3   # endpoint_id, payload_len, payload_entropy

# ======================
# GLOBAL STATE
# ======================
endpoint_map = {}
endpoint_counter = 0


def encode_endpoint(path: str) -> int:
    """
    Encode endpoint path into a unique integer ID.
    """
    global endpoint_counter
    if path not in endpoint_map:
        endpoint_map[path] = endpoint_counter
        endpoint_counter += 1
    return endpoint_map[path]


def load_sequences():
    """
    Build fixed-length sequences from events.jsonl.

    Returns:
        X : np.ndarray of shape (N, SEQUENCE_LEN, FEATURE_DIM)
        y : np.ndarray of shape (N,)
    """

    # ---------- File existence check ----------
    if not os.path.exists(LOG_FILE):
        raise FileNotFoundError(f"Log file not found: {LOG_FILE}")

    sessions = defaultdict(list)

    # ---------- Load events ----------
    with open(LOG_FILE, "r") as f:
        for line_num, line in enumerate(f, start=1):
            try:
                event = json.loads(line)
            except json.JSONDecodeError:
                print(f"[WARN] Invalid JSON at line {line_num}")
                continue

            # Required fields
            session_id = event.get("session_id")
            timestamp = event.get("timestamp")

            if session_id is None or timestamp is None:
                print(f"[WARN] Missing session_id/timestamp at line {line_num}")
                continue

            try:
                ts = datetime.fromisoformat(timestamp)
            except ValueError:
                print(f"[WARN] Invalid timestamp format at line {line_num}")
                continue

            # -------- Robust endpoint extraction --------
            path = (
                event.get("path")
                or event.get("endpoint")
                or event.get("url")
                or "UNKNOWN"
            )

            payload = event.get("payload", "")
            entropy = float(event.get("payload_entropy", 0.0))
            label = int(event.get("label", 0))

            sessions[session_id].append(
                (ts, path, payload, entropy, label)
            )

    print(f"[INFO] Total sessions found: {len(sessions)}")

    X = []
    y = []

    # ---------- Build sequences ----------
    for session_id, events in sessions.items():
        # Sort events chronologically
        events.sort(key=lambda x: x[0])

        sequence = []

        for (_, path, payload, entropy, _) in events:
            endpoint_id = encode_endpoint(path)
            payload_len = len(payload)

            sequence.append([
                endpoint_id,
                payload_len,
                entropy
            ])

        # Keep only sessions with enough events
        if len(sequence) >= SEQUENCE_LEN:
            X.append(sequence[:SEQUENCE_LEN])

            # Session-level label = label of last event
            last_label = events[-1][4]
            y.append(last_label)

    # ---------- Final validation ----------
    if len(X) == 0:
        raise RuntimeError(
            "No valid sequences created.\n"
            "Possible reasons:\n"
            "- SEQUENCE_LEN too large\n"
            "- Too few events per session\n"
            "- Log file mismatch"
        )

    X = np.array(X, dtype=np.float32)
    y = np.array(y, dtype=np.int32)

    print("[INFO] Sequence tensor shape:", X.shape)
    print("[INFO] Label vector shape:", y.shape)
    print("[INFO] Unique endpoints encoded:", len(endpoint_map))

    return X, y


# ======================
# DEBUG ENTRY POINT
# ======================
if __name__ == "__main__":
    X, y = load_sequences()

    print("\n[DEBUG] First sequence:")
    print(X[0])

    print("\n[DEBUG] First label:")
    print(y[0])
