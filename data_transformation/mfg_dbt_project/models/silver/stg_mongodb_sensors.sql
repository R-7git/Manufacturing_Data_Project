{{ config(
    materialized='table',
    schema='STG_SCHEMA',
    database='STG_DB'
) }}

WITH raw_json AS (
    -- Reference the Bronze table where your JSON lands
    SELECT 
        RECORD_CONTENT, -- This is your VARIANT column
        INGESTED_AT
    FROM {{ source('stg_db', 'RAW_SENSOR_STREAM') }}
),

flattened_data AS (
    -- Use LATERAL FLATTEN to handle nested JSON arrays if they exist
    -- Or direct casting for simple JSON objects
    SELECT
        RECORD_CONTENT:sensor_id::string AS SENSOR_ID,
        RECORD_CONTENT:metric_name::string AS METRIC_NAME,
        RECORD_CONTENT:metric_value::float AS METRIC_VALUE,
        RECORD_CONTENT:ingestion_timestamp::timestamp AS SOURCE_TIMESTAMP,
        INGESTED_AT AS LOAD_TIMESTAMP
    FROM raw_json
)

-- If you don't have a Mongo source yet, use this dummy select to stop the error
SELECT 
    CAST(NULL AS VARCHAR) as sensor_id,
    CAST(NULL AS VARCHAR) as location,
    CAST(NULL AS TIMESTAMP) as installed_at
LIMIT 0

