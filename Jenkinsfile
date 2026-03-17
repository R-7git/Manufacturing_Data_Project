pipeline {
    // This agent covers the entire pipeline, including the post-actions
    agent any

    triggers {
        pollSCM('* * * * *') 
    }

    environment {
        TF_VAR_snowflake_account  = "BKVGNQZ-UO15536"
        TF_VAR_snowflake_user     = "ROSHAN"
        
        // These IDs MUST exist in Jenkins -> Manage Jenkins -> Credentials
        TF_VAR_snowflake_password = credentials('snowflake-user-password') 
        AIRFLOW_AUTH              = credentials('airflow-credentials') 

        TF_BIN = "${WORKSPACE}/terraform_bin"
        TF_VERSION = "1.6.6"
        
        // Internal Docker network URL for Airflow
        AIRFLOW_URL = "http://airflow:8080/api/v1/dags/mfg_enterprise_automated_pipeline/dagRuns"
    }

    stages {
        stage('Step 0: Setup Terraform') {
            steps {
                sh """
                    mkdir -p ${env.TF_BIN}
                    curl -L https://releases.hashicorp.com/terraform/${env.TF_VERSION}/terraform_${env.TF_VERSION}_linux_amd64.zip -o terraform.zip
                    unzip -o terraform.zip -d ${env.TF_BIN}
                    chmod +x ${env.TF_BIN}/terraform
                    rm terraform.zip
                """
            }
        }

        stage('Step 1: Infrastructure (Terraform)') {
            steps {
                dir('infrastructure/terraform/snowflake') {
                    sh """
                        ${env.TF_BIN}/terraform init
                        ${env.TF_BIN}/terraform apply -auto-approve
                    """
                }
            }
        }

        stage('Step 2: Trigger Airflow DAG') {
            steps {
                script {
                    echo "🚀 Triggering Airflow DAG..."
                    // Added -f to curl to ensure Jenkins marks this as failure if the API call fails
                    sh """
                        curl -f -X POST "${env.AIRFLOW_URL}" \
                        -H "Content-Type: application/json" \
                        --user "${env.AIRFLOW_AUTH}" \
                        -d '{}'
                    """
                }
            }
        }
    }

    post {
        success {
            echo "✅ SUCCESS: Infrastructure deployed and DAG triggered!"
        }
        failure {
            echo "❌ FAILURE: Check the logs above for Terraform or API errors."
        }
        always {
            // FIX: Removed 'node(any)' which was causing the hang.
            // Using 'script' block instead to handle housekeeping.
            script {
                echo "--- Cleaning Workspace ---"
                sh "rm -rf ${env.TF_BIN} || true"
                deleteDir()
            }
        }
    }
}
