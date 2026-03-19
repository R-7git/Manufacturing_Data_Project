from airflow import DAG
from airflow.sensors.filesystem import FileSensor
from airflow.operators.bash import BashOperator
from airflow.providers.snowflake.operators.snowflake import SnowflakeOperator
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

    # 1. NEW: Ensure Snowflake Infrastructure exists (Fixes "DB does not exist" error)
    setup_snowflake_infra = SnowflakeOperator(
        task_id='setup_snowflake_infrastructure',
        sql="""
            CREATE DATABASE IF NOT EXISTS MFG_BRONZE_DB;
            CREATE SCHEMA IF NOT EXISTS MFG_BRONZE_DB.KAFKA_INGEST;
            CREATE WAREHOUSE IF NOT EXISTS INGEST_WH WITH WAREHOUSE_SIZE='XSMALL' AUTO_SUSPEND=60;
        """,
        snowflake_conn_id='snowflake_default'
    )

    # 2. SENSOR: Look in landing_zone for Parquet files
    wait_for_files = FileSensor(
        task_id='sense_incoming_files',
        filepath='/opt/airflow/project/landing_zone/mfg_sensor_batch_*.parquet',
        fs_conn_id='fs_default',
        poke_interval=60,
        timeout=600,
        mode='poke'
    )

    # 3. UPLOAD TO MINIO (Data Lake)
    upload_to_lake = BashOperator(
        task_id='upload_to_minio_lake',
        bash_command='python3 /opt/airflow/project/scripts/setup/minio_data_uploader.py'
    )

    # 4. CONNECTOR HEALTH CHECK: Ensure Kafka Sink isn't crashed (Fixes "Fake Green" status)
    check_connector_status = BashOperator(
        task_id='check_kafka_connector_health',
        bash_command="""
        STATUS=$(curl -s localhost:8083/connectors/mfg_snowflake_sink/status | jq -r '.tasks[0].state');
        if [ "$STATUS" != "RUNNING" ]; then
            echo "Connector is $STATUS. Failing task.";
            exit 1;
        fi
        """
    )

    # 5. INGESTION TO STAGING
    ingest_to_stg = BashOperator(
        task_id='snowflake_copy_ingestion',
        bash_command="""
        cd /opt/airflow/project/data_transformation/mfg_dbt_project && \
        dbt run-operation load_internal_stage --args "{stage_name: 'MINIO_RAW_STAGE', table_name: 'STG_SENSOR_DATA'}"
        """
    )

    # 6. DBT TRANSFORMATION (Medallion: Bronze -> Silver -> Gold)
    run_dbt = BashOperator(
        task_id='dbt_medallion_transformation',
        bash_command="""
        cd /opt/airflow/project/data_transformation/mfg_dbt_project && \
        dbt snapshot && dbt run
        """
    )

    # 7. VALIDATION & ARCHIVE
    validate_and_archive = BashOperator(
        task_id='validate_and_cleanup',
        bash_command="""
        python3 /opt/airflow/project/scripts/setup/data_comparator_utility.py && \
        mkdir -p /opt/airflow/project/archive && \
        mv /opt/airflow/project/landing_zone/mfg_sensor_batch_*.parquet /opt/airflow/project/archive/
        """
    )

    # Dependency Graph
    setup_snowflake_infra >> wait_for_files >> upload_to_lake >> check_connector_status >> ingest_to_stg >> run_dbt >> validate_and_archive
