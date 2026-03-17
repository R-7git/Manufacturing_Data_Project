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
    description='Full Medallion Pipeline with Automated Kafka Verification',
    schedule_interval='@hourly',
    catchup=False,
    tags=['manufacturing', 'snowflake', 'dbt', 'kafka'],
) as dag:

    # 1. BATCH DATA GENERATION
    generate_data = BashOperator(
        task_id='generate_and_upload_batch_data',
        bash_command='python3 /opt/airflow/project/scripts/setup/manufacturing_data_producer.py'
    )

    # 2. BATCH INGESTION (Copy Into Bronze)
    # Database and Schema are now handled by dbt environment variables
    copy_batch_to_bronze = BashOperator(
        task_id='copy_stage_to_bronze',
        bash_command="""
        cd /opt/airflow/project/data_transformation/mfg_dbt_project && \
        dbt run-operation load_internal_stage --args "{stage_name: 'MFG_INTERNAL_STAGE', table_name: 'SENSOR_DATA_LANDING'}" --profiles-dir .
        """
    )

    # 3. STREAM OBSERVABILITY (The dbt Fix)
    # Simplified table name to prevent double-prefixing
    verify_kafka_stream = BashOperator(
        task_id='verify_kafka_ingestion_health',
        bash_command="""
        cd /opt/airflow/project/data_transformation/mfg_dbt_project && \
        dbt run-operation test_stream_arrival --args "{table_name: 'RAW_SENSOR_STREAM'}" --profiles-dir .
        """
    )

    # 4. MEDALLION TRANSFORMATION
    dbt_run = BashOperator(
        task_id='dbt_run_medallion',
        bash_command='cd /opt/airflow/project/data_transformation/mfg_dbt_project && dbt run --profiles-dir .'
    )

    # 5. QUALITY GATE
    dbt_test = BashOperator(
        task_id='dbt_test_quality_gate',
        bash_command='cd /opt/airflow/project/data_transformation/mfg_dbt_project && dbt test --profiles-dir .'
    )

    # DAG Dependency Logic
    generate_data >> copy_batch_to_bronze >> verify_kafka_stream >> dbt_run >> dbt_test
