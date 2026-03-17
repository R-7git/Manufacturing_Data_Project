pipeline {
    agent any

    triggers {
        pollSCM('H/5 * * * *')
    }

    environment {
        TF_VAR_snowflake_account = "BKVGNQZ-UO15536"
        SF_CREDS = credentials('snowflake-user')
        AF_CREDS = credentials('airflow-credentials')

        TF_BIN     = "${WORKSPACE}/terraform_bin"
        TF_VERSION = "1.6.6"
        PATH = "${WORKSPACE}/terraform_bin:${env.PATH}"
        AIRFLOW_URL = "http://airflow:8080/api/v1/dags/mfg_enterprise_automated_pipeline/dagRuns"
    }

    stages {
        stage('Step 0: Setup Terraform Binary') {
            steps {
                sh '''
                    set -e
                    mkdir -p "$TF_BIN"
                    echo "--- Downloading Terraform ${TF_VERSION} ---"
                    curl -s -L "https://releases.hashicorp.com{TF_VERSION}/terraform_${TF_VERSION}_linux_amd64.zip" -o terraform.zip
                    unzip -o terraform.zip -d "$TF_BIN"
                    chmod +x "$TF_BIN/terraform"
                    rm -f terraform.zip
                '''
            }
        }

        stage('Step 1: Deploy STG & DW (Terraform)') {
            environment {
                // Mapping the credentials for Terraform variables
                TF_VAR_snowflake_user     = "${SF_CREDS_USR}"
                TF_VAR_snowflake_password = "${SF_CREDS_PSW}"
                // Ensure account is passed from the environment
                TF_VAR_snowflake_account  = "${env.TF_VAR_snowflake_account}"
            }
            steps {
                dir('infrastructure/terraform/snowflake') {
                    sh '''
                        set -e
                        # Force fresh provider download to fix conflicts
                        rm -f .terraform.lock.hcl
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
        always {
            script {
                echo "--- Performing Workspace Housekeeping ---"
                sh "rm -rf ${env.TF_BIN} || true"
                deleteDir()
            }
        }
    }
}
