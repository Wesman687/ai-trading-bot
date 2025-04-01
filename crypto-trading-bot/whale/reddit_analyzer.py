import os
import json
from datetime import datetime, timezone
from collections import defaultdict
from dotenv import load_dotenv
from config import SANTIMENT_SLUGS
from openai import OpenAI
from .reddit_comment_fetcher import fetch_reddit_comments

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

RAW_REDDIT_LOG = "data/sentiment/reddit_posts.jsonl"
RAW_OUTPUT_DIR = "whale/data/raw/reddit-posts"
OUT_DIR = "data/reddit-sentiment"
TOKENS = set(SANTIMENT_SLUGS.keys())

def post_mentions_token(post, token):
    text = (post.get("title", "") + " " + post.get("selftext", "")).lower()
    return token.lower() in text or SANTIMENT_SLUGS[token].lower() in text

def analyze_post_with_gpt(post):
    content = f"{post['title']}\n{post.get('selftext', '')}"
    prompt = (
        f"Analyze the following Reddit post and give:\n"
        f"1. A sentiment score between -1 (very negative) to 1 (very positive)\n"
        f"2. A 1-2 sentence explanation.\n\n"
        f"Post:\n{content}"
    )

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content

def analyze_reddit_sentiment(posts=None):
    date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    today = datetime.now(timezone.utc).date()
    token_to_posts = defaultdict(list)
    processed_ids = set()

    if not os.path.exists(RAW_REDDIT_LOG):
        print("❌ No Reddit log found.")
        return

    # Step 1: Group posts by token
    
    with open(RAW_REDDIT_LOG, "r") as f:
        for line in f:
            post = json.loads(line)
            if posts is None:
                if not os.path.exists(RAW_REDDIT_LOG):
                    print("❌ No Reddit log found.")
                    return
                with open(RAW_REDDIT_LOG, "r") as f:
                    posts = [json.loads(line) for line in f]
            post_time = datetime.fromisoformat(post["timestamp"]).date()
            if post_time != today:
                continue  # ⏭️ Skip non-today posts

            post_id = post.get("id")
            if not post_id or post_id in processed_ids:
                continue
            processed_ids.add(post_id)

            for token in TOKENS:
                if post_mentions_token(post, token):
                    token_to_posts[token].append(post)
    # Step 2: Analyze per token
    os.makedirs(OUT_DIR, exist_ok=True)
    os.makedirs(RAW_OUTPUT_DIR, exist_ok=True)

    for token, posts in token_to_posts.items():
        print(f"\n🧠 Analyzing {len(posts)} Reddit posts for {token}...")

        breakdown = []
        score_total = 0
        valid_scores = 0

        raw_dump_path = os.path.join(RAW_OUTPUT_DIR, f"{token.lower()}_{date_str}.json")
        with open(raw_dump_path, "w") as f:
            json.dump(posts, f, indent=2)

        out_path = os.path.join(OUT_DIR, f"{token.lower()}_{date_str}.json")
        if os.path.exists(out_path):
            print(f"⏩ Already analyzed: {token} ({date_str})")
            continue

        for post in posts:
            try:
                analysis = analyze_post_with_gpt(post)
                print(f"✅ {post['title'][:60]}...")

                breakdown.append({
                    "title": post["title"],
                    "id": post["id"],
                    "analysis": analysis
                })

                score_line = next((l for l in analysis.splitlines() if "score" in l.lower()), "")
                score = float(score_line.split(":")[-1].strip())
                score_total += score
                valid_scores += 1

            except Exception as e:
                print(f"⚠️ Failed to analyze post: {e}")

        avg_score = round(score_total / valid_scores, 3) if valid_scores else 0.0
        summary = {
            "score": avg_score,
            "summary": f"Avg score from {valid_scores} of {len(posts)} Reddit post(s)."
        }

        with open(out_path, "w") as f:
            json.dump({
                "token": token,
                "date": date_str,
                "sentiment_score": summary["score"],
                "hype_score": len(posts),
                "summary": summary["summary"],
                "breakdown": breakdown
            }, f, indent=2)

        print(f"📄 Saved Reddit sentiment for {token} to {out_path}")
        from . import reddit_aggregator
        reddit_aggregator.main()
        fetch_reddit_comments()
        

if __name__ == "__main__":
    analyze_reddit_sentiment()
