{{ config(materialized='table') }}

-- 1. Reference the cleaned Silver data
WITH silver_data AS (
    SELECT * FROM {{ ref('silver_sensor_readings') }}
),

-- 2. Aggregate logic for the Executive Dashboard
final_metrics AS (
    SELECT
        sensor_id,
        metric_type,
        COUNT(*) AS total_readings,
        AVG(metric_value) AS avg_reading_value,
        MAX(metric_value) AS peak_reading,
        -- How many times did this machine hit a 'CRITICAL' state?
        COUNT(CASE WHEN health_status = 'CRITICAL' THEN 1 END) AS critical_event_count
    FROM silver_data
    GROUP BY 1, 2
)

SELECT * FROM final_metrics
