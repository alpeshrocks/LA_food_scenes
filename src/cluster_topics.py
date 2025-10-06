import os, pandas as pd, numpy as np
from sklearn.cluster import KMeans
from openai import OpenAI
from .config import DATA_DIR, OPENAI_API_KEY

def main(k=6):
    path = os.path.join(DATA_DIR,"mentions_enhanced.csv")
    if not os.path.exists(path): path = os.path.join(DATA_DIR,"mentions_clean.csv")
    df = pd.read_csv(path)
    texts = (df["name"].fillna("") + " | " + df["why"].fillna("") + " | " + df.get("signature_dishes","").fillna("")).tolist()
    client = OpenAI(api_key=OPENAI_API_KEY)
    embs = []
    for i in range(0, len(texts), 100):
        chunk = texts[i:i+100]
        resp = client.embeddings.create(model="text-embedding-3-small", input=chunk)
        embs.extend([e.embedding for e in resp.data])
    X = np.array(embs, dtype="float32")
    km = KMeans(n_clusters=k, n_init=10, random_state=42).fit(X)
    df["topic_cluster"] = km.labels_
    df.to_csv(os.path.join(DATA_DIR,"mentions_clustered.csv"), index=False)
    print("Saved data/mentions_clustered.csv with topic clusters.")

if __name__ == "__main__":
    main()
