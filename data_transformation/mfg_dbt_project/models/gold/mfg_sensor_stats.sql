{{ config(materialized='table', schema='DATA_MARTS') }}

WITH silver_data AS (
    SELECT * FROM {{ ref('silver_sensor_readings') }}
),

aggregated_stats AS (
    SELECT
        sensor_id,
        metric_name,
        DATE_TRUNC('hour', ingestion_timestamp) as observation_hour,
        AVG(metric_value) as avg_reading,
        MAX(metric_value) as max_reading,
        MIN(metric_value) as min_reading,
        COUNT(*) as reading_count
    FROM silver_data
    GROUP BY 1, 2, 3
)

SELECT 
    *,
    -- Flagging high-intensity readings (e.g., Temperature > 80)
    CASE 
        WHEN metric_name = 'Temperature' AND max_reading > 80 THEN 'CRITICAL'
        WHEN metric_name = 'Vibration' AND max_reading > 5 THEN 'MAINTENANCE_REQUIRED'
        ELSE 'NORMAL'
    END as health_status
FROM aggregated_stats
