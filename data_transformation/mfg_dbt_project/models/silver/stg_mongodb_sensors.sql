{{ config(
    materialized='table',
    schema='STG_SCHEMA',
    database='STG_DB'
) }}

/* 
   Note: We are using a CTE for the JSON logic so it's ready when your 
   MongoDB stream is active. For now, we union it with a dummy 
   to prevent dbt from crashing on an empty source.
*/

WITH raw_json AS (
    -- Reference the Bronze table/stream where JSON lands
    -- Ensure 'RAW_SENSOR_STREAM' exists in your sources.yml
    SELECT 
        RECORD_CONTENT, 
        INGESTED_AT
    FROM {{ source('stg_db', 'RAW_SENSOR_STREAM') }}
    LIMIT 0 -- Set to 0 while the source is empty to prevent execution errors
),

flattened_data AS (
    SELECT
        RECORD_CONTENT:sensor_id::string AS SENSOR_ID,
        RECORD_CONTENT:metric_name::string AS METRIC_NAME,
        RECORD_CONTENT:metric_value::float AS METRIC_VALUE,
        RECORD_CONTENT:ingestion_timestamp::timestamp AS SOURCE_TIMESTAMP,
        INGESTED_AT AS LOAD_TIMESTAMP
    FROM raw_json
)

-- Final Select: Combines your logic with the required columns for downstream models
SELECT 
    SENSOR_ID,
    METRIC_NAME,
    METRIC_VALUE,
    SOURCE_TIMESTAMP,
    LOAD_TIMESTAMP
FROM flattened_data

UNION ALL

-- This keeps the model "Alive" with the correct schema even if the source is empty
SELECT 
    CAST(NULL AS VARCHAR) as SENSOR_ID,
    CAST(NULL AS VARCHAR) as METRIC_NAME,
    CAST(NULL AS FLOAT) as METRIC_VALUE,
    CAST(NULL AS TIMESTAMP) as SOURCE_TIMESTAMP,
    CAST(NULL AS TIMESTAMP) as LOAD_TIMESTAMP
WHERE 1=0 
