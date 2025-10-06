import os, pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
from src.config import DATA_DIR
def recommend(query: str, top_k=10):
    p = os.path.join(DATA_DIR,'mentions_enhanced.csv')
    df = pd.read_csv(p) if os.path.exists(p) else pd.read_csv(os.path.join(DATA_DIR,'mentions_clean.csv'))
    docs = (df['name'].fillna('') + ' | ' + df['cuisine'].fillna('') + ' | ' + df['why'].fillna('') + ' | ' + df.get('signature_dishes','').fillna('')).tolist()
    vec = TfidfVectorizer(max_features=8000, stop_words='english')
    X = vec.fit_transform(docs); qv = vec.transform([query])
    sims = cosine_similarity(qv, X).ravel(); top = sims.argsort()[-top_k:][::-1]
    return df.iloc[top][['name','neighborhood','cuisine','why']].assign(score=sims[top])
if __name__ == '__main__':
    print(recommend('casual Thai in Hollywood', 5).to_string(index=False))
