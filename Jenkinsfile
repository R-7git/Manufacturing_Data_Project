pipeline {
    agent any

    environment {
        TF_VAR_snowflake_account  = "BKVGNQZ-UO15536"
        TF_VAR_snowflake_user     = "ROSHAN"
        
        // Securely handle credentials
        SNOWFLAKE_PASSWORD        = credentials('snowflake-user-password')
        TF_VAR_snowflake_password = "${env.SNOWFLAKE_PASSWORD}"

        SNOWFLAKE_DATABASE        = "MFG_BRONZE_DB"
        SNOWFLAKE_SCHEMA          = "KAFKA_INGEST"
    }

    stages {
        stage('Step 1: dbt Setup') {
            agent {
                docker { 
                    image 'ghcr.io/dbt-labs/dbt-snowflake:1.8.2'
                    // This allows the container to see the files Jenkins cloned
                    reuseNode true 
                }
            }
            steps {
                dir('data_transformation/mfg_dbt_project') {
                    sh '''
                        dbt clean --profiles-dir .
                        dbt deps --profiles-dir .
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
                        terraform init
                        terraform plan -out=tfplan
                        terraform apply -auto-approve tfplan
                    '''
                }
            }
        }

        stage('Step 3: Data Transformation (dbt Build)') {
            agent {
                docker { 
                    image 'ghcr.io/dbt-labs/dbt-snowflake:1.8.2'
                    reuseNode true
                }
            }
            steps {
                dir('data_transformation/mfg_dbt_project') {
                    sh 'dbt build --profiles-dir .'
                }
            }
        }
    }

    post {
        success {
            echo "✅ SUCCESS: Pipeline completed."
            // This triggers your Airflow DAG
            sh 'docker exec airflow airflow dags trigger mfg_enterprise_automated_pipeline || true'
        }
        always {
            echo "Cleaning workspace..."
            // deleteDir() is the standard method since you don't have the cleanWs plugin
            deleteDir()
        }
    }
}
