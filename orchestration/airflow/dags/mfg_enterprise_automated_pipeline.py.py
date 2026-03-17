from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta

default_args = {
    'owner': 'roshan',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    'mfg_enterprise_automated_pipeline',
    default_args=default_args,
    description='Enterprise Migration: STG to DW with SCD Type 1 & 2',
    schedule_interval='@hourly',
    catchup=False,
    tags=['migration', 'snowflake', 'scd', 'json'],
) as dag:

    # STEP 1: DATA LAKE UPLOAD (Source -> MinIO)
    upload_to_minio = BashOperator(
        task_id='upload_source_to_datalake',
        bash_command='python3 /opt/airflow/project/scripts/setup/minio_data_uploader.py'
    )

    # STEP 2: BATCH INGESTION (COPY INTO STG_DB)
    ingest_batch_to_stg = BashOperator(
        task_id='ingest_batch_to_staging',
        bash_command="""
        cd /opt/airflow/project/data_transformation/mfg_dbt_project && \
        dbt run-operation load_internal_stage --args "{stage_name: 'MINIO_RAW_STAGE', table_name: 'STG_SENSOR_DATA'}"
        """
    )

    # STEP 3: SEMI-STRUCTURED PROCESSING (Flattening MongoDB/Kafka JSON)
    process_json_data = BashOperator(
        task_id='process_semi_structured_json',
        bash_command='cd /opt/airflow/project/data_transformation/mfg_dbt_project && dbt run --select stg_mongodb_sensors'
    )

    # STEP 4: CODE MIGRATION (SCD 1, SCD 2, and Materialized Views)
    # UPDATED: Added mv_sensor_health_summary for automated performance tuning
    run_scd_transformations = BashOperator(
        task_id='execute_scd_logic',
        bash_command="""
        cd /opt/airflow/project/data_transformation/mfg_dbt_project && \
        dbt snapshot && \
        dbt run --select rpt_sensor_master mv_sensor_health_summary v_sensor_analytics
        """
    )

    # STEP 5: DATA VALIDATION (RAPID Data Comparator)
    validate_migration = BashOperator(
        task_id='validate_stg_vs_dw_consistency',
        bash_command='python3 /opt/airflow/project/scripts/setup/data_comparator_utility.py'
    )

    # --- PIPELINE DEPENDENCY LOGIC ---
    upload_to_minio >> ingest_batch_to_stg >> process_json_data >> run_scd_transformations >> validate_migration
