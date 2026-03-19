from airflow import DAG
from airflow.sensors.filesystem import FileSensor
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from airflow.providers.slack.operators.slack_webhook import SlackWebhookOperator
import requests
from datetime import datetime, timedelta

def send_slack_alert(context):
    slack_msg = f":red_circle: *PIPELINE FAILURE*\n*Task*: {context.get('task_instance').task_id}"
    alert = SlackWebhookOperator(
        task_id='slack_failure_notification',
        slack_webhook_conn_id='slack_conn',  # Fixed argument name
        message=slack_msg,
        channel='#data-alerts'
    )
    return alert.execute(context=context)

# New Python-based health check (No jq required)
def check_kafka_status():
    try:
        response = requests.get("http://localhost:8083/connectors/mfg_snowflake_sink/status")
        response.raise_for_status()
        data = response.json()
        # Accessing the state of the first task
        status = data['tasks'][0]['state']
        if status != "RUNNING":
            raise ValueError(f"Connector task is in {status} state!")
        print(f"Connector is healthy and RUNNING.")
    except Exception as e:
        print(f"Health check failed: {str(e)}")
        raise

default_args = {
    'owner': 'roshan',
    'start_date': datetime(2024, 1, 1),
    'on_failure_callback': send_slack_alert,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    'mfg_enterprise_automated_pipeline',
    default_args=default_args,
    schedule_interval=timedelta(minutes=30),
    catchup=False,
) as dag:

    # 1. SENSOR
    wait_for_files = FileSensor(
        task_id='sense_incoming_files',
        filepath='/opt/airflow/project/landing_zone/mfg_sensor_batch_*.parquet',
        fs_conn_id='fs_default',
        poke_interval=60,
        timeout=600,
        mode='poke'
    )

    # 2. UPLOAD TO MINIO
    upload_to_lake = BashOperator(
        task_id='upload_to_minio_lake',
        bash_command='python3 /opt/airflow/project/scripts/setup/minio_data_uploader.py'
    )

    # 3. HEALTH CHECK (Now using Python Operator to avoid 'jq' requirement)
    check_connector_status = PythonOperator(
        task_id='check_kafka_connector_health',
        python_callable=check_kafka_status
    )

    # 4. INGESTION TO STAGING
    ingest_to_stg = BashOperator(
        task_id='snowflake_copy_ingestion',
        bash_command="""
        cd /opt/airflow/project/data_transformation/mfg_dbt_project && \
        dbt run-operation load_internal_stage --args "{stage_name: 'MINIO_RAW_STAGE', table_name: 'STG_SENSOR_DATA'}"
        """
    )

    # 5. DBT TRANSFORMATION
    run_dbt = BashOperator(
        task_id='dbt_medallion_transformation',
        bash_command="""
        cd /opt/airflow/project/data_transformation/mfg_dbt_project && \
        dbt snapshot && dbt run
        """
    )

    # 6. VALIDATION & ARCHIVE
    validate_and_archive = BashOperator(
        task_id='validate_and_cleanup',
        bash_command="""
        python3 /opt/airflow/project/scripts/setup/data_comparator_utility.py && \
        mkdir -p /opt/airflow/project/archive && \
        mv /opt/airflow/project/landing_zone/mfg_sensor_batch_*.parquet /opt/airflow/project/archive/
        """
    )

    wait_for_files >> upload_to_lake >> check_connector_status >> ingest_to_stg >> run_dbt >> validate_and_archive
