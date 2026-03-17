{{ config(materialized='view') }}

SELECT 
    * 
FROM {{ source('stg_db', 'STG_SENSOR_DATA') }} -- Changed from 'bronze_source' to 'stg_db'
