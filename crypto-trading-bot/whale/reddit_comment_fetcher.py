import praw
import os
import json
from datetime import datetime, timezone
from dotenv import load_dotenv
from config import SANTIMENT_SLUGS
from .reddit_comment_analyzer import analyze_reddit_comment

load_dotenv()

reddit = praw.Reddit(
    client_id=os.getenv("REDDIT_CLIENT_ID"),
    client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
    user_agent="crypto-sentiment-crawler",
    username=os.getenv("REDDIT_USERNAME"),
    password=os.getenv("REDDIT_PASSWORD")
)

def get_dynamic_subreddits():
    default_subs = ["CryptoCurrency", "CryptoMarkets", "CryptoMoonShots", "ethtrader", "altcoin"]
    token_subs = list({SANTIMENT_SLUGS[t].capitalize() for t in SANTIMENT_SLUGS})
    return list(set(default_subs + token_subs))

def fetch_reddit_comments(limit_per_mode=15, save_path="data/sentiment/reddit_posts.jsonl"):
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    entries = []

    modes = ["hot", "new", "top"]
    subreddits = get_dynamic_subreddits()

    for sub_name in subreddits:
        subreddit = reddit.subreddit(sub_name)
        print(f"📥 Fetching from r/{sub_name}...")

        for mode in modes:
            try:
                posts = getattr(subreddit, mode)(limit=limit_per_mode)
                for post in posts:
                    if post.stickied:
                        continue

                    post.comments.replace_more(limit=0)
                    top_comments = []
                    for comment in post.comments[:10]:
                        top_comments.append({
                            "id": comment.id,
                            "body": comment.body,
                            "score": comment.score,
                            "author": str(comment.author),
                            "created_utc": comment.created_utc
                        })

                    entry = {
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                        "subreddit": sub_name,
                        "mode": mode,
                        "title": post.title,
                        "score": post.score,
                        "num_comments": post.num_comments,
                        "id": post.id,
                        "selftext": post.selftext or "",
                        "url": post.url,
                        "comments": top_comments
                    }
                    entries.append(entry)

            except Exception as e:
                print(f"⚠️ Failed to fetch from r/{sub_name} ({mode}): {e}")

    # Append to master log
    with open(save_path, "a") as f:
        for entry in entries:
            f.write(json.dumps(entry) + "\n")

    print(f"\n🧠 Saved {len(entries)} Reddit posts to {save_path}")

    # Save full daily batch
    date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    daily_path = f"whale/data/raw/reddit-comments/fetch/reddit_comments_{date_str}.json"
    os.makedirs(os.path.dirname(daily_path), exist_ok=True)
    with open(daily_path, "w") as f:
        json.dump(entries, f, indent=2)

    print(f"🗂️ Saved full batch to {daily_path}")
    analyze_reddit_comment()
    return entries

if __name__ == "__main__":
    fetch_reddit_comments()
