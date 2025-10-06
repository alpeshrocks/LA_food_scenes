import argparse, json, os
from typing import Dict, Any, List
from tqdm import tqdm
import pandas as pd
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from .config import DATA_DIR, OPENAI_API_KEY

SYSTEM = """You are a precise information extractor. Given Reddit posts and comments about restaurants in Los Angeles, extract structured mentions.
Return ONLY valid JSON following this schema:
{
  "mentions":[
    {
      "name": "Restaurant name",
      "neighborhood": "Neighborhood if stated or infer with low confidence note",
      "cuisine": "Cuisine/category if mentioned or infer",
      "why": "Short reason/quote for recommendation",
      "sentiment": "positive|neutral|negative",
      "source_url": "Reddit permalink",
      "created_iso": "ISO timestamp of mention"
    }
  ]
}
If nothing is found, return {"mentions": []}.
Keep "why" under 160 characters.
"""

USER_TMPL = """POST_TITLE: {title}
POST_BODY: {selftext}
PERMALINK: {permalink}
TOP_COMMENTS_JSON: {comments_json}
"""

def chunk_comments(comments: List[Dict[str, Any]], max_items=50) -> List[List[Dict[str, Any]]]:
    chunks = []
    for i in range(0, len(comments), max_items):
        chunks.append(comments[i:i+max_items])
    return chunks

def run_llm(model_name: str, batch_size: int):
    llm = ChatOpenAI(model=model_name, temperature=0, timeout=60)
    prompt = ChatPromptTemplate.from_messages([("system", SYSTEM), ("user", USER_TMPL)])
    parser = JsonOutputParser()

    raw_path = os.path.join(DATA_DIR, "raw_threads.jsonl")
    out_path = os.path.join(DATA_DIR, "mentions_raw.jsonl")
    n = 0

    with open(raw_path, "r", encoding="utf-8") as f_in, open(out_path, "w", encoding="utf-8") as f_out:
        for line in tqdm(f_in, desc="LLM extracting"):
            post = json.loads(line)
            comments = post.get("comments", [])
            for chunk in chunk_comments(comments, max_items=batch_size*4):
                user = USER_TMPL.format(
                    title=post.get("title",""),
                    selftext=post.get("selftext",""),
                    permalink=post.get("permalink",""),
                    comments_json=json.dumps(chunk)[:12000]
                )
                try:
                    msg = prompt.format_messages()
                    msg[1].content = user
                    res = llm.invoke(msg)
                    data = parser.parse(res.content)
                except Exception:
                    data = {"mentions": []}

                for m in data.get("mentions", []):
                    m["post_id"] = post.get("id")
                    f_out.write(json.dumps(m) + "\n")
                    n += 1

    print(f"Wrote {n} mentions -> {out_path}")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", type=str, default="gpt-4o-mini")
    ap.add_argument("--batch_size", type=int, default=12)
    args = ap.parse_args()

    if not OPENAI_API_KEY:
        raise RuntimeError("OPENAI_API_KEY missing in environment.")

    run_llm(args.model, args.batch_size)

if __name__ == "__main__":
    main()
