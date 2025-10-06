import os, pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import LatentDirichletAllocation as LDA
from src.config import DATA_DIR
def main(k=6):
    p = os.path.join(DATA_DIR,'mentions_enhanced.csv')
    df = pd.read_csv(p) if os.path.exists(p) else pd.read_csv(os.path.join(DATA_DIR,'mentions_clean.csv'))
    texts = (df['name'].fillna('') + ' ' + df['why'].fillna('') + ' ' + df.get('signature_dishes','').fillna('')).tolist()
    vec = TfidfVectorizer(max_features=5000, stop_words='english')
    X = vec.fit_transform(texts)
    lda = LDA(n_components=k, random_state=42)
    lda.fit(X)
    comps = lda.components_; terms = vec.get_feature_names_out()
    print('Topics:')
    for i, comp in enumerate(comps):
        top = comp.argsort()[-10:][::-1]
        print(f'Topic {i}: ' + ', '.join(terms[j] for j in top))
if __name__ == '__main__':
    main()
