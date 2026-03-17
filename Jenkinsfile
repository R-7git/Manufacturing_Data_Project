
That **first ``` is illegal in Groovy**, so the pipeline crashes before even starting.

---

# ✅ Fix (IMPORTANT)

👉 **Remove ALL triple backticks (```)** from your Jenkinsfile**

---

# ✅ CLEAN WORKING JENKINSFILE (NO BACKTICKS)

Copy this EXACTLY 👇

:::writing{variant="standard" id="55291"}
pipeline {
    agent any

    triggers {
        pollSCM('* * * * *')
    }

    environment {
        TF_VAR_snowflake_account = "BKVGNQZ-UO15536"

        SF_CREDS = credentials('snowflake-user')
        AF_CREDS = credentials('airflow-credentials')

        TF_BIN     = "${WORKSPACE}/terraform_bin"
        TF_VERSION = "1.6.6"
        PATH       = "${WORKSPACE}/terraform_bin:${env.PATH}"

        AIRFLOW_URL = "http://airflow:8080/api/v1/dags/mfg_enterprise_automated_pipeline/dagRuns"
    }

    stages {

        stage('Step 0: Setup Terraform') {
            steps {
                sh '''
                    set -e
                    mkdir -p "$TF_BIN"

                    curl -s -L "https://releases.hashicorp.com/terraform/${TF_VERSION}/terraform_${TF_VERSION}_linux_amd64.zip" -o terraform.zip

                    unzip -o terraform.zip -d "$TF_BIN"
                    chmod +x "$TF_BIN/terraform"
                    rm -f terraform.zip

                    "$TF_BIN/terraform" -version
                '''
            }
        }

        stage('Step 1: Deploy Snowflake Infrastructure') {
            environment {
                TF_VAR_snowflake_user     = "${SF_CREDS_USR}"
                TF_VAR_snowflake_password = "${SF_CREDS_PSW}"
            }
            steps {
                dir('infrastructure/terraform/snowflake') {
                    sh '''
                        set -e

                        rm -rf .terraform .terraform.lock.hcl

                        terraform init -upgrade -input=false
                        terraform apply -auto-approve -input=false
                    '''
                }
            }
        }

        stage('Step 2: Trigger Airflow Pipeline') {
            steps {
                echo "🚀 Triggering Airflow DAG..."

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

    post {
        always {
            sh "rm -rf ${TF_BIN} || true"
        }
    }
}
