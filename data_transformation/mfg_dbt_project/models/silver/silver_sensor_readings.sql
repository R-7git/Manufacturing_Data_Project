{{ config(materialized='table') }}

-- 1. Reference the Bronze model (This creates the lineage)
WITH raw_readings AS (
    SELECT * FROM {{ ref('bronze_sensor_data') }}
),

-- 2. Apply "Senior Developer" Transformations
transformed AS (
    SELECT
        sensor_id,
        UPPER(metric_name) AS metric_type, -- Standardizing to Uppercase
        metric_value,
        -- Engineering: Converting timestamps to Snowflake standard
        ingestion_timestamp::TIMESTAMP_NTZ AS ingested_at,
        -- Business Logic: Adding a status flag for the factory floor
        CASE 
            WHEN metric_value > 100 THEN 'CRITICAL'
            WHEN metric_value > 80 THEN 'WARNING'
            ELSE 'STABLE'
        END AS health_status
    FROM raw_readings
)

SELECT * FROM transformed
