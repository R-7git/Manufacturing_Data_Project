pipeline {
    agent any 

    environment {
        TF_VAR_snowflake_account  = "BKVGNQZ-UO15536"
        TF_VAR_snowflake_user     = "ROSHAN"
        TF_VAR_snowflake_password  = credentials('snowflake-user-password')
        SNOWFLAKE_PASSWORD        = credentials('snowflake-user-password')
        DBT_PROFILES_DIR          = "${WORKSPACE}/data_transformation/mfg_dbt_project"
    }

    stages {
        stage('Step 1: Setup & Linting') {
            steps {
                dir('data_transformation/mfg_dbt_project') {
                    sh '''
                        python3 -m venv venv
                        . venv/bin/activate
                        pip install --upgrade pip dbt-snowflake
                        dbt clean
                        dbt deps
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
            sh 'docker exec airflow airflow dags trigger mfg_enterprise_automated_pipeline'
        }
        failure {
            echo "❌ ERROR: Pipeline failed. Archiving logs..."
            archiveArtifacts artifacts: 'data_transformation/mfg_dbt_project/logs/*.log', allowEmptyArchive: true
        }
        always {
            cleanWs()
        }
    }
}
