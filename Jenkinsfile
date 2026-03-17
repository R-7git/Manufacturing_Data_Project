pipeline {
    agent any

    environment {
        // Infrastructure Details
        TF_VAR_snowflake_account  = "BKVGNQZ-UO15536"
        TF_VAR_snowflake_user     = "ROSHAN"
        
        // Credentials
        SNOWFLAKE_PASSWORD        = credentials('snowflake-user-password')
        TF_VAR_snowflake_password = "${env.SNOWFLAKE_PASSWORD}"

        // Database/Schema Discovery
        SNOWFLAKE_DATABASE        = "MFG_BRONZE_DB"
        SNOWFLAKE_SCHEMA          = "KAFKA_INGEST"
    }

    stages {
        stage('Step 1: dbt Setup & Dependencies') {
            steps {
                echo "--- Running dbt deps via Airflow Container ---"
                // Using docker exec to bypass Jenkins-local permission issues
                sh '''
                    docker exec -u root airflow bash -c "
                        cd /opt/airflow/project/data_transformation/mfg_dbt_project && 
                        dbt deps --profiles-dir . &&
                        dbt clean --profiles-dir .
                    "
                '''
            }
        }

        stage('Step 2: Infrastructure (Terraform)') {
            steps {
                dir('infrastructure/terraform/snowflake') {
                    sh '''
                        echo "--- Provisioning Snowflake Objects ---"
                        terraform init
                        terraform plan -out=tfplan
                        terraform apply -auto-approve tfplan
                    '''
                }
            }
        }

        stage('Step 3: Medallion Transformation') {
            steps {
                echo "--- Running Medallion Build via Airflow Container ---"
                sh '''
                    docker exec -u root airflow bash -c "
                        cd /opt/airflow/project/data_transformation/mfg_dbt_project && 
                        dbt build --profiles-dir .
                    "
                '''
            }
        }
    }

    post {
        success {
            echo "✅ SUCCESS: Jenkins Pipeline finished. Triggering Airflow DAG..."
            sh 'docker exec airflow airflow dags trigger mfg_enterprise_automated_pipeline || true'
        }
        failure {
            echo "❌ ERROR: Pipeline failed. Check dbt or Terraform logs."
        }
        always {
            echo "--- Cleaning Workspace ---"
            deleteDir()
        }
    }
}
