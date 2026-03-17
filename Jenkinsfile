pipeline {
    agent any

    environment {
        // Snowflake Connection Details
        TF_VAR_snowflake_account  = "BKVGNQZ-UO15536"
        TF_VAR_snowflake_user     = "ROSHAN"
        
        // Credentials from Jenkins
        SNOWFLAKE_PASSWORD        = credentials('snowflake-user-password')
        TF_VAR_snowflake_password = "${SNOWFLAKE_PASSWORD}"

        // Corrected Database/Schema from our discovery
        SNOWFLAKE_DATABASE        = "MFG_BRONZE_DB"
        SNOWFLAKE_SCHEMA          = "KAFKA_INGEST"

        // dbt Paths
        DBT_PROFILES_DIR          = "${WORKSPACE}/data_transformation/mfg_dbt_project"
        DBT_VENV                  = "${WORKSPACE}/data_transformation/mfg_dbt_project/venv"
    }

    stages {
        stage('Step 1: Setup Environment & Install dbt') {
            steps {
                dir('data_transformation/mfg_dbt_project') {
                    sh '''
                        echo "--- Initializing Python Virtual Env ---"
                        python3 -m venv venv
                        
                        echo "--- Installing dbt-snowflake ---"
                        venv/bin/pip install --upgrade pip
                        venv/bin/pip install dbt-snowflake
                        
                        echo "--- Verifying Installation ---"
                        venv/bin/dbt --version
                        
                        echo "--- Cleaning & Installing Deps ---"
                        venv/bin/dbt clean --profiles-dir .
                        venv/bin/dbt deps --profiles-dir .
                    '''
                }
            }
        }

        stage('Step 2: Infrastructure Provisioning (Terraform)') {
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
                        echo "--- Building dbt Models ---"
                        ${DBT_VENV}/bin/dbt build --profiles-dir .
                    '''
                }
            }
        }

        stage('Step 4: Data Tests') {
            steps {
                dir('data_transformation/mfg_dbt_project') {
                    sh '''
                        echo "--- Running Data Quality Tests ---"
                        ${DBT_VENV}/bin/dbt test --profiles-dir .
                    '''
                }
            }
        }

        stage('Step 5: Documentation & Observability') {
            steps {
                dir('data_transformation/mfg_dbt_project') {
                    sh '''
                        echo "--- Generating Docs ---"
                        ${DBT_VENV}/bin/dbt docs generate --profiles-dir .
                    '''
                }
            }
        }
    }

    post {
        success {
            echo "✅ SUCCESS: Triggering Airflow DAG..."
            // Ensure Docker permissions are set for the Jenkins user
            sh 'docker exec airflow airflow dags trigger mfg_enterprise_automated_pipeline'
        }

        failure {
            echo "❌ ERROR: Pipeline failed. Archiving logs..."
            archiveArtifacts artifacts: 'data_transformation/mfg_dbt_project/logs/*.log', allowEmptyArchive: true
        }

        always {
            echo "Cleaning Jenkins workspace..."
            cleanWs()
        }
    }
}
