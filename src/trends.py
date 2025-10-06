import os, datetime as dt, pandas as pd
from .config import DATA_DIR

def snapshot():
    path = os.path.join(DATA_DIR,"mentions_enhanced.csv")
    if not os.path.exists(path): path = os.path.join(DATA_DIR,"mentions_clean.csv")
    df = pd.read_csv(path)
    today = dt.date.today()
    year, week, _ = today.isocalendar()
    out = os.path.join(DATA_DIR,"history", f"mentions_{year}W{week:02d}.csv")
    os.makedirs(os.path.join(DATA_DIR,"history"), exist_ok=True)
    df.to_csv(out, index=False)
    print(f"Snapshot -> {out}")

def movers():
    hist = os.path.join(DATA_DIR,"history")
    files = sorted([f for f in os.listdir(hist) if f.endswith(".csv")])
    if len(files) < 2:
        print("Not enough snapshots."); return
    last, prev = files[-1], files[-2]
    df_last = pd.read_csv(os.path.join(hist,last))
    df_prev = pd.read_csv(os.path.join(hist,prev))
    m = df_last[["name","score_total"]].merge(df_prev[["name","score_total"]], on="name", how="left", suffixes=("_new","_old"))
    m["delta"] = m["score_total_new"] - m["score_total_old"].fillna(0)
    m.sort_values("delta", ascending=False).head(20).to_csv(os.path.join(DATA_DIR,"movers.csv"), index=False)
    print("Wrote data/movers.csv")

if __name__ == "__main__":
    snapshot(); movers()
