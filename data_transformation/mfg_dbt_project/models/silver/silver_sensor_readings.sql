{{ config(materialized='table') }}

WITH raw_data AS (
    SELECT * FROM {{ ref('bronze_sensor_data') }}
)

SELECT 
    SENSOR_ID AS "SENSOR_ID",
    -- Industry Standard: Trim and Upper to prevent 'Accepted Values' failure
    TRIM(UPPER(METRIC_NAME)) AS "METRIC_NAME",
    METRIC_VALUE AS "METRIC_VALUE",
    INGESTION_TIMESTAMP AS "INGESTION_TIMESTAMP"
FROM raw_data
WHERE SENSOR_ID IS NOT NULL
