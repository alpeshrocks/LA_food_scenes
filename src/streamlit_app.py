import streamlit as st
import pandas as pd, numpy as np, os, altair as alt
import folium
from folium.plugins import HeatMap
from streamlit.components.v1 import html
from .config import DATA_DIR, OUT_DIR
from .embeddings_and_qna import search as qna_search

st.set_page_config(page_title="LA Food Scenes", layout="wide")
st.title("🍴 LA Food Scenes — Reddit + Multi-source")

# Load data
def load_df():
    if os.path.exists(os.path.join(DATA_DIR,"mentions_clustered.csv")):
        return pd.read_csv(os.path.join(DATA_DIR,"mentions_clustered.csv"))
    if os.path.exists(os.path.join(DATA_DIR,"mentions_enhanced.csv")):
        return pd.read_csv(os.path.join(DATA_DIR,"mentions_enhanced.csv"))
    if os.path.exists(os.path.join(DATA_DIR,"mentions_clean.csv")):
        return pd.read_csv(os.path.join(DATA_DIR,"mentions_clean.csv"))
    st.stop()

df = load_df()

tabs = st.tabs(["Explore Map","Trends","Heatmap","Q&A Search","Digest"])

# --- Explore Map
with tabs[0]:
    with st.sidebar:
        st.header("Filters")
        cuisines = sorted([c for c in df.get("cuisine", pd.Series()).dropna().unique().tolist() if c])
        hoods = sorted([h for h in df.get("neighborhood", pd.Series()).dropna().unique().tolist() if h])
        sel_cuisine = st.multiselect("Cuisine", cuisines)
        sel_hood = st.multiselect("Neighborhood", hoods)
        min_buzz = st.slider("Min Buzz", 0, int(df.get("score_buzz", pd.Series([0])).max()), 0)
        must_try_only = st.checkbox("Only 'Must-try'")

    q = df.copy()
    if sel_cuisine: q = q[q["cuisine"].isin(sel_cuisine)]
    if sel_hood: q = q[q["neighborhood"].isin(sel_hood)]
    if "score_buzz" in q.columns: q = q[q["score_buzz"] >= min_buzz]
    if must_try_only and "sentiment_label" in q.columns: q = q[q["sentiment_label"]=="must-try"]

    st.subheader(f"Results ({len(q)})")
    st.dataframe(q[["name","neighborhood","cuisine","signature_dishes","why","score_buzz","score_trend","score_total","source_url"]].fillna(""))

    # Map
    map_path = os.path.join(OUT_DIR, "la_food_map.html")
    if os.path.exists(map_path):
        with open(map_path, "r", encoding="utf-8") as f:
            html_data = f.read()
        html(html_data, height=700)
    else:
        st.info("Map not found. Run geocode_and_map.py to generate a Folium map.")

# --- Trends
with tabs[1]:
    st.subheader("Buzz timeline (weekly)")
    # Build a weekly time series from mentions if available
    if os.path.exists(os.path.join(DATA_DIR,"mentions_raw.jsonl")):
        rows = [json.loads(l) for l in open(os.path.join(DATA_DIR,"mentions_raw.jsonl"),"r",encoding="utf-8")]
        raw = pd.DataFrame(rows)
        raw["week"] = pd.to_datetime(raw["created_iso"], errors="coerce").dt.to_period("W").astype(str)
        ts = raw.groupby("week").size().reset_index(name="mentions")
        chart = alt.Chart(ts).mark_line().encode(x="week:T", y="mentions:Q", tooltip=["week","mentions"]).properties(height=300)
        st.altair_chart(chart, use_container_width=True)
    else:
        st.info("No raw mention timestamps found. Create mentions_raw.jsonl via LLM pipeline.")

    if os.path.exists(os.path.join(DATA_DIR,"movers.csv")):
        st.subheader("Top Movers (WoW)")
        st.dataframe(pd.read_csv(os.path.join(DATA_DIR,"movers.csv")))
    else:
        st.caption("Run trends.py to generate movers.")

# --- Heatmap
with tabs[2]:
    st.subheader("Neighborhood density heatmap")
    if all(c in df.columns for c in ["lat","lng"]):
        m = folium.Map(location=[34.0522, -118.2437], zoom_start=10)
        pts = df[["lat","lng"]].dropna().values.tolist()
        if pts:
            HeatMap(pts, radius=18).add_to(m)
        html(folium.Figure().add_child(m)._repr_html_(), height=700)
    else:
        st.info("No coordinates found. Run geocode_and_map.py first.")

# --- Q&A
with tabs[3]:
    st.subheader("Ask a question")
    prompt = st.text_input("E.g., Where should I go for Thai in Hollywood under $30?")
    top_k = st.slider("Results", 3, 15, 6)
    if st.button("Search") and prompt:
        try:
            res = qna_search(prompt, top_k=top_k)
            st.dataframe(res[["name","neighborhood","cuisine","signature_dishes","why","similarity","source_url"]])
        except Exception as e:
            st.error(str(e))
            st.caption("Make sure you've built the Q&A index via: python -m src.embeddings_and_qna --build")

# --- Digest
with tabs[4]:
    st.subheader("Weekly Buzz Digest")
    dig_dir = os.path.join(OUT_DIR,"digests")
    if os.path.exists(dig_dir):
        files = sorted([f for f in os.listdir(dig_dir) if f.endswith(".md")], reverse=True)
        if files:
            last = files[0]
            st.markdown(open(os.path.join(dig_dir,last),"r",encoding="utf-8").read())
        else:
            st.info("No digests yet. Run weekly_digest.py.")
    else:
        st.info("No digests directory found.")
