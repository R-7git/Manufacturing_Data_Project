{{ config(
    materialized='incremental',
    unique_key='sensor_id',
    incremental_strategy='merge'
) }}

SELECT 
    sensor_id,
    metric_name,
    metric_value,
    ingestion_timestamp AS last_updated_at
FROM {{ ref('bronze_sensor_data') }}

{% if is_incremental() %}
  -- This filter ensures we only process new data from the stream/staging
  WHERE ingestion_timestamp > (SELECT MAX(last_updated_at) FROM {{ this }})
{% endif %}
