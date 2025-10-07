# 🍜 LA Food Scenes — Data Engineering + Data Science + Analytics Project  

![Python](https://img.shields.io/badge/Python-3.10-blue) 
![Streamlit](https://img.shields.io/badge/Streamlit-App-red)
![Airflow](https://img.shields.io/badge/Airflow-Orchestration-green)
![dbt](https://img.shields.io/badge/dbt-Transformations-orange)
![CI/CD](https://img.shields.io/badge/GitHub%20Actions-CI%2FCD-lightgrey)
![License](https://img.shields.io/badge/license-MIT-brightgreen)

**LA Food Scenes** is a full-stack data project that scrapes, processes, analyzes, and visualizes Los Angeles restaurant trends from **Reddit, Yelp, Google Places, and EaterLA RSS**.  
The project demonstrates **end-to-end skills** across **Data Engineering, Data Science, and Data Analytics** — making it ideal as a portfolio piece.

---

## ✨ Features

### 🔧 Data Engineering
- **ETL pipeline** orchestrated via **Apache Airflow**.  
- **Multi-source ingestion** (Reddit + Yelp + Google Places + RSS).  
- **Warehouse schema** (Postgres star schema with fact/dim + marts).  
- **dbt models** for transformations, marts, and data tests.  
- **Data quality validation** with Great Expectations-style checks.  
- **CI/CD** via GitHub Actions nightly pipeline.  
- **Dockerized deployment** for portability.  

### 🧠 Data Science
- **LLM enrichment**: extract *signature dishes* + classify sentiment (`must-try`, `good`, `mixed`).  
- **Embeddings + RAG**: semantic Q&A search like *“Where should I go for Thai in Hollywood under $30?”*.  
- **Trend classifier** (RandomForest) to predict which restaurants will trend.  
- **Forecasting** (time-series moving average).  
- **Topic modeling** (LDA/BERT-based clustering).  
- **Recommender system** (TF-IDF + cosine similarity).  

### 📊 Data Analytics
- **Interactive Streamlit app** with:  
  - 🌍 **Map** of restaurants (geocoded).  
  - 📈 **Buzz timeline** & “movers” (week-over-week trending).  
  - 🗺 **Neighborhood heatmap**.  
  - 🔎 **LLM-powered Q&A search**.  
  - 📰 **Weekly Buzz Digest** (auto-generated summaries).  
- **Warehouse marts** feeding BI dashboards (Power BI / Looker Studio).  
- **Sample data provided** for quick demos.  

---

## 📂 Project Structure

```
la_food_scenes_project/
│
├── airflow/              # Airflow DAGs for orchestration
├── dbt_la_food/          # dbt project with seeds + marts
├── data/                 # Raw + processed + sample data
├── warehouse/            # Warehouse schema + seeds
├── ml/                   # ML models (trend classifier, recommender, etc.)
├── src/                  # Core ingestion + processing scripts
├── ge/                   # Data quality checks
├── outputs/              # Digests, maps, artifacts
├── streamlit_app.py      # Interactive dashboard
├── Dockerfile            # Containerization
└── README.md             # (this file)
```

---

## 🚀 Quickstart

1. **Clone repo & setup env**
   ```bash
   git clone https://github.com/<your-handle>/la_food_scenes.git
   cd la_food_scenes_project
   python -m venv .venv && source .venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Configure environment**
   ```bash
   cp .env.example .env
   # Add keys: OPENAI_API_KEY, REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET, YELP_API_KEY (optional)
   ```

3. **Run pipeline locally**
   ```bash
   python -m src.scrape_reddit --subreddits r/LosAngeles r/FoodLosAngeles --days_back 30
   python -m src.llm_pipeline --model gpt-4o-mini
   python -m src.dedupe_and_score
   python -m src.llm_enhance
   python -m src.sources_external
   python -m src.geocode_and_map
   python -m src.trends
   python -m src.weekly_digest
   ```

4. **Launch the app**
   ```bash
   streamlit run src/streamlit_app.py
   ```

---

## 🧪 Sample Data

We provide demo data under `data/mentions_enhanced.csv` and warehouse seeds in `warehouse/seeds/`.  
This allows you to explore dashboards and models without scraping.

---

## 📊 Example Visuals

> _Replace these with screenshots of your app and charts._

- Buzz timeline (Altair)  
- LA neighborhood heatmap (Folium)  
- Weekly Digest snippet  

---

## 🛠️ Tech Stack

- **Languages**: Python, SQL  
- **Frameworks**: Streamlit, LangChain, scikit-learn  
- **Data Engineering**: Airflow, dbt, Great Expectations, Docker  
- **Data Science**: RandomForest, LDA, embeddings, RAG  
- **Data Storage**: Postgres / Snowflake / BigQuery (pluggable)  
- **Visualization**: Altair, Folium, Power BI, Looker Studio  

---

## 🌟 Why This Project Matters

Most food trend apps rely only on static reviews.  
**This project dynamically surfaces real-time restaurant trends using community buzz + ML insights.**  
It’s a **portfolio-ready project** that demonstrates:  
- Scalable pipelines (DE)  
- Predictive/ML modeling (DS)  
- Clear analytics and dashboards (DA)  

---

## 📌 Future Enhancements

- Deploy to cloud (AWS/GCP/Azure)  
- MLflow model tracking  
- User personalization (favorites + alerts)  
- Push digests via email/Slack  

---

## 👤 Author

**Alpesh Shinde**  
🎓 MS CS @ USC | Data Engineering • Data Science • AI/ML • SWE  
🌍 Passion for food, travel, and building impactful tech.  

[LinkedIn](https://www.linkedin.com/in/alpeshshinde/) • [GitHub](https://github.com/alpeshrocks) • [Portfolio](https://alpeshrocks.github.io/alpesh-portfolio/)

---

## 📜 License
This project is licensed under the MIT License — free to use and adapt.
