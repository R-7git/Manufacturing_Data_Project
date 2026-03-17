{{ config(
    materialized='incremental',
    unique_key='SENSOR_ID',
    schema='RPT_SCHEMA',
    database='DW_DB',
    incremental_strategy='merge'
) }}

WITH stream_data AS (
    -- This is the CDC Stream created by Terraform
    SELECT 
        SENSOR_ID,
        METRIC_NAME,
        METRIC_VALUE,
        INGESTION_TIMESTAMP,
        METADATA_FILENAME,
        METADATA$ACTION,    -- Snowflake Stream Metadata
        METADATA$ISUPDATE   -- Snowflake Stream Metadata
    FROM {{ source('stg_db', 'SENSOR_DATA_STREAM') }}
    WHERE METADATA$ACTION = 'INSERT' -- Only process new/changed records
)

SELECT 
    SENSOR_ID,
    METRIC_NAME,
    METRIC_VALUE,
    INGESTION_TIMESTAMP AS LAST_UPDATED_AT,
    METADATA_FILENAME
FROM stream_data
