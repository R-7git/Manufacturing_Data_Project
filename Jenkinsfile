pipeline {
    agent any

    environment {
        TF_VAR_snowflake_account  = "BKVGNQZ-UO15536"
        TF_VAR_snowflake_user     = "ROSHAN"
        SNOWFLAKE_PASSWORD        = credentials('snowflake-user-password')
        TF_VAR_snowflake_password = "${env.SNOWFLAKE_PASSWORD}"
        
        TF_BIN = "${WORKSPACE}/terraform_bin"
        TF_VERSION = "1.6.6"
    }

    stages {
        stage('Step 0: Setup Terraform') {
            steps {
                sh """
                    mkdir -p ${env.TF_BIN}
                    echo "--- Downloading Terraform ${env.TF_VERSION} ---"
                    curl -L https://releases.hashicorp.com{env.TF_VERSION}/terraform_${env.TF_VERSION}_linux_amd64.zip -o terraform.zip
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
                        echo "--- Building Snowflake Infrastructure ---"
                        ${env.TF_BIN}/terraform init
                        ${env.TF_BIN}/terraform apply -auto-approve
                    """
                }
            }
        }

        stage('Step 2: Handoff to Airflow') {
            steps {
                echo "✅ Terraform complete. Please trigger the DAG in Airflow UI at http://localhost:8080"
            }
        }
    }

    post {
        success {
            echo "SUCCESS: Infrastructure is ready!"
        }
        always {
            echo "--- Cleaning Workspace ---"
            sh "rm -rf ${env.TF_BIN} || true"
            deleteDir()
        }
    }
}
