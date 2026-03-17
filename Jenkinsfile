pipeline {
    agent any

    triggers {
        pollSCM('H/5 * * * *')
    }

    environment {
        TF_VAR_snowflake_organization = "BKVGNQZ" 
        TF_VAR_snowflake_account      = "UO15536"
        
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

                    echo "Downloading Terraform ${TF_VERSION}..."

                    # ✅ FINAL FIXED URL
                    curl -s -L "https://releases.hashicorp.com/terraform/${TF_VERSION}/terraform_${TF_VERSION}_linux_amd64.zip" -o terraform.zip

                    unzip -o terraform.zip -d "$TF_BIN"
                    chmod +x "$TF_BIN/terraform"
                    rm -f terraform.zip

                    "$TF_BIN/terraform" -version
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
                        rm -rf .terraform .terraform.lock.hcl

                        "$TF_BIN/terraform" init -upgrade -input=false
                        "$TF_BIN/terraform" apply -auto-approve -input=false
                    '''
                }
            }
        }

        stage('Step 2: Trigger Airflow DAG') {
            steps {
                script {
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
                sh "rm -rf ${env.TF_BIN} || true"
                deleteDir()
            }
        }
    }
}