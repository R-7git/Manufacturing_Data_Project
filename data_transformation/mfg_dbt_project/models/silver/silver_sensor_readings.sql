{{ config(materialized='table') }}

WITH raw_data AS (
    -- Reference the Bronze VIEW we just updated above
    SELECT * FROM {{ ref('bronze_sensor_data') }}
)

SELECT 
    SENSOR_ID AS "SENSOR_ID",
    -- This regex strips '(C)', '(BAR)', etc. and forces UPPERCASE
    UPPER(REGEXP_REPLACE(METRIC_NAME, ' \\(.*\\)', '')) AS "METRIC_NAME",
    METRIC_VALUE AS "METRIC_VALUE",
    INGESTION_TIMESTAMP AS "INGESTION_TIMESTAMP"
FROM raw_data
WHERE SENSOR_ID IS NOT NULL
