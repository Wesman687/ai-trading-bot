import os
import json
from datetime import datetime, timedelta, timezone
import numpy as np
from config import SANTIMENT_SLUGS

DAYS_BACK = 7
DECAY = 0.9

def load_sentiment_history(token, source_dir="data/reddit-sentiment"):
    scores_by_date = {}
    today = datetime.now(timezone.utc).date()

    for i in range(DAYS_BACK):
        date_str = (today - timedelta(days=i)).strftime("%Y-%m-%d")
        file_path = os.path.join(source_dir, f"{token.lower()}_{date_str}.json")

        if os.path.exists(file_path):
            with open(file_path, "r") as f:
                try:
                    data = json.load(f)
                    score = data.get("sentiment_score")
                    if score is not None:
                        scores_by_date[date_str] = score
                except Exception as e:
                    print(f"⚠️ Error reading {file_path}: {e}")

    return dict(sorted(scores_by_date.items()))


def calculate_weighted_sentiment(scores):
    weighted_total = 0
    total_weight = 0
    for i, (date, score) in enumerate(reversed(list(scores.items()))):
        weight = DECAY ** i
        weighted_total += score * weight
        total_weight += weight
    return round(weighted_total / total_weight, 3) if total_weight else 0


def determine_trend(scores):
    if len(scores) < 2:
        return "flat"
    values = list(scores.values())
    deltas = [b - a for a, b in zip(values, values[1:])]
    avg_delta = sum(deltas) / len(deltas)

    if avg_delta > 0.05:
        return "upward"
    elif avg_delta < -0.05:
        return "downward"
    return "flat"


def calculate_volatility(scores):
    values = list(scores.values())
    return round(np.std(values), 3) if len(values) >= 2 else 0.0


def append_to_master_file(token, analysis, out_dir="data/sentiment/reddit"):
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, f"{token.lower()}.json")

    history = []
    if os.path.exists(path):
        with open(path, "r") as f:
            try:
                history = json.load(f)
            except:
                history = []

    # Avoid duplicate
    if any(entry["date"] == analysis["date"] for entry in history):
        print(f"⏩ Already aggregated {token} for {analysis['date']}")
        return

    history.append(analysis)
    with open(path, "w") as f:
        json.dump(history, f, indent=2)

    print(f"✅ Appended Reddit trend to {path}")


def main():
    tokens = SANTIMENT_SLUGS.keys()
    today_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    for token in tokens:
        scores = load_sentiment_history(token)
        if not scores:
            continue

        weighted = calculate_weighted_sentiment(scores)
        volatility = calculate_volatility(scores)
        trend = determine_trend(scores)

        today_score = scores.get(today_str)
        if today_score is None:
            print(f"⚠️ Missing today’s sentiment for {token}")
            continue

        analysis = {
            "date": today_str,
            "hype_score": len(scores),
            "weighted_sentiment": weighted,
            "volatility": volatility,
            "sentiment_trend": trend,
            "raw_scores": scores
        }

        append_to_master_file(token, analysis)

if __name__ == "__main__":
    main()
