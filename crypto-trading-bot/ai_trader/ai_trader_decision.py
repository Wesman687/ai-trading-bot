import os
import json
from datetime import datetime, timezone

LOG_DIR = "logs/ai_trader"
os.makedirs(LOG_DIR, exist_ok=True)

def ai_trader_decision(context):
    """
    Logs trade decision context for later AI analysis.
    :param context: dict containing pair, prediction, features, price, etc.
    """
    pair = context.get("pair", "unknown").replace("/", "_")
    timestamp = datetime.now(timezone.utc).isoformat()
    
    log_entry = {
        "timestamp": timestamp,
        "pair": pair,
        "price": context.get("price"),
        "prediction": context.get("prediction", {}),
        "features": context.get("features", {}),
        "source": "live-evaluation"
    }

    log_path = os.path.join(LOG_DIR, f"{pair}_context.jsonl")
    with open(log_path, "a") as f:
        f.write(json.dumps(log_entry, default=str) + "\n")
