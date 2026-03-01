import json
import numpy as np
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.sequence import pad_sequences
LOG_FILE = "data/logs/events.jsonl"

def load_events():
    events = []
    with open(LOG_FILE, "r") as f:
        for line in f:
            events.append(json.loads(line))
    return events


def build_sequences(events, window_seconds=15):
    events.sort(key=lambda e: e["timestamp"])

    sessions = []
    current = []
    start_time = None

    for e in events:
        t = np.datetime64(e["timestamp"])

        if start_time is None:
            start_time = t

        if (t - start_time) <= np.timedelta64(window_seconds, 's'):
            current.append(e["endpoint"])
        else:
            sessions.append(current)
            current = [e["endpoint"]]
            start_time = t

    if current:
        sessions.append(current)

    return sessions
def build_vocab(sequences):
    vocab = {}
    reverse_vocab = {}

    idx = 1
    for seq in sequences:
        for endpoint in seq:
            if endpoint not in vocab:
                vocab[endpoint] = idx
                reverse_vocab[idx] = endpoint
                idx += 1

    return vocab, reverse_vocab
def predict_next(sequence, model, vocab, reverse_vocab, max_len):
    encoded = [vocab[e] for e in sequence if e in vocab]
    padded = pad_sequences([encoded], maxlen=max_len, padding="pre")

    probs = model.predict(padded, verbose=0)[0]
    predicted_idx = np.argmax(probs)

    return reverse_vocab.get(predicted_idx, "UNKNOWN")
if __name__ == "__main__":
    events = load_events()
    sessions = build_sequences(events)

    vocab, reverse_vocab = build_vocab(sessions)
    max_len = max(len(s) for s in sessions)

    model = load_model("ml/lstm_attack_path_model.h5")

    # Pick the most recent session
    recent_session = sessions[-1]

    print("Recent attacker behaviour:")
    for e in recent_session:
        print("  →", e)

    next_step = predict_next(
        recent_session,
        model,
        vocab,
        reverse_vocab,
        max_len
    )

    print("\nPredicted next attacker action:")
    print("  →", next_step)
