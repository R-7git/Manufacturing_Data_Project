{{ config(
    materialized='incremental',
    unique_key='sensor_id',
    incremental_strategy='merge'
) }}

WITH source_data AS (
    SELECT * FROM {{ ref('bronze_sensor_data') }}
)

SELECT 
    sensor_id,
    metric_name,
    metric_value,
    last_updated_at
FROM source_data

{% if is_incremental() %}
  -- 1. First, filter for ONLY new data
  WHERE last_updated_at > (SELECT MAX(last_updated_at) FROM {{ this }})
{% endif %}

-- 2. Then, pick only the latest record per sensor to avoid the 'Duplicate' error
QUALIFY ROW_NUMBER() OVER (PARTITION BY sensor_id ORDER BY last_updated_at DESC) = 1
