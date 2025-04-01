import os
import json
import requests
from datetime import datetime, timezone
from dotenv import load_dotenv
from collections import defaultdict
from config import SANTIMENT_SLUGS
from .news_analyzer import aggregate_news_sentiment, analyze_article_with_gpt, save_news_sentiment

load_dotenv()
API_KEY = os.getenv("CRYPTOPANIC_API")
BASE_URL = "https://cryptopanic.com/api/v1/posts/"

slug_to_token = {v.lower(): k for k, v in SANTIMENT_SLUGS.items()}
WATCHED_TOKENS = set(SANTIMENT_SLUGS.keys())

def article_mentions_token(article, slug, token_code):
    if "currencies" not in article:
        return False

    for currency in article["currencies"]:
        code = currency.get("code", "").upper()
        article_slug = currency.get("slug", "").lower()
        if code == token_code.upper():
            return True
        if article_slug == slug.lower():
            return True
        if article_slug in slug_to_token and slug_to_token[article_slug] == token_code:
            return True
    return False

def fetch_news(slug):
    params = {
        "auth_token": API_KEY,
        "currencies": slug,
        "kind": "news"
    }
    response = requests.get(BASE_URL, params=params)
    if response.status_code != 200:
        raise Exception(f"❌ CryptoPanic API error {response.status_code}: {response.text}")
    return response.json().get("results", [])

def append_to_history_json(token, entry, history_dir="data/cryptopanic-news/history"):
    os.makedirs(history_dir, exist_ok=True)
    path = os.path.join(history_dir, f"{token.lower()}_history.json")
    history = []
    if os.path.exists(path):
        with open(path, "r") as f:
            try:
                history = json.load(f)
            except Exception:
                history = []
    history.append(entry)
    with open(path, "w") as f:
        json.dump(history, f, indent=2)

def main():
    date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    token_to_articles = defaultdict(list)
    processed_ids = set()
    raw_dir = "whale/data/raw/cryptopanic-news"

    print(f"\n📰 Fetching news using all watched slugs: {', '.join(SANTIMENT_SLUGS.values())}")

    all_articles = []

    for token_code in WATCHED_TOKENS:
        slug = SANTIMENT_SLUGS[token_code]
        print(f"🔍 Fetching for token: {token_code} (slug: {slug})")
        try:
            articles = fetch_news(slug)
            print(f"📊 Articles returned: {len(articles)}")
            all_articles.extend(articles)
        except Exception as e:
            print(f"⚠️ Error fetching articles for {slug}: {e}")

    combined_fetch_path = os.path.join(raw_dir, f"fetch/_combined_{date_str}.json")
    os.makedirs(os.path.dirname(combined_fetch_path), exist_ok=True)
    with open(combined_fetch_path, "w") as f:
        json.dump(all_articles, f, indent=2)

    print(f"\n🧠 Classifying articles into tokens...")
    for article in all_articles:
        article_id = article.get("id")
        if not article_id or article_id in processed_ids:
            continue
        processed_ids.add(article_id)

        for token_code in WATCHED_TOKENS:
            slug = SANTIMENT_SLUGS[token_code]
            if article_mentions_token(article, slug, token_code):
                token_to_articles[token_code].append(article)

    for token, articles in token_to_articles.items():
        print(f"\n🧠 Analyzing {len(articles)} articles for {token}...")
        breakdown = []
        score_total = 0
        valid_scores = 0

        debug_dir = "debug/cryptopanic/fetched_articles"
        os.makedirs(debug_dir, exist_ok=True)
        with open(f"{debug_dir}/{token.lower()}_{date_str}.json", "w") as f:
            json.dump(articles, f, indent=2)

        existing_analysis_path = os.path.join("data/cryptopanic-news", f"{token.lower()}_{date_str}.json")
        already_done_urls = set()

        if os.path.exists(existing_analysis_path):
            try:
                with open(existing_analysis_path, "r") as f:
                    existing_data = json.load(f)
                    for entry in existing_data.get("breakdown", []):
                        if "url" in entry:
                            already_done_urls.add(entry["url"])
            except Exception as e:
                print(f"⚠️ Failed to load existing analysis for {token}: {e}")

        articles = [a for a in articles if a.get("url") not in already_done_urls]

        for article in articles:
            try:
                analysis = analyze_article_with_gpt(article)
                print(f"✅ Analyzed: {article['title'][:60]}...")

                breakdown.append({
                    "title": article["title"],
                    "url": article["url"],
                    "analysis": analysis
                })

                score_line = next((l for l in analysis.splitlines() if "score" in l.lower()), "")
                score = float(score_line.split(":")[-1].strip())
                score_total += score
                valid_scores += 1

            except Exception as e:
                print(f"⚠️ Failed to analyze article: {e}")

        avg_score = round(score_total / valid_scores, 3) if valid_scores else 0.0
        summary = {
            "score": avg_score,
            "summary": f"Avg score from {valid_scores} of {len(articles)} article(s)."
        }

        print(f"📄 {len(articles)} articles classified for {token}")
        save_news_sentiment(token, date_str, summary, breakdown, articles, "whale/data/raw/cryptopanic-news", "data/cryptopanic-news")

        # ✨ Append to long-term history file
        append_to_history_json(token, {
            "token": token,
            "as_of": date_str,
            "hype_score": len(articles),
            "sentiment_score": avg_score,
            "summary": summary["summary"]
        })

    aggregate_news_sentiment("data/cryptopanic-news", "data/sentiment/cryptopanic")

if __name__ == "__main__":
    main()
