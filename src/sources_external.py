import os, time, json, feedparser, requests, pandas as pd
from typing import List, Dict, Any
from .config import DATA_DIR

YELP_API_KEY = os.getenv("YELP_API_KEY")
GOOGLE_PLACES_API_KEY = os.getenv("GOOGLE_PLACES_API_KEY")
EATER_FEED_URL = os.getenv("EATER_FEED_URL", "https://la.eater.com/rss/index.xml")

def load_mentions_clean() -> pd.DataFrame:
    p = os.path.join(DATA_DIR, "mentions_clean.csv")
    if os.path.exists(p):
        return pd.read_csv(p)
    return pd.DataFrame(columns=["name","neighborhood","cuisine","why","source_url","sentiment",
                                 "first_seen","last_seen","mentions","score_buzz","score_trend","score_total"])

def eater_rss(limit: int = 50) -> pd.DataFrame:
    feed = feedparser.parse(EATER_FEED_URL)
    rows = []
    for e in feed.entries[:limit]:
        title = e.get("title","")
        link = e.get("link","")
        summary = e.get("summary","")
        # naive extraction: look for capitalized words followed by restaurant keyword
        rows.append({"name_from": title, "why": summary[:240], "source_url": link, "source":"eater_rss"})
    return pd.DataFrame(rows)

def yelp_search(term="restaurant", location="Los Angeles, CA", limit=20) -> pd.DataFrame:
    if not YELP_API_KEY:
        return pd.DataFrame(columns=["name","neighborhood","cuisine","why","source_url","source"])
    headers = {"Authorization": f"Bearer {YELP_API_KEY}"}
    url = "https://api.yelp.com/v3/businesses/search"
    params = {"term": term, "location": location, "limit": limit, "sort_by":"rating"}
    r = requests.get(url, headers=headers, params=params, timeout=20).json()
    rows = []
    for b in r.get("businesses", []):
        rows.append({
            "name": b.get("name"),
            "neighborhood": ", ".join(b.get("location",{}).get("display_address",[])),
            "cuisine": ", ".join(b.get("categories",[]) and [c["title"] for c in b["categories"]] or []),
            "why": f"Yelp rating {b.get('rating')} ({b.get('review_count')} reviews)",
            "source_url": b.get("url"),
            "source": "yelp_api"
        })
    return pd.DataFrame(rows)

def places_search(query="best restaurants in Los Angeles", limit=20) -> pd.DataFrame:
    if not GOOGLE_PLACES_API_KEY:
        return pd.DataFrame(columns=["name","neighborhood","cuisine","why","source_url","source"])
    url = f"https://maps.googleapis.com/maps/api/place/textsearch/json"
    params = {"query": query, "key": GOOGLE_PLACES_API_KEY}
    r = requests.get(url, params=params, timeout=20).json()
    rows = []
    for res in r.get("results", [])[:limit]:
        rows.append({
            "name": res.get("name"),
            "neighborhood": res.get("formatted_address"),
            "cuisine": None,
            "why": f"Google rating {res.get('rating')} ({res.get('user_ratings_total')} reviews)",
            "source_url": None,
            "source": "google_places"
        })
    return pd.DataFrame(rows)

def merge_external(limit_eater=40, limit_yelp=30, limit_places=30, output="external_merged.csv"):
    df_eater = eater_rss(limit=limit_eater)
    df_yelp = yelp_search(limit=limit_yelp)
    df_places = places_search(limit=limit_places)

    # Basic harmonization
    def _clean_cols(df):
        for c in ["name","neighborhood","cuisine","why","source_url","source"]:
            if c not in df.columns: df[c] = None
        if "name_from" in df.columns and df["name"].isna().all():
            df["name"] = df["name_from"].str.replace("Opening","", case=False)
        return df[["name","neighborhood","cuisine","why","source_url","source"]]

    out = pd.concat([_clean_cols(df_eater), _clean_cols(df_yelp), _clean_cols(df_places)], ignore_index=True)
    p = os.path.join(DATA_DIR, output)
    out.to_csv(p, index=False)
    print(f"Saved external sources -> {p} (rows={len(out)})")
    return out

if __name__ == "__main__":
    merge_external()
