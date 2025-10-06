from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash import BashOperator
import os
default_args = {"owner":"you","depends_on_past":False,"email_on_failure":False,"retries":1,"retry_delay":timedelta(minutes=10)}
REPO_DIR = os.environ.get("REPO_DIR", "/opt/airflow/la_food_scenes_project")
with DAG("la_food_pipeline", default_args=default_args, description="ETL + LLM + Enrichment + Map + Digest", schedule_interval="0 7 * * 1", start_date=datetime(2025,1,1), catchup=False) as dag:
    scrape = BashOperator(task_id="scrape_reddit", bash_command=f"cd {REPO_DIR} && . .venv/bin/activate && python -m src.scrape_reddit --subreddits r/LosAngeles r/FoodLosAngeles r/AskLosAngeles --days_back 45 --max_posts 150")
    llm_extract = BashOperator(task_id="llm_extract", bash_command=f"cd {REPO_DIR} && . .venv/bin/activate && python -m src.llm_pipeline --model gpt-4o-mini")
    dedupe = BashOperator(task_id="dedupe_and_score", bash_command=f"cd {REPO_DIR} && . .venv/bin/activate && python -m src.dedupe_and_score")
    enhance = BashOperator(task_id="llm_enhance", bash_command=f"cd {REPO_DIR} && . .venv/bin/activate && python -m src.llm_enhance")
    external = BashOperator(task_id="external_sources", bash_command=f"cd {REPO_DIR} && . .venv/bin/activate && python -m src.sources_external")
    geocode = BashOperator(task_id="geocode_map", bash_command=f"cd {REPO_DIR} && . .venv/bin/activate && python -m src.geocode_and_map --provider nominatim")
    build_index = BashOperator(task_id="qna_index", bash_command=f"cd {REPO_DIR} && . .venv/bin/activate && python -m src.embeddings_and_qna --build")
    cluster = BashOperator(task_id="cluster_topics", bash_command=f"cd {REPO_DIR} && . .venv/bin/activate && python -m src.cluster_topics")
    snapshot = BashOperator(task_id="snapshot_and_movers", bash_command=f"cd {REPO_DIR} && . .venv/bin/activate && python -m src.trends")
    digest = BashOperator(task_id="weekly_digest", bash_command=f"cd {REPO_DIR} && . .venv/bin/activate && python -m src.weekly_digest")
    scrape >> llm_extract >> dedupe >> enhance >> [external, build_index] >> geocode >> cluster >> snapshot >> digest
