import os, time, json, feedparser, requests, pandas as pd
from typing import List, Dict, Any
from .config import DATA_DIR

YELP_API_KEY = os.getenv("YELP_API_KEY")
GOOGLE_PLACES_API_KEY = os.getenv("GOOGLE_PLACES_API_KEY")
EATER_FEED_URL = os.getenv("EATER_FEED_URL", "https://la.eater.com/rss/index.xml")

def merge_external(limit_eater=40, limit_yelp=30, limit_places=30, output="external_merged.csv"):
    # Eater RSS
    feed = feedparser.parse(EATER_FEED_URL)
    eater_rows = [{"name": e.get("title",""), "neighborhood": None, "cuisine": None, "why": e.get("summary","")[:240], "source_url": e.get("link",""), "source": "eater_rss"} for e in feed.entries[:limit_eater]]
    df_eater = pd.DataFrame(eater_rows)

    # Yelp
    rows_yelp = []
    if YELP_API_KEY:
        headers = {"Authorization": f"Bearer {YELP_API_KEY}"}
        url = "https://api.yelp.com/v3/businesses/search"
        params = {"term": "restaurant", "location": "Los Angeles, CA", "limit": limit_yelp, "sort_by":"rating"}
        r = requests.get(url, headers=headers, params=params, timeout=20).json()
        for b in r.get("businesses", []):
            rows_yelp.append({
                "name": b.get("name"),
                "neighborhood": ", ".join(b.get("location",{}).get("display_address",[])),
                "cuisine": ", ".join([c["title"] for c in b.get("categories",[])]),
                "why": f"Yelp rating {b.get('rating')} ({b.get('review_count')} reviews)",
                "source_url": b.get("url"),
                "source": "yelp_api"
            })
    df_yelp = pd.DataFrame(rows_yelp or [], columns=["name","neighborhood","cuisine","why","source_url","source"])

    # Google Places
    rows_g = []
    if GOOGLE_PLACES_API_KEY:
        url = f"https://maps.googleapis.com/maps/api/place/textsearch/json"
        params = {"query": "best restaurants in Los Angeles", "key": GOOGLE_PLACES_API_KEY}
        r = requests.get(url, params=params, timeout=20).json()
        for res in r.get("results", [])[:limit_places]:
            rows_g.append({
                "name": res.get("name"),
                "neighborhood": res.get("formatted_address"),
                "cuisine": None,
                "why": f"Google rating {res.get('rating')} ({res.get('user_ratings_total')} reviews)",
                "source_url": None,
                "source": "google_places"
            })
    df_places = pd.DataFrame(rows_g or [], columns=["name","neighborhood","cuisine","why","source_url","source"])

    out = pd.concat([df_eater, df_yelp, df_places], ignore_index=True)
    p = os.path.join(DATA_DIR, output)
    out.to_csv(p, index=False)
    print(f"Saved external sources -> {p} (rows={len(out)})")
    return out

if __name__ == "__main__":
    merge_external()
