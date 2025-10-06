import argparse, os, json, pandas as pd
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from .config import DATA_DIR, OPENAI_API_KEY

SYSTEM = """Enhance each restaurant mention.
Return JSON with:
- signature_dishes: list[str] (<=3)
- sentiment_label: "must-try" | "good" | "mixed"
If info insufficient, dishes []."""

USER_TMPL = """NAME: {name}
WHY: {why}
"""

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", type=str, default="gpt-4o-mini")
    args = ap.parse_args()

    if not OPENAI_API_KEY:
        raise RuntimeError("OPENAI_API_KEY missing")

    import pandas as pd, json
    df = pd.read_csv(os.path.join(DATA_DIR, "mentions_clean.csv"))
    llm = ChatOpenAI(model=args.model, temperature=0)
    prompt = ChatPromptTemplate.from_messages([("system", SYSTEM), ("user", USER_TMPL)])
    parser = JsonOutputParser()

    sigs, labels = [], []
    for _, r in df.iterrows():
        msg = prompt.format_messages(name=r["name"], why=str(r.get("why",""))[:500])
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
