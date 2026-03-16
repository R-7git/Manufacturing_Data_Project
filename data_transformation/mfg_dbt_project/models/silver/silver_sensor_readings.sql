{{ config(materialized='table') }}

WITH raw_data AS (
    SELECT * FROM {{ ref('bronze_sensor_data') }}
)

SELECT 
    sensor_id AS "SENSOR_ID",
    UPPER(metric_name) AS "METRIC_NAME",
    metric_value AS "METRIC_VALUE",
    ingestion_timestamp AS "INGESTION_TIMESTAMP"
FROM raw_data
WHERE sensor_id IS NOT NULL
