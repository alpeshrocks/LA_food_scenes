{{ config(materialized='view') }}
SELECT
  name, neighborhood, cuisine,
  COUNT(*) as mentions,
  SUM(score_buzz) as buzz,
  MAX(score_trend) as recent_trend
FROM {{ ref('stg_mentions') }}
GROUP BY 1,2,3
ORDER BY buzz DESC;
