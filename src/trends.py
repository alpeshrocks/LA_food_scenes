import os, datetime as dt, pandas as pd
from .config import DATA_DIR

def snapshot():
    df = pd.read_csv(os.path.join(DATA_DIR,"mentions_enhanced.csv")) if os.path.exists(os.path.join(DATA_DIR,"mentions_enhanced.csv")) else pd.read_csv(os.path.join(DATA_DIR,"mentions_clean.csv"))
    today = dt.date.today()
    year, week, _ = today.isocalendar()
    path = os.path.join(DATA_DIR, "history", f"mentions_{year}W{week:02d}.csv")
    df.to_csv(path, index=False)
    print(f"Snapshot saved -> {path}")

def movers():
    hist_dir = os.path.join(DATA_DIR,"history")
    files = sorted([f for f in os.listdir(hist_dir) if f.endswith(".csv")])
    if len(files) < 2:
        print("Not enough snapshots for movers.")
        return None
    last, prev = files[-1], files[-2]
    df_last = pd.read_csv(os.path.join(hist_dir,last))
    df_prev = pd.read_csv(os.path.join(hist_dir,prev))
    m = df_last[["name","score_total"]].merge(df_prev[["name","score_total"]], on="name", how="left", suffixes=("_new","_old"))
    m["delta"] = m["score_total_new"] - m["score_total_old"].fillna(0)
    movers = m.sort_values("delta", ascending=False).head(20)
    out = os.path.join(DATA_DIR,"movers.csv")
    movers.to_csv(out, index=False)
    print(f"Top movers -> {out}")
    return out

if __name__ == "__main__":
    snapshot(); movers()
