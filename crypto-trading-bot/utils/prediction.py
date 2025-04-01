from datetime import datetime, timezone
import json


def log_prediction(pair, direction, confidence, success, price=None, features=None, reason=None, exit_price=None):
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "pair": pair,
        "direction": direction,
        "confidence": confidence,
        "success": success,
        "entry_price": price,
        "exit_price": exit_price,
        "pnl": round((exit_price - price) if success else 0.0, 2) if price and exit_price else None,
        "features": features or {},
        "reason": reason
    }

    with open("logs/prediction_history.jsonl", "a") as f:
        f.write(json.dumps(entry) + "\n")