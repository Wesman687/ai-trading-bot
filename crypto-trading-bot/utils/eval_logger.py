# utils/eval_logger.py
import json
from datetime import datetime

LOG_PATH = "logs/prediction_history.json"

def log_prediction(pair, direction, confidence, success=None):
    entry = {
        "timestamp": datetime.now().isoformat(),
        "pair": pair,
        "direction": direction,
        "confidence": round(confidence, 4),
        "success": success  # None = unknown (live), True/False = later update
    }
    try:
        with open(LOG_PATH, "r") as f:
            history = json.load(f)
    except FileNotFoundError:
        history = []

    history.append(entry)
    with open(LOG_PATH, "w") as f:
        json.dump(history[-500:], f, indent=2)  # Keep last 500

    return entry
