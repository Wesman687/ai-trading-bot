import json
import os
from datetime import datetime, timezone


def score_metric(metric_data, metric_name):
    # Simple scoring rules
    if not metric_data or not isinstance(metric_data, list) or len(metric_data) == 0:
        return -1, f"No data for {metric_name}"

    # Dev Activity: check for drop or rise
    if metric_name == "dev_activity" and len(metric_data) >= 2:
        delta = metric_data[-1]['value'] - metric_data[-2]['value']
        if delta > 10:
            return 1, "Developer activity increased"
        elif delta < -10:
            return -1, "Developer activity dropped sharply"
        else:
            return 0, "Developer activity is stable"

    # Daily Active Addresses / Network Growth
    if metric_name in ["daily_active_addresses", "network_growth"]:
        val = metric_data[-1]['value']
        if val > 10000:
            return 1, f"Strong {metric_name.replace('_', ' ')}"
        elif val == 0:
            return -1, f"No {metric_name.replace('_', ' ')}"
        else:
            return 0, f"Moderate {metric_name.replace('_', ' ')}"

    # Social metrics
    if metric_name in ["social_dominance_total", "social_volume_total"]:
        return -1, f"No social data for {metric_name.replace('_', ' ')}"

    # Exchange balance
    if metric_name == "exchange_balance":
        return -1, "Exchange balance data missing"

    return 0, f"Neutral {metric_name.replace('_', ' ')}"


def analyze_sentiment(data):
    breakdown = {}
    explanations = []
    total_score = 0
    count = 0

    for key in data:
        metric_data = data[key].get("getMetric", {}).get("timeseriesData", [])
        score, explanation = score_metric(metric_data, key)
        breakdown[key] = score
        explanations.append(explanation)
        if score is not None:
            total_score += score
            count += 1

    sentiment_score = round(total_score / count, 2) if count else 0
    summary = ". ".join(explanations)

    return sentiment_score, breakdown, summary



def process_all():
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    raw_dir = "whale/data/raw/santiment"
    out_dir = "data/sentiment/santiment"
    os.makedirs(out_dir, exist_ok=True)

    for filename in os.listdir(raw_dir):
        if not filename.endswith(".json"):
            continue

        token = filename.replace(".json", "").upper()

        with open(os.path.join(raw_dir, filename), "r") as f:
            data = json.load(f)

        sentiment_score, breakdown, summary = analyze_sentiment(data)

        new_entry = {
            "token": token,
            "date": now,
            "sentiment_score": sentiment_score,
            "breakdown": breakdown,
            "summary": summary
        }

        out_path = os.path.join(out_dir, f"{token.lower()}.json")
        history = []

        if os.path.exists(out_path):
            try:
                with open(out_path, "r") as f:
                    history = json.load(f)
                    # Filter out any existing entry for today
                    history = [h for h in history if h.get("date") != now]
            except Exception as e:
                print(f"⚠️ Failed to load history for {token}: {e}")

        history.append(new_entry)

        with open(out_path, "w") as out_file:
            json.dump(history, out_file, indent=2)

        print(f"✅ Appended sentiment for {token} → {out_path}")

if __name__ == "__main__":
    process_all()
