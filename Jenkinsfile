pipeline {
    agent any 

    environment {
        // Terraform Snowflake Provider vars
        TF_VAR_snowflake_account  = "BKVGNQZ-UO15536"
        TF_VAR_snowflake_user     = "ROSHAN"
        // Jenkins Credentials
        SNOWFLAKE_PASSWORD        = credentials('snowflake-user-password')
        TF_VAR_snowflake_password = "${SNOWFLAKE_PASSWORD}"
        
        // dbt specific vars
        DBT_PROFILES_DIR          = "${WORKSPACE}/data_transformation/mfg_dbt_project"
    }

    stages {
        stage('Step 1: Setup & Linting') {
            steps {
                dir('data_transformation/mfg_dbt_project') {
                    sh '''
                        python3 -m venv venv
                        . venv/bin/activate
                        pip install --upgrade pip
                        pip install dbt-snowflake
                        dbt --version
                        dbt clean --profiles-dir .
                        dbt deps --profiles-dir .
                    '''
                }
            }
        }

        stage('Step 2: Infrastructure (Terraform)') {
            steps {
                dir('infrastructure/terraform/snowflake') {
                    sh '''
                        terraform --version
                        terraform init
                        terraform plan -out=tfplan
                        terraform apply -auto-approve tfplan
                    '''
                }
            }
        }

        stage('Step 3: Transformation (dbt Build)') {
            steps {
                dir('data_transformation/mfg_dbt_project') {
                    sh '''
                        . venv/bin/activate
                        dbt build --profiles-dir .
                    '''
                }
            }
        }

        stage('Step 4: Observability') {
            steps {
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
            echo "✅ SUCCESS: Triggering Airflow DAG..."
            // Ensure the Jenkins user has permission to run docker exec
            sh 'docker exec airflow airflow dags trigger mfg_enterprise_automated_pipeline'
        }
        failure {
            echo "❌ ERROR: Pipeline failed. Archiving logs..."
            archiveArtifacts artifacts: 'data_transformation/mfg_dbt_project/logs/*.log', allowEmptyArchive: true
        }
        always {
            // Optional: comment out cleanWs() if you need to debug files on the agent
            cleanWs()
        }
    }
}
