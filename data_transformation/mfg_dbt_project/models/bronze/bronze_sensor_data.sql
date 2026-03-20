{{ config(materialized='view') }}

SELECT
    RECORD_CONTENT:sensor_id::STRING AS sensor_id,
    RECORD_CONTENT:metric_name::STRING AS metric_name,
    RECORD_CONTENT:metric_value::FLOAT AS metric_value,
    RECORD_CONTENT:ingestion_timestamp::TIMESTAMP AS ingestion_timestamp
FROM {{ source('bronze_layer', 'MFG_SENSOR_STREAM') }}
