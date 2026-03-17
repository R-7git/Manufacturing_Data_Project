pipeline {
    agent any

    environment {
        // Snowflake Connection Details
        TF_VAR_snowflake_account  = "BKVGNQZ-UO15536"
        TF_VAR_snowflake_user     = "ROSHAN"
        
        // Credentials from Jenkins
        SNOWFLAKE_PASSWORD        = credentials('snowflake-user-password')
        TF_VAR_snowflake_password = "${SNOWFLAKE_PASSWORD}"

        // The exact Database/Schema we found in your Snowflake Explorer
        SNOWFLAKE_DATABASE        = "MFG_BRONZE_DB"
        SNOWFLAKE_SCHEMA          = "KAFKA_INGEST"

        // dbt Pathing
        DBT_PROJECT_DIR           = "${WORKSPACE}/data_transformation/mfg_dbt_project"
        DBT_VENV                  = "${WORKSPACE}/data_transformation/mfg_dbt_project/venv"
    }

    stages {
        stage('Step 1: Setup Environment & Install dbt') {
            steps {
                dir('data_transformation/mfg_dbt_project') {
                    sh '''
                        echo "--- Creating Virtual Environment ---"
                        python3 -m venv venv
                        
                        echo "--- Installing dbt-snowflake ---"
                        venv/bin/pip install --upgrade pip
                        venv/bin/pip install dbt-snowflake
                        
                        echo "--- Cleaning and Loading Dependencies ---"
                        # We call the exact path to dbt inside the venv
                        venv/bin/dbt clean --profiles-dir .
                        venv/bin/dbt deps --profiles-dir .
                    '''
                }
            }
        }

        stage('Step 2: Infrastructure (Terraform)') {
            steps {
                dir('infrastructure/terraform/snowflake') {
                    sh '''
                        terraform init
                        terraform plan -out=tfplan
                        terraform apply -auto-approve tfplan
                    '''
                }
            }
        }

        stage('Step 3: Data Transformation (dbt Build)') {
            steps {
                dir('data_transformation/mfg_dbt_project') {
                    sh '''
                        echo "--- Running dbt build using venv ---"
                        venv/bin/dbt build --profiles-dir .
                    '''
                }
            }
        }

        stage('Step 4: Data Quality Tests') {
            steps {
                dir('data_transformation/mfg_dbt_project') {
                    sh '''
                        venv/bin/dbt test --profiles-dir .
                    '''
                }
            }
        }
    }

    post {
        success {
            echo "✅ SUCCESS: Jenkins finished. Triggering Airflow..."
            sh 'docker exec airflow airflow dags trigger mfg_enterprise_automated_pipeline'
        }
        failure {
            echo "❌ ERROR: Jenkins Pipeline failed."
            archiveArtifacts artifacts: 'data_transformation/mfg_dbt_project/logs/*.log', allowEmptyArchive: true
        }
        always {
            cleanWs()
        }
    }
}


