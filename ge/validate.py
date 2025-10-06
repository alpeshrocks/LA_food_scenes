import os, pandas as pd
def validate(path: str) -> int:
    df = pd.read_csv(path)
    problems = []
    req = ['name','neighborhood','cuisine','why','sentiment_label','score_buzz','score_trend','score_total']
    missing = [c for c in req if c not in df.columns]
    if missing: problems.append(f'Missing columns: {missing}')
    if df['name'].isna().any(): problems.append('Null restaurant names found')
    if (df['score_buzz'] < 0).any(): problems.append('Negative score_buzz values detected')
    if not set(df['sentiment_label'].dropna().unique()).issubset({'must-try','good','mixed'}):
        problems.append('Unexpected sentiment_label values')
    if problems:
        print('DATA QUALITY FAILED:\n- ' + '\n- '.join(problems)); return 1
    print('Data quality checks passed.'); return 0
if __name__ == '__main__':
    import sys; path = sys.argv[1] if len(sys.argv)>1 else 'data/mentions_enhanced.csv'
    raise SystemExit(validate(path))
