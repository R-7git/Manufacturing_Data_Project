pipeline {
    agent any

    triggers {
        pollSCM('H/5 * * * *')
    }

    environment {
        TF_VAR_snowflake_account  = "BKVGNQZ-UO15536"
        SF_CREDS = credentials('snowflake-user')
        AF_CREDS = credentials('airflow-credentials')
        AIRFLOW_URL = "http://airflow:8080/api/v1/dags/mfg_enterprise_automated_pipeline/dagRuns"
    }

    stages {

        stage('Step 1: Deploy Snowflake Infrastructure') {
            agent {
                docker {
                    image 'hashicorp/terraform:1.6.6'
                    args '-u root'   // avoids permission issues
                }
            }
            environment {
                TF_VAR_snowflake_user     = "${SF_CREDS_USR}"
                TF_VAR_snowflake_password = "${SF_CREDS_PSW}"
            }
            steps {
                dir('infrastructure/terraform/snowflake') {
                    sh """
                        set -e
                        rm -rf .terraform .terraform.lock.hcl
                        terraform init -upgrade -input=false
                        terraform apply -auto-approve -input=false
                    """
                }
            }
        }

        stage('Step 2: Trigger Airflow Pipeline') {
            steps {
                sh """
                    set -e
                    curl -f -X POST "${AIRFLOW_URL}" \
                      -H "Content-Type: application/json" \
                      --user "${AF_CREDS_USR}:${AF_CREDS_PSW}" \
                      -d '{}'
                """
            }
        }
    }

    post {
        always {
            deleteDir()
        }
    }
}