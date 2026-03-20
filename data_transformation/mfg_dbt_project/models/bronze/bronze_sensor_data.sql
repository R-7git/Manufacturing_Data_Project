{{ config(materialized='view') }}

SELECT
    RECORD_CONTENT:sensor_id::STRING AS sensor_id,
    RECORD_CONTENT:metric_name::STRING AS metric_name,
    RECORD_CONTENT:metric_value::FLOAT AS metric_value,
    -- Standardizing name to last_updated_at for the entire pipeline
    RECORD_CONTENT:ingestion_timestamp::TIMESTAMP AS last_updated_at 
FROM {{ source('bronze_layer', 'MFG_SENSOR_STREAM') }}
