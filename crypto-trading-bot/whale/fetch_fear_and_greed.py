import requests
from datetime import datetime, timezone
import os
import json

def fetch_fear_and_greed(save_path="data/sentiment/fear_greed.jsonl"):
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    url = "https://api.alternative.me/fng/?limit=1"

    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()["data"][0]

        today_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "date": today_str,
            "index_value": int(data["value"]),
            "classification": data["value_classification"]
        }

        # Check for duplicate (same date already logged)
        if os.path.exists(save_path):
            with open(save_path, "r") as f:
                for line in f:
                    existing = json.loads(line)
                    if existing.get("date") == today_str:
                        print(f"[Skip] Fear & Greed already logged for {today_str}")
                        return entry

        # Append new entry
        with open(save_path, "a") as f:
            f.write(json.dumps(entry) + "\n")

        print(f"[Fear & Greed] {entry['index_value']} ({entry['classification']}) saved.")
        return entry

    except Exception as e:
        print(f"[Error] Failed to fetch Fear & Greed Index: {e}")
        return None


# 👇 Allows running via: python -m whale.fetch_fear_and_greed
if __name__ == "__main__":
    fetch_fear_and_greed()
