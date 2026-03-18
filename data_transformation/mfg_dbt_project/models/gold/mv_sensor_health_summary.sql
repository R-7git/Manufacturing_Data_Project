{{ config(
    materialized='view' 
) }}

SELECT 
    metric_name,
    AVG(metric_value) as avg_value,
    COUNT(*) as total_readings,
    MAX(last_updated_at) as last_reading_at
FROM {{ ref('rpt_sensor_master') }}
GROUP BY 1
