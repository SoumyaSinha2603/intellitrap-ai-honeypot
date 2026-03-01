import json
import numpy as np
from collections import defaultdict
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Embedding
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.utils import to_categorical
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
def encode_sequences(sequences):
    vocab = {}
    encoded = []

    for seq in sequences:
        enc = []
        for endpoint in seq:
            if endpoint not in vocab:
                vocab[endpoint] = len(vocab) + 1
            enc.append(vocab[endpoint])
        encoded.append(enc)

    return encoded, vocab
def prepare_xy(sequences):
    X, y = [], []

    for seq in sequences:
        for i in range(1, len(seq)):
            X.append(seq[:i])
            y.append(seq[i])

    X = pad_sequences(X, padding="pre")
    y = to_categorical(y)

    return X, y
def train_lstm(X, y, vocab_size):
    model = Sequential()
    model.add(Embedding(input_dim=vocab_size + 1, output_dim=8))
    model.add(LSTM(32))
    model.add(Dense(vocab_size + 1, activation="softmax"))

    model.compile(
        loss="categorical_crossentropy",
        optimizer="adam",
        metrics=["accuracy"]
    )

    model.fit(X, y, epochs=20, verbose=1)
    return model
if __name__ == "__main__":
    events = load_events()
    sessions = build_sequences(events)

    encoded, vocab = encode_sequences(sessions)
    X, y = prepare_xy(encoded)

    print("Total sessions:", len(sessions))
    print("Vocabulary:", vocab)

    model = train_lstm(X, y, len(vocab))
    model.save("ml/lstm_attack_path_model.h5")

    print("LSTM model trained and saved")
