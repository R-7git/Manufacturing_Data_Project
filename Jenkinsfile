pipeline {
    agent any

    environment {
        // Infrastructure Details
        TF_VAR_snowflake_account  = "BKVGNQZ-UO15536"
        TF_VAR_snowflake_user     = "ROSHAN"
        
        // Credentials
        SNOWFLAKE_PASSWORD        = credentials('snowflake-user-password')
        TF_VAR_snowflake_password = "${env.SNOWFLAKE_PASSWORD}"

        // Database Discovery from Snowflake Explorer
        SNOWFLAKE_DATABASE        = "MFG_BRONZE_DB"
        SNOWFLAKE_SCHEMA          = "KAFKA_INGEST"
    }

    stages {
        stage('Step 1: dbt Setup & Dependencies') {
            agent {
                docker { 
                    image 'ghcr.io/dbt-labs/dbt-snowflake:1.8.2'
                    reuseNode true 
                }
            }
            steps {
                dir('data_transformation/mfg_dbt_project') {
                    sh '''
                        echo "--- Downloading dbt dependencies ---"
                        dbt deps --profiles-dir .
                        dbt clean --profiles-dir .
                    '''
                }
            }
        }

        stage('Step 2: Infrastructure (Terraform)') {
            agent {
                docker { 
                    image 'hashicorp/terraform:1.6'
                    reuseNode true
                }
            }
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
            agent {
                docker { 
                    image 'ghcr.io/dbt-labs/dbt-snowflake:1.8.2'
                    reuseNode true
                }
            }
            steps {
                dir('data_transformation/mfg_dbt_project') {
                    sh '''
                        echo "--- Running dbt build (Bronze -> Silver -> Gold) ---"
                        dbt build --profiles-dir .
                    '''
                }
            }
        }
    }

    post {
        success {
            echo "✅ SUCCESS: Jenkins Pipeline finished. Triggering Airflow..."
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
