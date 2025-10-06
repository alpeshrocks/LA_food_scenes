import argparse, json, time, os
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Any
from tqdm import tqdm
import praw
from .config import DATA_DIR, REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET, REDDIT_USER_AGENT

def utcnow():
    return datetime.now(timezone.utc)

def scrape(subreddits: List[str], days_back: int, max_posts: int, query: str) -> List[Dict[str, Any]]:
    reddit = praw.Reddit(
        client_id=REDDIT_CLIENT_ID,
        client_secret=REDDIT_CLIENT_SECRET,
        user_agent=REDDIT_USER_AGENT,
    )
    since = utcnow() - timedelta(days=days_back)
    results = []

    for sub in subreddits:
        sr = reddit.subreddit(sub.strip("r/"))
        # Use Reddit search for recency + keyword filtering
        for post in tqdm(sr.search(query=query, sort="new", time_filter="month"), desc=f"Searching {sub}"):
            if len(results) >= max_posts:
                break
            created = datetime.fromtimestamp(post.created_utc, tz=timezone.utc)
            if created < since:
                continue

            post.comments.replace_more(limit=0)
            comments = []
            for c in post.comments.list():
                comments.append({
                    "id": c.id,
                    "parent_id": c.parent_id,
                    "body": c.body,
                    "score": c.score,
                    "created_utc": c.created_utc,
                })

            results.append({
                "id": post.id,
                "title": post.title,
                "selftext": post.selftext,
                "permalink": "https://www.reddit.com" + post.permalink,
                "url": post.url,
                "score": post.score,
                "num_comments": post.num_comments,
                "created_utc": post.created_utc,
                "subreddit": sub,
                "comments": comments,
            })
    return results

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--subreddits", nargs="+", required=True)
    ap.add_argument("--days_back", type=int, default=60)
    ap.add_argument("--max_posts", type=int, default=200)
    ap.add_argument("--query", type=str, default="restaurant OR opening OR recommend OR eats OR best")
    args = ap.parse_args()

    data = scrape(args.subreddits, args.days_back, args.max_posts, args.query)
    out_path = os.path.join(DATA_DIR, "raw_threads.jsonl")
    with open(out_path, "w", encoding="utf-8") as f:
        for row in data:
            f.write(json.dumps(row) + "\n")
    print(f"Wrote {len(data)} threads -> {out_path}")

if __name__ == "__main__":
    main()
