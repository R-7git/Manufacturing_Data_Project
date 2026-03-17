pipeline {
    agent any

    // FIX 1: Add this triggers block so Jenkins knows to poll GitHub
    triggers {
        pollSCM('* * * * *') 
    }

    environment {
        TF_VAR_snowflake_account  = "BKVGNQZ-UO15536"
        TF_VAR_snowflake_user     = "ROSHAN"
        // Ensure 'snowflake-user-password' and 'airflow-credentials' exist in Jenkins Credentials
        TF_VAR_snowflake_password = credentials('snowflake-user-password') 
        AIRFLOW_AUTH              = credentials('airflow-credentials') // Format: admin:password123

        TF_BIN = "${WORKSPACE}/terraform_bin"
        TF_VERSION = "1.6.6"
        
        // Update this to your Docker host IP if 'localhost' fails inside the Jenkins container
        AIRFLOW_URL = "http://airflow:8080/api/v1/dags/mfg_enterprise_automated_pipeline/dagRuns"
    }

    stages {
        stage('Step 0: Setup Terraform') {
            steps {
                sh """
                    mkdir -p ${TF_BIN}
                    curl -L https://releases.hashicorp.com/terraform/${TF_VERSION}/terraform_${TF_VERSION}_linux_amd64.zip -o terraform.zip
                    unzip -o terraform.zip -d ${TF_BIN}
                    chmod +x ${TF_BIN}/terraform
                    rm terraform.zip
                """
            }
        }

        stage('Step 1: Infrastructure (Terraform)') {
            steps {
                dir('infrastructure/terraform/snowflake') {
                    sh """
                        ${TF_BIN}/terraform init
                        ${TF_BIN}/terraform apply -auto-approve
                    """
                }
            }
        }

        // FIX 2: Replaced the 'echo' with an actual API trigger
        stage('Step 2: Trigger Airflow DAG') {
            steps {
                script {
                    echo "🚀 Triggering Airflow DAG..."
                    sh """
                        curl -X POST "${AIRFLOW_URL}" \
                        -H "Content-Type: application/json" \
                        --user "${AIRFLOW_AUTH}" \
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
            sh "rm -rf ${TF_BIN} || true"
            deleteDir()
        }
    }
}
