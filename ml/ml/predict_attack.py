import joblib
import json
import numpy as np
import os

# Get path of this script
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Load model and scaler
model = joblib.load(os.path.join(BASE_DIR, "login_attack_model.pkl"))
scaler = joblib.load(os.path.join(BASE_DIR, "scaler.pkl"))

# Load threshold
with open(os.path.join(BASE_DIR, "model_config.json")) as f:
    config = json.load(f)

THRESHOLD = config["threshold"]


def predict_attack(features):

    features = list(features)

    # unpack original features
    (
        login_time,
        typing_speed,
        backspace_count,
        mouse_movement_speed,
        cursor_path_length,
        ip_address_risk,
        geo_location_change,
        device_type,
        browser_type,
        failed_attempts_last_10min,
        login_hour,
        session_request_rate,
        password_paste,
        vpn_detected,
        tor_detected,
        keystroke_variance
    ) = features


    # ---- Feature Engineering (same as training) ----
    typing_error_rate = backspace_count / (typing_speed + 1)

    mouse_efficiency = cursor_path_length / (mouse_movement_speed + 1)

    network_risk = ip_address_risk + vpn_detected + tor_detected

    behavior_score = typing_speed * keystroke_variance

    login_pressure = failed_attempts_last_10min * session_request_rate


    full_features = [
        login_time,
        typing_speed,
        backspace_count,
        mouse_movement_speed,
        cursor_path_length,
        ip_address_risk,
        geo_location_change,
        device_type,
        browser_type,
        failed_attempts_last_10min,
        login_hour,
        session_request_rate,
        password_paste,
        vpn_detected,
        tor_detected,
        keystroke_variance,
        typing_error_rate,
        mouse_efficiency,
        network_risk,
        behavior_score,
        login_pressure
    ]


    X = np.array(full_features).reshape(1, -1)

    X_scaled = scaler.transform(X)

    prob = model.predict_proba(X_scaled)[0][1]

    if prob > THRESHOLD:
        return "ATTACK", prob
    else:
        return "NORMAL", prob