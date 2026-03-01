from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Masking
from tensorflow.keras.optimizers import Adam

def build_model(input_shape):
    """
    input_shape = (SEQUENCE_LEN, FEATURE_DIM)
    """

    model = Sequential()

    # Masking for future padding support
    model.add(Masking(mask_value=0.0, input_shape=input_shape))

    # LSTM layer for temporal behavior learning
    model.add(LSTM(
        units=64,
        return_sequences=False
    ))

    # Dense layers for decision making
    model.add(Dense(32, activation="relu"))
    model.add(Dense(1, activation="sigmoid"))

    # Compile model
    model.compile(
        optimizer=Adam(learning_rate=0.001),
        loss="binary_crossentropy",
        metrics=["accuracy"]
    )

    return model
