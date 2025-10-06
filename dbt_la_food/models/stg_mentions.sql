{{ config(materialized='table') }}
WITH base AS (
  SELECT
    name, neighborhood, cuisine, why, sentiment_label,
    score_buzz, score_trend, score_total, source_url
  FROM {{ ref('seed_mentions') }}
)
SELECT * FROM base;
