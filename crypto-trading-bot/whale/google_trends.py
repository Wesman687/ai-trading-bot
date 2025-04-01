import os
import json
from datetime import datetime, timezone
from pytrends.request import TrendReq
from config import SANTIMENT_SLUGS


def fetch_google_trend(token_name, out_dir="data/sentiment/googletrends"):
    pytrends = TrendReq(hl='en-US', tz=360)
    pytrends.build_payload([token_name], cat=0, timeframe='now 7-d', geo='', gprop='')

    data = pytrends.interest_over_time()
    if data.empty:
        print(f"⚠️ No trend data for {token_name}")
        return

    trend_values = data[token_name].to_dict()
    trend_score = list(trend_values.values())[-1]  # Most recent score
    date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    output = {
        "token": token_name.upper(),
        "as_of": date_str,
        "google_trend_score": trend_score,
        "daily_trend_history": {k.strftime('%Y-%m-%d'): v for k, v in trend_values.items()}
    }

    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, f"{token_name.lower()}.json")

    existing = []
    if os.path.exists(out_path):
        try:
            with open(out_path, "r") as f:
                existing = json.load(f)
        except Exception as e:
            print(f"⚠️ Failed to load existing trend history for {token_name}: {e}")

    existing.append(output)

    with open(out_path, "w") as f:
        json.dump(existing, f, indent=2)

    print(f"✅ Saved Google Trend score for {token_name} → {trend_score}")


def main():
    print("\n📊 Fetching Google Trends for all tokens...\n")
    for token, slug in SANTIMENT_SLUGS.items():
        fetch_google_trend(slug)
    print("\n✅ Google Trends fetch complete.")


if __name__ == "__main__":
    main()
