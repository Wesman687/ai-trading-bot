import os
import requests
import json
from datetime import datetime, timedelta, timezone
from config import BTCC_SYMBOLS, SANTIMENT_SLUGS
from dotenv import load_dotenv
from whale.santiment_analyzer import process_all

load_dotenv()
API_KEY = os.getenv("SANTIMENT_API")
BASE_URL = "https://api.santiment.net/graphql"

WATCHED_TOKENS = [symbol.replace("USDT", "") for symbol in BTCC_SYMBOLS]
now = datetime.now(timezone.utc)
from_date = (now - timedelta(days=1)).strftime("%Y-%m-%dT%H:%M:%SZ")
to_date = now.strftime("%Y-%m-%dT%H:%M:%SZ")

METRICS = [
    "social_dominance_total",
    "social_volume_total",
    "dev_activity",
    "daily_active_addresses",
    "exchange_balance",
    "network_growth"
]

def fetch_metric_history(slug, metric):
    query = {
        "query": """
        query GetMetric($slug: String!, $metric: String!, $from: DateTime!, $to: DateTime!) {
            getMetric(metric: $metric) {
                timeseriesData(
                    slug: $slug
                    from: $from
                    to: $to
                    interval: "1d"
                ) {
                    datetime
                    value
                }
            }
        }
        """,
        "variables": {
            "slug": slug,
            "metric": metric,
            "from": from_date,
            "to": to_date
        }
    }

    headers = {"Authorization": f"Apikey {API_KEY}"}
    response = requests.post(BASE_URL, json=query, headers=headers)

    try:
        json_response = response.json()
    except Exception as e:
        raise Exception(f"❌ Failed to parse JSON: {e}")

    if "data" not in json_response:
        print(f"❌ API Error {response.status_code}: {json_response}")
        raise Exception("'data' key missing in response")

    return json_response["data"]




def main():
    for token in WATCHED_TOKENS:
        slug = SANTIMENT_SLUGS.get(token)
        if not slug:
            print(f"⚠️ No slug mapping for {token}, skipping.")
            continue

        try:
            print(f"📡 Fetching Santiment metrics for {token} ({slug})...")

            all_data = {}
            for metric in METRICS:
                try:
                    all_data[metric] = fetch_metric_history(slug, metric)
                except Exception as metric_error:
                    print(f"⚠️ Failed to fetch {metric}: {metric_error}")

            if not any(all_data.values()):
                print(f"⚠️ No valid data returned for {token}, skipping sentiment analysis.")
                continue

            # Save raw metric data for debugging
            raw_dir = "whale/data/raw/santiment"
            os.makedirs(raw_dir, exist_ok=True)
            with open(f"{raw_dir}/{token.lower()}.json", "w") as f:
                json.dump(all_data, f, indent=2)

            print(f"🧠 Analyzing sentiment for {token}...")
            process_all()


        except Exception as e:
            print(f"❌ Failed for {token}: {e}")

if __name__ == "__main__":
    main()