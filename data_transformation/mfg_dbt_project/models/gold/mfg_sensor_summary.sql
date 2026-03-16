{{ config(materialized='table') }}

SELECT 
    "SENSOR_ID",
    "METRIC_NAME" as METRIC_TYPE,
    COUNT(*) as TOTAL_READINGS,
    AVG("METRIC_VALUE") as AVG_READING_VALUE,
    MAX("METRIC_VALUE") as PEAK_READING_VALUE,
    COUNT(CASE WHEN "METRIC_VALUE" > 90 THEN 1 END) as HEALTH_STATUS_COUNT
FROM {{ ref('silver_sensor_readings') }}
GROUP BY 1, 2
