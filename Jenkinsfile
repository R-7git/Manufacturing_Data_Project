pipeline {
    agent any

    // Triggers Jenkins to check GitHub for changes every minute
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
        
        // Uses the Docker service name 'airflow' to communicate internally
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
                // script block used to handle the API call logic
                script {
                    echo "🚀 Triggering Airflow DAG..."
                    sh """
                        curl -X POST "${env.AIRFLOW_URL}" \
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
        always {
            echo "--- Cleaning Workspace ---"
            // FIX: Use env.TF_BIN to ensure the post-condition can find the variable
            sh "rm -rf ${env.TF_BIN} || true"
            deleteDir()
        }
    }
}
