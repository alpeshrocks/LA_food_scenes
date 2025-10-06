# LA Food Scenes — Reddit + LLM Pipeline

Analyze community-driven restaurant recommendations in Los Angeles by scraping subreddit threads, extracting structured insights with an LLM, deduplicating/ ranking, and visualizing on an interactive map + Streamlit dashboard.

## What you get
- **Scraper**: Pulls posts + full comment trees from target subreddits.
- **LLM extractor**: Uses an LLM (via LangChain) to convert messy threads into structured restaurant mentions.
- **Cleaner + Scorer**: Deduplicates names (fuzzy match), computes Buzz/Trend scores.
- **Map & App**: Geocodes and renders a Folium map; Streamlit app for filters and exploration.
- **Reproducible**: All steps save intermediate artifacts in `/data` and `/outputs`.

## Project Structure
```
la_food_scenes_project/
├─ src/
│  ├─ config.py
│  ├─ scrape_reddit.py
│  ├─ llm_pipeline.py
│  ├─ dedupe_and_score.py
│  ├─ geocode_and_map.py
│  └─ streamlit_app.py
├─ data/
│  ├─ raw_threads.jsonl            # scraped raw threads
│  ├─ mentions_raw.jsonl           # LLM-extracted raw mentions
│  ├─ mentions_clean.csv           # deduped & scored
│  └─ sample.csv                   # starter data (optional)
├─ outputs/
│  └─ la_food_map.html             # Folium map
├─ .env.example
├─ requirements.txt
└─ README.md
```

## ⚙️ Setup
1. **Python** 3.10+ recommended.
2. Clone/download this folder.
3. Create a virtual environment and install deps:
   ```bash
   python -m venv .venv && source .venv/bin/activate
   pip install -r requirements.txt
   ```
4. Copy `.env.example` to `.env` and fill in keys:
   - `REDDIT_CLIENT_ID`, `REDDIT_CLIENT_SECRET`, `REDDIT_USER_AGENT`
   - `OPENAI_API_KEY` (or another provider supported by LangChain)
   - _(optional)_ `GEOCODER="nominatim"` or `"google"` and `GOOGLE_MAPS_API_KEY` if using Google.
5. (Optional) NLTK one-time setup for sentence tokenization:
   ```bash
   python -c "import nltk; nltk.download('punkt')"
   ```

## 🚀 Run the pipeline
These commands can be run step-by-step or chained.

1) **Scrape Reddit**
```bash
python -m src.scrape_reddit --subreddits r/LosAngeles r/FoodLosAngeles r/AskLosAngeles   --days_back 45 --max_posts 150 --query "restaurant OR opening OR recommend OR eats OR best"
```
- Saves `data/raw_threads.jsonl`

2) **Extract mentions with LLM**
```bash
python -m src.llm_pipeline --model gpt-4o-mini --batch_size 12
```
- Saves `data/mentions_raw.jsonl`

3) **Deduplicate + score**
```bash
python -m src.dedupe_and_score --min_similarity 88 --decay_half_life_days 30
```
- Saves `data/mentions_clean.csv`

4) **Geocode + make map**
```bash
python -m src.geocode_and_map --provider nominatim
```
- Saves `outputs/la_food_map.html`

5) **Open the Streamlit app**
```bash
streamlit run src/streamlit_app.py
```

## Data schema
**mentions_clean.csv** (final):
- `name` — restaurant name
- `neighborhood` — inferred or extracted
- `cuisine` — inferred category
- `why` — short reason/quote
- `source_url` — Reddit permalink
- `score_buzz` — mentions × avg upvotes
- `score_trend` — time-decayed weight
- `score_total` — composite score
- `lat`, `lng` — coordinates (if geocoded)
- `first_seen`, `last_seen` — ISO dates

## 📝 Notes
- Respect subreddit rules and API rate limits.
- This is for educational/research use; do not spam or republish OP content wholesale.
- If you don't want to scrape, you can seed from `data/sample.csv` and skip to `dedupe_and_score` and `geocode_and_map`.


---

## New Features

### Multi-Source Integration
```bash
python -m src.sources_external  # writes data/external_merged.csv
```

### Menu-Level Insights + Sentiment
```bash
# enhances mentions with signature dishes + sentiment_label (must-try/good/mixed)
python -m src.llm_enhance --model gpt-4o-mini
```

### Trend Tracking (Snapshots & Movers)
```bash
# snapshot this week's data
python -m src.trends
# after 2+ weeks of snapshots, check movers
python -m src.trends
```

### Embeddings + Q&A (RAG)
```bash
# build embedding index
python -m src.embeddings_and_qna --build
# ask
python -m src.embeddings_and_qna --ask "Where should I go for Thai in Hollywood under $30?"
```

### Weekly Buzz Digest
```bash
python -m src.weekly_digest  # writes outputs/digests/buzz_digest_YYYY-MM-DD.md
```

### Topic Clustering
```bash
python -m src.cluster_topics  # writes data/mentions_clustered.csv
```

### Streamlit App (updated)
- Tabs: Map, Trends (buzz timeline + movers), Heatmap, Q&A Search, Digest
```bash
streamlit run src/streamlit_app.py
```
