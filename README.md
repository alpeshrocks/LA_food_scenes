# LA Food Scenes — Reddit + LLM + Multi-source (DE/DS/DA)

Pipeline that scrapes community dining threads, extracts structured insights using LLMs, enriches with Yelp/Google/Eater, dedupes & scores, and serves an interactive app + analytics.

## Quickstart
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # fill keys
# Run end-to-end
python -m src.scrape_reddit --subreddits r/LosAngeles r/FoodLosAngeles --days_back 45 --max_posts 150
python -m src.llm_pipeline --model gpt-4o-mini
python -m src.dedupe_and_score
python -m src.llm_enhance
python -m src.sources_external
python -m src.geocode_and_map --provider nominatim
python -m src.embeddings_and_qna --build
python -m src.cluster_topics
python -m src.trends
python -m src.weekly_digest
streamlit run src/streamlit_app.py
```

## Data Engineering
- Airflow DAG: `airflow/dags/la_food_pipeline.py`
- Warehouse DDL (Postgres): `warehouse/sql/schema.sql`
- dbt project: `dbt_la_food/` (staging + marts + tests)
- Data quality checks: `ge/validate.py`

## Data Science
- Trend classifier: `ml/train_trend_classifier.py`
- Forecast baseline: `ml/forecast_trends.py`
- Topic modeling: `ml/topic_modeling.py`
- Recommender: `ml/recommend.py`

## Data Analyst
- Streamlit tabs: Map, Trends, Heatmap, Q&A, Digest
- Weekly movers + digest for stakeholders
