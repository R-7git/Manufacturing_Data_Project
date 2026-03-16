{{ config(materialized='view') }}

-- Industry Standard: Selecting from the landing table populated by the producer
SELECT 
    sensor_id,
    metric_name,
    metric_value,
    ingestion_timestamp
FROM MFG_BRONZE_DB.RAW_DATA.SENSOR_DATA_LANDING
