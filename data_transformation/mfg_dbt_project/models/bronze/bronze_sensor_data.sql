{{ config(materialized='view') }}

SELECT 
    * 
FROM {{ source('bronze_source', 'SENSOR_DATA_LANDING') }}
