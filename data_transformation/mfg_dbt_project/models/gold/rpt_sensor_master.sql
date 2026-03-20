{{ config(
    materialized='incremental',
    unique_key='sensor_id',
    incremental_strategy='merge'
) }}

WITH source_data AS (
    SELECT * FROM {{ ref('bronze_sensor_data') }}
),

-- Use QUALIFY to pick only the most recent record per sensor_id
latest_records AS (
    SELECT * 
    FROM source_data
    QUALIFY ROW_NUMBER() OVER (PARTITION BY sensor_id ORDER BY last_updated_at DESC) = 1
)

SELECT 
    sensor_id,
    metric_name,
    metric_value,
    last_updated_at
FROM latest_records

{% if is_incremental() %}
  WHERE last_updated_at > (SELECT MAX(last_updated_at) FROM {{ this }})
{% endif %}
