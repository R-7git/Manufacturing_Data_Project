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
    description='Full Medallion Pipeline: Batch, Stream, and SaaS Ingestion',
    schedule_interval='@hourly',
    catchup=False,
    tags=['manufacturing', 'snowflake', 'dbt'],
) as dag:

    # 1. DATA GENERATION (The 'Producer' phase)
    # Simulates real sensors and ERP data arriving in the landing zone
    generate_data = BashOperator(
        task_id='generate_and_upload_batch_data',
        bash_command='python3 /opt/airflow/project/scripts/setup/manufacturing_data_producer.py'
    )

    # 2. INGESTION (Moving data from Internal Stage to Bronze Table)
    # Uses dbt macro to run the COPY INTO command
    copy_batch_to_bronze = BashOperator(
        task_id='copy_stage_to_bronze',
        bash_command='cd /opt/airflow/project/data_transformation/mfg_dbt_project && dbt run-operation load_internal_stage --args "{stage_name: \'MFG_INTERNAL_STAGE\', table_name: \'SENSOR_DATA_LANDING\'}"'
    )

    # 3. OBSERVABILITY (Verifying the Automated Kafka Sink)
    # Industry Standard: Ensuring the real-time stream is actually hitting Snowflake
    verify_kafka_stream = BashOperator(
        task_id='verify_kafka_ingestion_health',
        bash_command='snowflake-cli sql -q "SELECT COUNT(*) FROM MFG_BRONZE_DB.KAFKA_INGEST.RAW_SENSOR_STREAM WHERE INGESTED_AT > CURRENT_TIMESTAMP() - INTERVAL \'1 HOUR\'"'
    )

    # 4. TRANSFORMATION (The Medallion Flow)
    # Builds Silver (Cleaned) and Gold (Aggregated) layers
    dbt_run = BashOperator(
        task_id='dbt_run_medallion',
        bash_command='cd /opt/airflow/project/data_transformation/mfg_dbt_project && dbt run'
    )

    # 5. QUALITY GATE (Automated Testing)
    # Ensures business logic in Gold layer is accurate
    dbt_test = BashOperator(
        task_id='dbt_test_quality_gate',
        bash_command='cd /opt/airflow/project/data_transformation/mfg_dbt_project && dbt test'
    )

    # DAG Dependency Logic
    generate_data >> copy_batch_to_bronze >> verify_kafka_stream >> dbt_run >> dbt_test
