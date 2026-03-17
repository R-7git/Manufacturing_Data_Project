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
        stage('Step 1: Workspace Verification') {
            steps {
                echo "--- Verifying project files are present ---"
                sh 'ls -R data_transformation/mfg_dbt_project'
            }
        }

        stage('Step 2: Infrastructure (Terraform)') {
            steps {
                dir('infrastructure/terraform/snowflake') {
                    sh '''
                        echo "--- Provisioning Snowflake Infrastructure ---"
                        terraform init
                        terraform plan -out=tfplan
                        terraform apply -auto-approve tfplan
                    '''
                }
            }
        }

        stage('Step 3: Trigger Full Data Pipeline') {
            steps {
                echo "--- Handing off to Airflow for dbt Transformations ---"
                // Note: If this shell command fails due to permissions, 
                // you should trigger the DAG manually at http://localhost:8080
                sh 'docker exec airflow airflow dags trigger mfg_enterprise_automated_pipeline || echo "Please trigger Airflow manually at localhost:8080"'
            }
        }
    }

    post {
        success {
            echo "✅ SUCCESS: Infrastructure is ready."
        }
        failure {
            echo "❌ ERROR: Infrastructure setup failed. Check Terraform logs."
        }
        always {
            echo "--- Cleaning Workspace ---"
            deleteDir()
        }
    }
}
