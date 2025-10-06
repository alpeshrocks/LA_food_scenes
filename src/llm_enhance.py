import argparse, os, json, pandas as pd
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from .config import DATA_DIR, OPENAI_API_KEY

SYSTEM = """Extract enhancements from restaurant mentions:
For each record, identify:
- signature_dishes: list[str] (up to 3)
- sentiment_label: "must-try" | "good" | "mixed"
Return JSON: {"signature_dishes": [...], "sentiment_label": "..."}
Base on text fields provided (name, why, optional context). If insufficient info, leave dishes []."""

USER_TMPL = """NAME: {name}
WHY: {why}
OPTIONAL_CONTEXT: {ctx}
"""

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ctx_path", type=str, default=None, help="Optional jsonl with extra context per restaurant")
    ap.add_argument("--model", type=str, default="gpt-4o-mini")
    args = ap.parse_args()

    if not OPENAI_API_KEY:
        raise RuntimeError("OPENAI_API_KEY missing")

    df = pd.read_csv(os.path.join(DATA_DIR, "mentions_clean.csv"))
    ctx_map = {}
    if args.ctx_path and os.path.exists(args.ctx_path):
        for line in open(args.ctx_path,"r",encoding="utf-8"):
            j = json.loads(line); ctx_map[j.get("name","")] = j

    llm = ChatOpenAI(model=args.model, temperature=0)
    prompt = ChatPromptTemplate.from_messages([("system", SYSTEM), ("user", USER_TMPL)])
    parser = JsonOutputParser()

    sigs, labels = [], []
    for _, r in df.iterrows():
        ctx = ctx_map.get(r["name"],{})
        msg = prompt.format_messages(name=r["name"], why=str(r.get("why",""))[:500], ctx=json.dumps(ctx)[:1200])
        try:
            res = llm.invoke(msg)
            out = parser.parse(res.content)
            sigs.append(", ".join(out.get("signature_dishes", [])[:3]))
            labels.append(out.get("sentiment_label","good"))
        except Exception:
            sigs.append("")
            labels.append("good")
    df["signature_dishes"] = sigs
    df["sentiment_label"] = labels
    df.to_csv(os.path.join(DATA_DIR,"mentions_enhanced.csv"), index=False)
    print("Wrote data/mentions_enhanced.csv")

if __name__ == "__main__":
    main()
