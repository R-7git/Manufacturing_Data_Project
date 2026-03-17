{% snapshot sensor_history_snapshot %}

{{
    config(
      target_database='DW_DB',
      target_schema='RPT_SCHEMA',
      unique_key='SENSOR_ID',

      strategy='check',
      check_cols=['METRIC_VALUE'],
      invalidate_hard_deletes=True,
    )
}}

-- This source points to your Silver/Staging table
SELECT 
    SENSOR_ID,
    METRIC_NAME,
    METRIC_VALUE,
    INGESTION_TIMESTAMP
FROM {{ source('stg_db', 'STG_SENSOR_DATA') }}

{% endsnapshot %}
