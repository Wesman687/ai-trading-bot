import praw
import os
import json
from datetime import datetime, timezone
from collections import defaultdict
from dotenv import load_dotenv
from openai import OpenAI
from config import SANTIMENT_SLUGS
from .reddit_analyzer import analyze_reddit_sentiment

load_dotenv()

reddit = praw.Reddit(
    client_id=os.getenv("REDDIT_CLIENT_ID"),
    client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
    user_agent="crypto-sentiment-crawler",
    username=os.getenv("REDDIT_USERNAME"),
    password=os.getenv("REDDIT_PASSWORD")
)

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

TOKENS = set(SANTIMENT_SLUGS.keys())

def fetch_reddit_posts(subreddits=["CryptoCurrency"], limit=25, save_path="data/sentiment/reddit_posts.jsonl"):
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    entries = []

    for sub in subreddits:
        subreddit = reddit.subreddit(sub)
        for post in subreddit.hot(limit=limit):
            if post.stickied:
                continue
            entry = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "subreddit": sub,
                "title": post.title,
                "score": post.score,
                "num_comments": post.num_comments,
                "id": post.id,
                "selftext": post.selftext or "",
                "url": post.url
            }
            entries.append(entry)

    with open(save_path, "a") as f:
        for entry in entries:
            f.write(json.dumps(entry) + "\n")

    print(f"🧠 Saved {len(entries)} Reddit posts to {save_path}")

    # Save daily batch
    date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    daily_path = f"whale/data/raw/reddit-posts/fetch/reddit_posts_{date_str}.json"
    os.makedirs(os.path.dirname(daily_path), exist_ok=True)
    with open(daily_path, "w") as f:
        json.dump(entries, f, indent=2)

    print(f"🗂️ Saved full batch to {daily_path}")
    return entries




# ✅ Run with: python -m whale.reddit_crawler
if __name__ == "__main__":
    posts = fetch_reddit_posts()
    analyze_reddit_sentiment(posts)
