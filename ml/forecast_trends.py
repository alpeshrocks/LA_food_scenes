import os, pandas as pd
from src.config import DATA_DIR
def main():
    raw_path = os.path.join(DATA_DIR,'mentions_raw.jsonl')
    if not os.path.exists(raw_path): print('No raw mentions found.'); return
    df = pd.read_json(raw_path, lines=True)
    df['created_iso'] = pd.to_datetime(df['created_iso'], errors='coerce')
    ts = df.set_index('created_iso').resample('W').size().rename('mentions')
    ts_ma = ts.rolling(4, min_periods=1).mean()
    print('Last 8 weeks actual:\n', ts.tail(8))
    print('Moving average forecast (next 4w):\n', [float(ts_ma.iloc[-1])] * 4)
if __name__ == '__main__':
    main()
