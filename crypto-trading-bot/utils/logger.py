# utils/logger.py
from datetime import datetime, timezone
import json
import os

import numpy as np
import pandas as pd

def log(msg, tag="INFO"):
    now = datetime.now(timezone.utc).strftime("%H:%M:%S")
    print(f"[{tag}] {now} | {msg}")

LOG_DIR = "data/logs"
os.makedirs(LOG_DIR, exist_ok=True)

def safe_jsonify(obj):
    if isinstance(obj, (np.integer, np.int64)):
        return int(obj)
    elif isinstance(obj, (np.floating, np.float64)):
        return float(obj)
    elif isinstance(obj, (pd.Timestamp, datetime)):
        return obj.isoformat()
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    return str(obj)

def make_json_safe(obj):
    if isinstance(obj, dict):
        return {k: make_json_safe(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [make_json_safe(v) for v in obj]
    elif isinstance(obj, (np.integer, np.int64)):
        return int(obj)
    elif isinstance(obj, (np.floating, np.float64)):
        return float(obj)
    elif isinstance(obj, (pd.Timestamp, datetime)):
        return obj.isoformat()
    return obj


def json_dump_safe(obj, file):
    safe_obj = make_json_safe(obj)
    json.dump(safe_obj, file)
    return safe_obj  # optional: return it for logging/debugging

def json_dumps_safe(obj):
    return json.dumps(make_json_safe(obj))

def to_serializable_dict(d):
    return {
        k: (
            v.item() if hasattr(v, "item")
            else v.isoformat() if isinstance(v, (pd.Timestamp, datetime))
            else v
        )
        for k, v in d.items()
    }

def log_confidence(direction, token, confidence, out_dir="logs/confidence"):
    os.makedirs(out_dir, exist_ok=True)
    log_entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "token": token,
        "direction": direction,
        "confidence": round(confidence, 2)
    }
    file_path = os.path.join(out_dir, f"{token}_signals.jsonl")
    with open(file_path, "a") as f:
        f.write(json_dumps_safe(log_entry) + "\n")