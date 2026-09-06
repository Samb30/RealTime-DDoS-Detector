import os
import numpy as np
import joblib
from tensorflow.keras.models import load_model

# Load all artifacts once, at import time — not per-request, for performance
MODELS_DIR = os.path.join(os.path.dirname(__file__), "training", "models")

autoencoder = load_model(os.path.join(MODELS_DIR, "autoencoder_model.keras"))
classifier = load_model(os.path.join(MODELS_DIR, "classifier_model.keras"))
scaler = joblib.load(os.path.join(MODELS_DIR, "scaler.joblib"))
label_encoder = joblib.load(os.path.join(MODELS_DIR, "label_encoder.joblib"))
feature_cols = joblib.load(os.path.join(MODELS_DIR, "feature_cols.joblib"))
anomaly_threshold = joblib.load(os.path.join(MODELS_DIR, "anomaly_threshold.joblib"))

print(f"Loaded models. Anomaly threshold: {anomaly_threshold:.6f}")


def predict_traffic(traffic_data):
    """
    Takes a raw traffic record (dict from Kafka), runs it through the
    real LSTM Autoencoder + DNN classifier pipeline, and returns a prediction.
    """
    # 1. Extract exactly the 77 feature columns, in the exact trained order
    try:
        feature_values = np.array([[traffic_data[col] for col in feature_cols]], dtype=float)
    except KeyError as e:
        print(f"Missing expected feature column: {e}")
        return {
            "source_ip": traffic_data.get("source_ip"),
            "destination_ip": traffic_data.get("destination_ip"),
            "anomaly_score": None,
            "is_threat": False,
            "predicted_attack_type": "Error"
        }

    # 2. Scale using the SAME scaler fitted during training (transform only, never fit)
    scaled_values = scaler.transform(feature_values)

    # 3. Reshape for LSTM input: (1 sample, 1 timestep, 77 features)
    lstm_input = scaled_values.reshape((1, 1, scaled_values.shape[1]))

    # 4. Run through autoencoder, compute reconstruction error
    reconstruction = autoencoder.predict(lstm_input, verbose=0)
    reconstruction_error = float(np.mean(np.square(lstm_input - reconstruction)))

    # 5. Compare against the honestly-derived threshold (0.000715, from validation set)
    is_threat = reconstruction_error > anomaly_threshold

    # 6. If flagged as a threat, classify WHICH attack type
    if is_threat:
        class_probs = classifier.predict(scaled_values, verbose=0)
        predicted_class_idx = int(np.argmax(class_probs, axis=1)[0])
        predicted_attack_type = label_encoder.classes_[predicted_class_idx]
    else:
        predicted_attack_type = "Normal"

    return {
        "source_ip": traffic_data.get("source_ip"),
        "destination_ip": traffic_data.get("destination_ip"),
        "anomaly_score": round(reconstruction_error, 6),
        "is_threat": bool(is_threat),
        "predicted_attack_type": predicted_attack_type,
        "true_label": traffic_data.get("label")  # for your own verification during demo, not a real-world field
    }