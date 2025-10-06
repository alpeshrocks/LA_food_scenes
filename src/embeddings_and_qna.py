import os, json, argparse, numpy as np, pandas as pd
from typing import List
from .config import DATA_DIR, OPENAI_API_KEY
from openai import OpenAI

INDEX_PATH = os.path.join(DATA_DIR, "qna_index.npz")

def build_index():
    df = pd.read_csv(os.path.join(DATA_DIR,"mentions_enhanced.csv")) if os.path.exists(os.path.join(DATA_DIR,"mentions_enhanced.csv")) else pd.read_csv(os.path.join(DATA_DIR,"mentions_clean.csv"))
    texts = (df["name"].fillna("") + " | " + df["neighborhood"].fillna("") + " | " + df["cuisine"].fillna("") + " | " + df["why"].fillna("") + " | " + df.get("signature_dishes","").fillna("")).tolist()
    client = OpenAI(api_key=OPENAI_API_KEY)
    embs = []
    for i in range(0, len(texts), 100):
        chunk = texts[i:i+100]
        resp = client.embeddings.create(model="text-embedding-3-small", input=chunk)
        embs.extend([e.embedding for e in resp.data])
    embs = np.array(embs).astype("float32")
    np.savez(INDEX_PATH, vectors=embs, ids=np.arange(len(texts)))
    df.to_csv(os.path.join(DATA_DIR,"qna_index_rows.csv"), index=False)
    print(f"Index built with {len(texts)} items.")

def search(query: str, top_k=10):
    client = OpenAI(api_key=OPENAI_API_KEY)
    q = client.embeddings.create(model="text-embedding-3-small", input=[query]).data[0].embedding
    data = np.load(INDEX_PATH)
    V = data["vectors"]; ids = data["ids"]
    vq = np.array(q, dtype="float32")
    # cosine similarity
    Vn = V / (np.linalg.norm(V, axis=1, keepdims=True) + 1e-9)
    vqn = vq / (np.linalg.norm(vq) + 1e-9)
    sims = (Vn @ vqn)
    top = sims.argsort()[-top_k:][::-1]
    rows = pd.read_csv(os.path.join(DATA_DIR,"qna_index_rows.csv")).iloc[ids[top]]
    rows = rows.assign(similarity=sims[top])
    return rows

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--build", action="store_true")
    ap.add_argument("--ask", type=str, default=None)
    ap.add_argument("--top_k", type=int, default=5)
    args = ap.parse_args()

    if args.build:
        build_index()
    if args.ask:
        print(search(args.ask, args.top_k).to_string(index=False))

if __name__ == "__main__":
    main()
