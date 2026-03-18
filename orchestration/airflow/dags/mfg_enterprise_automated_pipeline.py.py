from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.providers.slack.operators.slack_webhook import SlackWebhookOperator
from datetime import datetime, timedelta

# --- SLACK ALERT FUNCTION ---
def send_slack_alert(context):
    slack_msg = f"""
            :red_circle: *PIPELINE FAILURE*
            *Task*: {context.get('task_instance').task_id}
            *Dag*: {context.get('task_instance').dag_id}
            *Log*: <{context.get('task_instance').log_url}|Click here to view log>
            """
    alert = SlackWebhookOperator(
        task_id='slack_failure_notification',
        http_conn_id='slack_conn', # Define this in Airflow UI Admin -> Connections
        message=slack_msg,
        channel='#data-alerts'
    )
    return alert.execute(context=context)

default_args = {
    'owner': 'roshan',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
    'on_failure_callback': send_slack_alert,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    'mfg_enterprise_automated_pipeline',
    default_args=default_args,
    description='Full Enterprise Automated Medallion Pipeline',
    schedule_interval=timedelta(minutes=30), # Runs every 30 mins
    catchup=False,
    tags=['enterprise', 'automation', 'slack'],
) as dag:

    # 1. SENSOR: Wait for CSV files from Docker Producer
    wait_for_files = BashOperator(
        task_id='sense_incoming_csv_files',
        bash_command='ls /opt/airflow/project/mfg_sensor_batch_*.csv'
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

    # 4. DBT TRANSFORMATION (Bronze -> Silver -> Gold)
    run_dbt = BashOperator(
        task_id='dbt_medallion_transformation',
        bash_command="""
        cd /opt/airflow/project/data_transformation/mfg_dbt_project && \
        dbt snapshot && \
        dbt run
        """
    )

    # 5. VALIDATION & ARCHIVE (Final cleanup)
    validate_and_archive = BashOperator(
        task_id='validate_and_cleanup',
        bash_command="""
        python3 /opt/airflow/project/scripts/setup/data_comparator_utility.py && \
        mkdir -p /opt/airflow/project/archive && \
        mv /opt/airflow/project/mfg_sensor_batch_*.csv /opt/airflow/project/archive/
        """
    )

    wait_for_files >> upload_to_lake >> ingest_to_stg >> run_dbt >> validate_and_archive
