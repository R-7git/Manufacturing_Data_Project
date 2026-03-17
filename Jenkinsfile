pipeline {
    agent any

    environment {
        TF_VAR_snowflake_account  = "BKVGNQZ-UO15536"
        TF_VAR_snowflake_user     = "ROSHAN"
        TF_VAR_snowflake_password = credentials('snowflake-user-password')  // secure password

        TF_BIN = "${WORKSPACE}/terraform_bin"
        TF_VERSION = "1.6.6"
    }

    stages {
        stage('Step 0: Setup Terraform') {
            steps {
                sh """
                    mkdir -p ${TF_BIN}
                    echo "--- Downloading Terraform ${TF_VERSION} ---"
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
                        echo "--- Building Snowflake Infrastructure ---"
                        ${TF_BIN}/terraform init
                        ${TF_BIN}/terraform apply -auto-approve
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
            sh "rm -rf ${TF_BIN} || true"
            deleteDir()
        }
    }
}