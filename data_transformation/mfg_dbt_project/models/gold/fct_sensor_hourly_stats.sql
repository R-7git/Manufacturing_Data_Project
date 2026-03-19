{{ config(materialized='table') }}

SELECT
    sensor_id,
    DATE_TRUNC('hour', ingestion_ts) AS obs_hour,
    AVG(metric_value) AS avg_vibration,
    MAX(metric_value) AS max_vibration,
    COUNT(*) AS reading_count
FROM {{ ref('stg_sensor_data') }}
GROUP BY 1, 2
