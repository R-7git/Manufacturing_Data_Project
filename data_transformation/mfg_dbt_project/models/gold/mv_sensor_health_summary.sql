{{ config(
    materialized='materialized_view',
    schema='RPT_SCHEMA',
    database='DW_DB'
) }}

SELECT 
    SENSOR_ID,
    METRIC_NAME,
    AVG(METRIC_VALUE) AS AVG_VALUE,
    MAX(METRIC_VALUE) AS PEAK_VALUE,
    COUNT(*) AS TOTAL_READINGS,
    CURRENT_TIMESTAMP() AS LAST_REFRESHED_AT
FROM {{ ref('rpt_sensor_master') }}
GROUP BY 1, 2
