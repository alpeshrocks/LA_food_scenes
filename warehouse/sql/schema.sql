-- Star schema for LA Food Scenes
CREATE TABLE IF NOT EXISTS restaurants_dim (
  restaurant_id SERIAL PRIMARY KEY,
  name TEXT NOT NULL,
  name_norm TEXT NOT NULL,
  neighborhood TEXT,
  cuisine TEXT,
  first_seen TIMESTAMP,
  last_seen TIMESTAMP
);
CREATE TABLE IF NOT EXISTS sources_dim (
  source_id SERIAL PRIMARY KEY,
  source_name TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS mentions_fact (
  mention_id BIGSERIAL PRIMARY KEY,
  restaurant_id INT REFERENCES restaurants_dim(restaurant_id),
  source_id INT REFERENCES sources_dim(source_id),
  created_at TIMESTAMP,
  sentiment_label TEXT,
  why TEXT,
  url TEXT,
  score_buzz NUMERIC,
  score_trend NUMERIC
);
CREATE MATERIALIZED VIEW IF NOT EXISTS vw_trending_restaurants AS
SELECT r.name, r.neighborhood, r.cuisine,
       SUM(COALESCE(m.score_buzz,1)) AS buzz,
       MAX(m.score_trend) AS recent_trend,
       MAX(m.created_at) AS last_mention
FROM mentions_fact m
JOIN restaurants_dim r ON r.restaurant_id = m.restaurant_id
GROUP BY r.name, r.neighborhood, r.cuisine
ORDER BY buzz DESC;
CREATE MATERIALIZED VIEW IF NOT EXISTS vw_new_openings AS
SELECT DISTINCT r.name, r.neighborhood, r.cuisine, MIN(m.created_at) as first_mention
FROM mentions_fact m
JOIN restaurants_dim r ON r.restaurant_id = m.restaurant_id
WHERE m.created_at >= NOW() - INTERVAL '60 days'
ORDER BY first_mention DESC;
