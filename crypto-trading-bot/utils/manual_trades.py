# trading/manual_trades.py
import os
import json
from datetime import datetime

LOG_PATH = "logs/manual_trades.json"

def log_manual_trade(pair, direction, price, confidence):
    os.makedirs("logs", exist_ok=True)

    entry = {
        "timestamp": datetime.now().isoformat(),
        "pair": pair,
        "action": direction,
        "price": round(price, 5),
        "confidence": round(confidence, 3)
    }

    if os.path.exists(LOG_PATH):
        with open(LOG_PATH, "r") as f:
            history = json.load(f)
    else:
        history = []

    history.append(entry)

    with open(LOG_PATH, "w") as f:
        json.dump(history, f, indent=2)

    print(f"📝 Logged manual {direction.upper()} on {pair} @ {price} (conf: {confidence})")
