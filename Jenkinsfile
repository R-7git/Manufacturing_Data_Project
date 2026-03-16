pipeline {
    agent any 

    environment {
        TF_VAR_snowflake_account  = "BKVGNQZ-UO15536"
        TF_VAR_snowflake_user     = "ROSHAN"
        SNOWFLAKE_PASSWORD        = credentials('snowflake-user-password')
        DBT_PROFILES_DIR          = "${WORKSPACE}/data_transformation/mfg_dbt_project"
    }

    stages {
        stage('Step 1: Code Linting & Setup') {
            steps {
                echo "Setting up Python environment and validating SQL..."
                dir('data_transformation/mfg_dbt_project') {
                    sh '''
                        python3 -m venv venv
                        . venv/bin/activate
                        pip install --upgrade pip
                        pip install dbt-snowflake
                        dbt clean --profiles-dir .
                    '''
                }
            }
        }

        stage('Step 2: Infrastructure Sync (Terraform)') {
            steps {
                echo "Syncing Snowflake via Terraform..."
                dir('infrastructure/terraform/snowflake') {
                    sh 'terraform init'
                    sh 'terraform apply -auto-approve'
                }
            }
        }

        stage('Step 3: Data Transformation (dbt Build)') {
            steps {
                echo "Building Medallion Layers and Running Tests..."
                dir('data_transformation/mfg_dbt_project') {
                    // Re-activate the venv created in Step 1
                    sh '''
                        . venv/bin/activate
                        dbt deps --profiles-dir .
                        dbt build --profiles-dir .
                    '''
                }
            }
        }

        stage('Step 4: Observability (Documentation)') {
            steps {
                echo "Generating updated Lineage Graphs..."
                dir('data_transformation/mfg_dbt_project') {
                    sh '''
                        . venv/bin/activate
                        dbt docs generate --profiles-dir .
                    '''
                }
            }
        }
    }

    post {
        success {
            echo "✅ SUCCESS: Snowflake Platform is Live!"
            echo "Triggering Airflow DAG for Data Ingestion..."
            sh 'docker exec airflow airflow dags trigger mfg_enterprise_automated_pipeline'
        }
        failure {
            echo "❌ ERROR: Pipeline failed. Check dbt logs for data quality violations."
        }
    }
}
