{{ config(
    materialized='view',
    schema='RPT_SCHEMA',
    database='DW_DB'
) }}

WITH current_status AS (
    SELECT * FROM {{ ref('rpt_sensor_master') }}
),

history_summary AS (
    -- Counting how many times each sensor has changed state
    SELECT 
        SENSOR_ID,
        COUNT(*) as VERSION_COUNT,
        MIN(dbt_valid_from) as FIRST_SEEN,
        MAX(dbt_valid_from) as LAST_CHANGE
    FROM {{ ref('sensor_history_snapshot') }}
    GROUP BY 1
)

SELECT 
    c.SENSOR_ID,
    c.METRIC_NAME,
    c.METRIC_VALUE AS CURRENT_VALUE,
    -- Business Logic: Health Flagging
    CASE 
        WHEN c.METRIC_VALUE > 90 THEN 'CRITICAL'
        WHEN c.METRIC_VALUE > 75 THEN 'WARNING'
        ELSE 'HEALTHY'
    END as CURRENT_HEALTH_STATUS,
    h.VERSION_COUNT,
    h.FIRST_SEEN,
    h.LAST_CHANGE
FROM current_status c
LEFT JOIN history_summary h ON c.SENSOR_ID = h.SENSOR_ID
