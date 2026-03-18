from airflow import DAG
from airflow.sensors.filesystem import FileSensor
from airflow.operators.bash import BashOperator
from airflow.providers.slack.operators.slack_webhook import SlackWebhookOperator
from datetime import datetime, timedelta

def send_slack_alert(context):
    slack_msg = f":red_circle: *PIPELINE FAILURE*\n*Task*: {context.get('task_instance').task_id}"
    alert = SlackWebhookOperator(
        task_id='slack_failure_notification',
        http_conn_id='slack_conn',
        message=slack_msg,
        channel='#data-alerts'
    )
    return alert.execute(context=context)

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

    # 1. SENSOR: Wait for CSV files (Instead of failing, it will 'poke' every 60s)
    wait_for_files = FileSensor(
        task_id='sense_incoming_csv_files',
        filepath='mfg_sensor_batch_*.csv',
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

    # 3. INGESTION TO SNOWFLAKE
    ingest_to_stg = BashOperator(
        task_id='snowflake_copy_ingestion',
        bash_command="""
        cd /opt/airflow/project/data_transformation/mfg_dbt_project && \
        dbt run-operation load_internal_stage --args "{stage_name: 'MINIO_RAW_STAGE', table_name: 'STG_SENSOR_DATA'}"
        """
    )

    # 4. DBT TRANSFORMATION
    run_dbt = BashOperator(
        task_id='dbt_medallion_transformation',
        bash_command="""
        cd /opt/airflow/project/data_transformation/mfg_dbt_project && \
        dbt snapshot && dbt run
        """
    )

    # 5. VALIDATION & ARCHIVE
    validate_and_archive = BashOperator(
        task_id='validate_and_cleanup',
        bash_command="""
        python3 /opt/airflow/project/scripts/setup/data_comparator_utility.py && \
        mkdir -p /opt/airflow/project/archive && \
        mv /opt/airflow/project/mfg_sensor_batch_*.csv /opt/airflow/project/archive/
        """
    )

    wait_for_files >> upload_to_lake >> ingest_to_stg >> run_dbt >> validate_and_archive
