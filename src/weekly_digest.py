import os, pandas as pd, datetime as dt
from .config import DATA_DIR, OUT_DIR, OPENAI_API_KEY
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

SYSTEM = "Write a crisp, upbeat weekly newsletter summarizing LA dining buzz. Use bullet points. 200-300 words."

def main():
    df_mov = os.path.join(DATA_DIR,"movers.csv")
    df_ext = os.path.join(DATA_DIR,"external_merged.csv")
    movers = pd.read_csv(df_mov) if os.path.exists(df_mov) else pd.DataFrame()
    external = pd.read_csv(df_ext) if os.path.exists(df_ext) else pd.DataFrame()

    context = []
    if not movers.empty:
        context.append("Top movers this week:\n" + "\n".join(f"- {r.name} (Δ {r.delta:.2f})" for _, r in movers.head(10).iterrows()))
    if not external.empty:
        context.append("\nNew/openings spotted:\n" + "\n".join(f"- {r['name']} — {r.get('why','')}" for _, r in external.head(10).iterrows()))

    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.4)
    tmpl = ChatPromptTemplate.from_messages([("system", SYSTEM), ("user","Context:\n{ctx}\nWrite the digest.")])
    res = llm.invoke(tmpl.format_messages(ctx="\n".join(context)))
    fname = os.path.join(OUT_DIR,"digests", f"buzz_digest_{dt.date.today().isoformat()}.md")
    with open(fname,"w",encoding="utf-8") as f:
        f.write(res.content)
    print(f"Saved digest -> {fname}")

if __name__ == "__main__":
    main()
