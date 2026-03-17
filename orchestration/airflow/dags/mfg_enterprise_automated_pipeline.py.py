from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta

# Industry Standard: Setting robust default arguments
default_args = {
    'owner': 'roshan',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
    'email_on_failure': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    'mfg_enterprise_automated_pipeline',
    default_args=default_args,
    description='Automated Enterprise Migration: STG to DW with SCD & Performance Views',
    schedule_interval='@hourly',
    catchup=False,
    tags=['migration', 'snowflake', 'automation', 'scd', 'json'],
) as dag:

    # 1. DATA LAKE LANDING (Source -> MinIO Lake)
    # Industry Standard: First move data to the object store (S3/MinIO)
    upload_to_lake = BashOperator(
        task_id='upload_source_to_datalake',
        bash_command='python3 /opt/airflow/project/scripts/setup/minio_data_uploader.py'
    )

    # 2. BATCH INGESTION (MinIO -> Snowflake STG_DB)
    # Uses the Snowflake COPY command to move data from the External Stage to the STG table
    ingest_to_stg = BashOperator(
        task_id='ingest_batch_to_staging',
        bash_command="""
        cd /opt/airflow/project/data_transformation/mfg_dbt_project && \
        dbt run-operation load_internal_stage --args "{stage_name: 'MINIO_RAW_STAGE', table_name: 'STG_SENSOR_DATA'}"
        """
    )

    # 3. CODE MIGRATION (Bronze View, JSON Flattening, SCD 1, SCD 2, & Performance MVs)
    # This step executes the full Medallion transformation in the correct sequence
    run_migration_logic = BashOperator(
        task_id='execute_migration_and_scd_logic',
        bash_command="""
        cd /opt/airflow/project/data_transformation/mfg_dbt_project && \
        dbt snapshot && \
        dbt run --select bronze_sensor_data stg_mongodb_sensors rpt_sensor_master mv_sensor_health_summary v_sensor_analytics
        """
    )

    # 4. RAPID DATA VALIDATION (Source vs Target Integrity)
    # Compares row counts in STG_DB vs DW_DB to ensure no data loss during migration
    validate_migration = BashOperator(
        task_id='validate_stg_vs_dw_consistency',
        bash_command='python3 /opt/airflow/project/scripts/setup/data_comparator_utility.py'
    )

    # --- PIPELINE FLOW ---
    upload_to_lake >> ingest_to_stg >> run_migration_logic >> validate_migration
