import os, pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
from sklearn.ensemble import RandomForestClassifier
from src.config import DATA_DIR
def main():
    p = os.path.join(DATA_DIR,'mentions_enhanced.csv')
    df = pd.read_csv(p)
    thresh = df['score_total'].quantile(0.75)
    y = (df['score_total'] >= thresh).astype(int)
    X = pd.DataFrame({
        'buzz': df['score_buzz'].fillna(0),
        'trend': df['score_trend'].fillna(0),
        'mentions': df.get('mentions', pd.Series([1]*len(df))).fillna(1),
        'must_try': (df.get('sentiment_label','good') == 'must-try').astype(int)
    })
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=42)
    clf = RandomForestClassifier(n_estimators=200, random_state=42).fit(X_train, y_train)
    y_pred = clf.predict(X_test)
    print(classification_report(y_test, y_pred))
if __name__ == '__main__':
    main()
