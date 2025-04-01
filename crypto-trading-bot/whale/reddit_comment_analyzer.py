import os
import json
from datetime import datetime, timezone
from collections import defaultdict
from dotenv import load_dotenv
from openai import OpenAI
from config import SANTIMENT_SLUGS
import ollama

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

RAW_COMMENTS_PATH = "whale/data/raw/reddit-comments/fetch"
FINAL_COMMENT_SENTIMENT_PATH = "data/sentiment/reddit-comment"
TOKENS = set(SANTIMENT_SLUGS.keys())

def comment_mentions_token(comment, token):
    text = comment.get("body", "").lower()
    return token.lower() in text or SANTIMENT_SLUGS[token].lower() in text

import re

def extract_score_from_analysis(analysis):
    matches = re.findall(r"[-+]?[0-1](?:\\.\\d+)?", analysis)
    for match in matches:
        try:
            score = float(match)
            if -1 <= score <= 1:
                return score
        except:
            continue
    return None

def analyze_comment_with_ollama(comment_text):
    prompt = (
        f"Analyze the sentiment of this Reddit comment.\n"
        f"Return a score between -1 (very negative) to 1 (very positive) and a brief summary.\n\n"
        f"Comment:\n{comment_text}"
    )
    try:
        response = ollama.chat(
            model="DeepSeek-R1:latest",
            messages=[{"role": "user", "content": prompt}]
        )
        content = response['message']['content']
        return content.replace("<think>", "").replace("</think>", "").strip()
    except Exception as e:
        print(f"⚠️ Ollama (Mistral) request failed: {e}")
        return None

def analyze_reddit_comment():
    date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    combined_path = os.path.join(RAW_COMMENTS_PATH, f"reddit_comments_{date_str}.json")
    if not os.path.exists(combined_path):
        print(f"❌ No Reddit comment dump found for {date_str}.")
        return


    with open(combined_path, "r") as f:
        posts = json.load(f)

    token_to_comments = defaultdict(list)
    for post in posts:
        for comment in post.get("comments", []):
            for token in TOKENS:
                if comment_mentions_token(comment, token):
                    token_to_comments[token].append(comment)

    os.makedirs(FINAL_COMMENT_SENTIMENT_PATH, exist_ok=True)
    os.makedirs(RAW_COMMENTS_PATH, exist_ok=True)

    for token, comments in token_to_comments.items():
        print(f"\n🧠 Analyzing {len(comments)} comments for {token}...")
        results = []
        score_total = 0
        valid_scores = 0

        raw_token_path = os.path.join(RAW_COMMENTS_PATH, f"{token.lower()}_{date_str}.json")
        with open(raw_token_path, "w") as f:
            json.dump(comments, f, indent=2)

        for comment in comments:
            try:
                analysis = analyze_comment_with_ollama(comment["body"])
                print(f"✅ Comment: {comment['body'][:60]}...")

                results.append({
                    "id": comment["id"],
                    "analysis": analysis,
                    "original": comment
                })

                score = extract_score_from_analysis(analysis)
                if score is not None:
                    score_total += score
                    valid_scores += 1
                else:
                    print(f"⚠️ Could not parse score from:\n{analysis}")

            except Exception as e:
                print(f"⚠️ Failed to analyze comment: {e}")

        avg_score = round(score_total / valid_scores, 3) if valid_scores else 0.0
        summary = {
            "token": token,
            "date": date_str,
            "sentiment_score": avg_score,
            "summary": f"Avg score from {valid_scores} of {len(comments)} comment(s).",
            "breakdown": results
        }

        final_path = os.path.join(FINAL_COMMENT_SENTIMENT_PATH, f"{token.lower()}.json")
        history = []
        if os.path.exists(final_path):
            with open(final_path, "r") as f:
                try:
                    history = json.load(f)
                    history = [h for h in history if h.get("date") != date_str]
                except:
                    pass

        history.append(summary)
        with open(final_path, "w") as f:
            json.dump(history, f, indent=2)

        print(f"📄 Saved comment sentiment to {final_path}")

if __name__ == "__main__":
    analyze_reddit_comment()
