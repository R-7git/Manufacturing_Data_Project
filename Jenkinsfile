pipeline {
    agent any

    triggers {
        // Industry Standard: Poll GitHub every 5 minutes for changes
        pollSCM('* * * * *')
    }

    environment {
        // 1. Snowflake Account ID
        TF_VAR_snowflake_account = "BKVGNQZ-UO15536"

        // 2. Secure Credentials from Jenkins UI
        SF_CREDS = credentials('snowflake-user')
        AF_CREDS = credentials('airflow-credentials')

        // 3. Terraform setup
        TF_BIN     = "${WORKSPACE}/terraform_bin"
        TF_VERSION = "1.6.6"

        // Update PATH so the 'terraform' command works in all subsequent stages
        PATH = "${WORKSPACE}/terraform_bin:${env.PATH}"

        // 4. Airflow API endpoint (Internal Docker network)
        AIRFLOW_URL = "http://airflow:8080/api/v1/dags/mfg_enterprise_automated_pipeline/dagRuns"
    }

    stages {
        stage('Step 0: Setup Terraform Binary') {
            steps {
                sh '''
                    set -e
                    mkdir -p "$TF_BIN"
                    
                    echo "--- Downloading Terraform ${TF_VERSION} ---"
                    # Corrected URL syntax for Hashicorp releases
                    curl -s -L "https://releases.hashicorp.com/terraform/${TF_VERSION}/terraform_${TF_VERSION}_linux_amd64.zip" -o terraform.zip
                    
                    unzip -o terraform.zip -d "$TF_BIN"
                    chmod +x "$TF_BIN/terraform"
                    rm -f terraform.zip

                    echo "--- Terraform Version Check ---"
                    terraform -version
                '''
            }
        }

        stage('Step 1: Deploy STG & DW (Terraform)') {
            environment {
                // Pass Jenkins credentials into Terraform environment variables
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
                        # Call Airflow API with Basic Auth using credentials from Jenkins
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
            echo "✅ SUCCESS: Infrastructure for STG_DB/DW_DB is live and Airflow is processing data."
        }
        failure {
            echo "❌ FAILURE: Check Terraform download, Jenkins credentials, or Airflow API connectivity."
        }
        always {
            script {
                echo "--- Performing Workspace Housekeeping ---"
                // Clean the binary folder using the environment variable
                sh "rm -rf ${env.TF_BIN} || true"
                deleteDir()
            }
        }
    }
}
