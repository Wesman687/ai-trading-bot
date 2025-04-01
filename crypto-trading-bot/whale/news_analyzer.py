import os
import json
from datetime import datetime, timedelta, timezone

import numpy as np
from config import SANTIMENT_SLUGS

DAYS_BACK = 7
DECAY_FACTOR = 0.9

def calculate_volatility(scores):
    values = list(scores.values())
    if len(values) < 2:
        return 0.0
    return round(np.std(values), 3)

def load_sentiment_history(token, sentiment_dir="data/sentiment-news", days_back=7):
    scores_by_date = {}
    today = datetime.now(timezone.utc).date()

    for i in range(DAYS_BACK):
        date_str = (today - timedelta(days=i)).strftime("%Y-%m-%d")
        file_path = os.path.join(sentiment_dir, f"{token.lower()}_{date_str}.json")

        if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
            try:
                with open(file_path, "r") as f:
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
        weight = DECAY_FACTOR ** i
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

def analyze_article_with_gpt(article):
    from openai import OpenAI
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    content = f"{article['title']}\n{article.get('description', '')}"
    prompt = (
        f"Analyze the following news article and give:\n"
        f"1. A sentiment score between -1 (very negative) to 1 (very positive)\n"
        f"2. A 1-2 sentence explanation.\n\n"
        f"Article:\n{content}"
    )

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content

def save_news_sentiment(token, date_str, summary, breakdown, raw_articles,  raw_dir, out_dir):
    if not raw_articles:
        print(f"⚠️ No analyzed articles for {token} — skipping save.")
        return
    os.makedirs(out_dir, exist_ok=True)
    os.makedirs(raw_dir, exist_ok=True)

    with open(f"{out_dir}/{token.lower()}_{date_str}.json", "w") as f:
        json.dump({
            "token": token,
            "date": date_str,
            "sentiment_score": summary["score"],
            "summary": summary["summary"],
            "breakdown": breakdown
        }, f, indent=2)

    
    with open(f"{raw_dir}/{token.lower()}_{date_str}.json", "w") as f:
        json.dump(raw_articles, f, indent=2)

    print(f"📥 Saved news sentiment to data/sentiment-news/{token.lower()}_{date_str}.json")


def aggregate_news_sentiment(raw_dir="whale/data/raw/sentiment-news", out_dir="data/sentiment/"):
    os.makedirs(out_dir, exist_ok=True)
    tokens = SANTIMENT_SLUGS.keys()

    for token in sorted(tokens):
        scores = load_sentiment_history(token, raw_dir)
        hype_score = len(scores)
        weighted_sentiment = calculate_weighted_sentiment(scores)
        sentiment_trend = determine_trend(scores)

        output = {
            "token": token,
            "date": datetime.now(timezone.utc).date().strftime("%Y-%m-%d"),
            "hype_score": hype_score,
            "weighted_sentiment": weighted_sentiment,
            "volatility": calculate_volatility(scores),
            "sentiment_trend": sentiment_trend,
            "past_scores": scores
        }

        out_path = os.path.join(out_dir, f"{token.lower()}.json")
        with open(out_path, "w") as f:
            json.dump(output, f, indent=2)

        print(f"✅ Aggregated sentiment saved to {out_path}")
