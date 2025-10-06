import argparse, json, os, math, statistics, datetime as dt
from typing import List, Dict, Any
import pandas as pd
from rapidfuzz import fuzz
from .config import DATA_DIR

def time_decay_weight(ts: pd.Series, half_life_days: int = 30) -> pd.Series:
    now = pd.Timestamp.utcnow()
    ages = (now - pd.to_datetime(ts, errors="coerce")).dt.total_seconds() / (3600*24)
    lam = math.log(2) / max(half_life_days,1)
    return (2 ** (-ages * lam))

def cluster_names(names: List[str], threshold: int = 88) -> Dict[int, List[int]]:
    clusters = {}
    used = set()
    idx = list(range(len(names)))
    cluster_id = 0
    for i in idx:
        if i in used: 
            continue
        base = names[i]
        clusters[cluster_id] = [i]
        used.add(i)
        for j in idx:
            if j in used: 
                continue
            sim = fuzz.token_set_ratio(base, names[j])
            if sim >= threshold:
                clusters[cluster_id].append(j)
                used.add(j)
        cluster_id += 1
    return clusters

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--min_similarity", type=int, default=88)
    ap.add_argument("--decay_half_life_days", type=int, default=30)
    args = ap.parse_args()

    raw_path = os.path.join(DATA_DIR, "mentions_raw.jsonl")
    rows = [json.loads(l) for l in open(raw_path, "r", encoding="utf-8")] if os.path.exists(raw_path) else []

    if not rows:
        print("No mentions found. Did you run llm_pipeline?")
        return

    df = pd.DataFrame(rows)
    for col in ["name","neighborhood","cuisine","why","source_url","sentiment","created_iso"]:
        if col not in df.columns:
            df[col] = None

    df["name_norm"] = df["name"].fillna("").str.strip()
    df = df[df["name_norm"]!=""].copy()

    names = df["name_norm"].tolist()
    clusters = cluster_names(names, threshold=args.min_similarity)
    df["cluster_id"] = -1
    for cid, idxs in clusters.items():
        df.loc[df.index[idxs], "cluster_id"] = cid

    agg = df.groupby("cluster_id").agg({
        "name_norm": lambda s: s.value_counts().idxmax(),
        "neighborhood": lambda s: s.dropna().value_counts().index[0] if s.dropna().size else None,
        "cuisine": lambda s: s.dropna().value_counts().index[0] if s.dropna().size else None,
        "why": lambda s: s.dropna().iloc[0] if s.dropna().size else None,
        "source_url": lambda s: s.dropna().iloc[0] if s.dropna().size else None,
        "sentiment": lambda s: s.dropna().value_counts().idxmax() if s.dropna().size else "positive",
        "created_iso": ["min","max","count"]
    })
    agg.columns = ["name","neighborhood","cuisine","why","source_url","sentiment","first_seen","last_seen","mentions"]
    agg = agg.reset_index(drop=True)

    agg["score_buzz"] = agg["mentions"]
    agg["score_trend"] = time_decay_weight(agg["last_seen"], half_life_days=args.decay_half_life_days)
    agg["score_total"] = agg["score_buzz"] * (1 + agg["score_trend"])

    out_csv = os.path.join(DATA_DIR, "mentions_clean.csv")
    agg.to_csv(out_csv, index=False)
    print(f"Wrote cleaned dataset -> {out_csv} (rows={len(agg)})")

if __name__ == "__main__":
    main()
