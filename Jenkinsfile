pipeline {
    agent any

    triggers {
        pollSCM('* * * * *')
    }

    environment {
        TF_VAR_snowflake_account = "BKVGNQZ-UO15536"
        SF_CREDS = credentials('snowflake-user')   // Snowflake Credentials
        AF_CREDS = credentials('airflow-credentials')  // Airflow Credentials

        TF_BIN     = "${WORKSPACE}/terraform_bin"
        TF_VERSION = "1.6.6"
        PATH = "${WORKSPACE}/terraform_bin:${env.PATH}"
        AIRFLOW_URL = "http://airflow:8080/api/v1/dags/mfg_enterprise_automated_pipeline/dagRuns"
    }

    stages {
        stage('Step 0.1: Emergency Git Cleanup') {
            steps {
                sh 'rm -f .git/index.lock || true'  // Ensure the lock file is removed if exists
            }
        }

        stage('Step 0.2: Setup Terraform Binary') {
            steps {
                sh '''
                    set -e
                    mkdir -p "$TF_BIN"
                    
                    # Download Terraform with the correct version
                    echo "--- Downloading Terraform ${TF_VERSION} ---"
                    curl -s -L "https://releases.hashicorp.com/terraform/${TF_VERSION}/terraform_${TF_VERSION}_linux_amd64.zip" -o terraform.zip
                    
                    # Unzip and setup the binary
                    unzip -o terraform.zip -d "$TF_BIN"
                    chmod +x "$TF_BIN/terraform"
                    rm -f terraform.zip
                    terraform -version  # Check the version
                '''
            }
        }

        stage('Step 1: Deploy STG & DW (Terraform)') {
            environment {
                TF_VAR_snowflake_user     = "${SF_CREDS_USR}"
                TF_VAR_snowflake_password = "${SF_CREDS_PSW}"
            }
            steps {
                dir('infrastructure/terraform/snowflake') {
                    sh '''
                        set -e
                        terraform init -input=false
                        terraform apply -auto-approve -input=false
                    '''
                }
            }
        }

        stage('Step 2: Trigger Airflow DAG') {
            steps {
                script {
                    echo "🚀 Triggering Airflow Migration Pipeline..."
                    sh '''
                        set -e
                        curl -f -X POST "$AIRFLOW_URL" \
                          -H "Content-Type: application/json" \
                          --user "$AF_CREDS_USR:$AF_CREDS_PSW" \
                          -d '{}'
                    '''
                }
            }
        }
    }

    post {
        success {
            echo "✅ SUCCESS: Infrastructure live and Airflow processing!"
        }
        failure {
            echo "❌ FAILURE: URL error or Authentication issue. Check console."
        }
        always {
            script {
                echo "--- Performing Workspace Housekeeping ---"
                sh "rm -rf ${env.TF_BIN} || true"
                deleteDir()  // Clean up the workspace
            }
        }
    }
}