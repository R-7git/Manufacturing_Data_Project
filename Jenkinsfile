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
                sh '''
                    mkdir -p $TF_BIN
                    curl -L https://releases.hashicorp.com{TF_VERSION}/terraform_${TF_VERSION}_linux_amd64.zip -o terraform.zip
                    unzip -o terraform.zip -d $TF_BIN
                    chmod +x $TF_BIN/terraform
                    rm terraform.zip
                '''
            }
        }

        stage('Step 1: Infrastructure (Terraform)') {
            steps {
                dir('infrastructure/terraform/snowflake') {
                    sh '''
                        echo "--- Building Snowflake Infrastructure ---"
                        $TF_BIN/terraform init
                        $TF_BIN/terraform apply -auto-approve
                    '''
                }
            }
        }

        stage('Step 2: Handoff to Airflow') {
            steps {
                echo "--- Handing off to Airflow for dbt and Data Processing ---"
                echo "Terraform is complete. Please trigger the DAG in Airflow UI at http://localhost:8080"
            }
        }
    }

    post {
        success {
            echo "✅ SUCCESS: Infrastructure is ready!"
        }
        always {
            echo "--- Cleaning Workspace ---"
            sh "rm -rf $TF_BIN || true"
            deleteDir()
        }
    }
}
