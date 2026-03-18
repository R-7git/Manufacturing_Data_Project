{{ config(
    materialized='table',
    schema='STG_SCHEMA',
    database='STG_DB'
) }}

-- This provides a clean schema without hitting a non-existent source
SELECT 
    CAST(NULL AS VARCHAR) as SENSOR_ID,
    CAST(NULL AS VARCHAR) as METRIC_NAME,
    CAST(NULL AS FLOAT) as METRIC_VALUE,
    CAST(NULL AS TIMESTAMP) as SOURCE_TIMESTAMP,
    CAST(NULL AS TIMESTAMP) as LOAD_TIMESTAMP
WHERE 1=0
