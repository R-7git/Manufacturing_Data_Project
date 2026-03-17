pipeline {
    agent any

    environment {
        TF_VAR_snowflake_account  = "BKVGNQZ-UO15536"
        TF_VAR_snowflake_user     = "ROSHAN"

        // FIXED: Using env. prefix to avoid Groovy interpolation security warnings
        SNOWFLAKE_PASSWORD        = credentials('snowflake-user-password')
        TF_VAR_snowflake_password = "${env.SNOWFLAKE_PASSWORD}"

        TF_BIN = "${WORKSPACE}/terraform_bin"
        TF_VERSION = "1.6.6"
    }

    stages {
        stage('Step 0: Setup Terraform Binary') {
            steps {
                sh '''
                    echo "--- Downloading Terraform ${TF_VERSION} ---"
                    mkdir -p $TF_BIN
                    curl -L https://releases.hashicorp.com/terraform/${TF_VERSION}/terraform_${TF_VERSION}_linux_amd64.zip -o terraform.zip

                    echo "--- Extracting Terraform ---"
                    # Fallback chain: unzip -> python3 -> jar
                    if command -v unzip >/dev/null; then
                        unzip -o terraform.zip -d $TF_BIN
                    elif command -v python3 >/dev/null; then
                        python3 -m zipfile -e terraform.zip $TF_BIN
                    else
                        echo "ERROR: No extraction tool (unzip/python3) found."
                        exit 1
                    fi

                    chmod +x $TF_BIN/terraform
                    $TF_BIN/terraform version
                    rm terraform.zip
                '''
            }
        }

        stage('Step 1: dbt Setup & Dependencies') {
            steps {
                echo "--- Running dbt via Airflow Container ---"
                sh '''
                    docker exec -u root airflow bash -c "
                        cd /opt/airflow/project/data_transformation/mfg_dbt_project &&
                        dbt clean --profiles-dir . &&
                        dbt deps --profiles-dir .
                    "
                '''
            }
        }

        stage('Step 2: Infrastructure (Terraform)') {
            steps {
                dir('infrastructure/terraform/snowflake') {
                    sh '''
                        echo "--- Provisioning Snowflake Infrastructure ---"
                        $TF_BIN/terraform init
                        $TF_BIN/terraform plan -out=tfplan
                        $TF_BIN/terraform apply -auto-approve tfplan
                    '''
                }
            }
        }

        stage('Step 3: Medallion Transformation') {
            steps {
                echo "--- Running dbt Build ---"
                sh '''
                    docker exec -u root airflow bash -c "
                        cd /opt/airflow/project/data_transformation/mfg_dbt_project &&
                        dbt build --profiles-dir .
                    "
                '''
            }
        }
    }

    post {
        success {
            echo "SUCCESS: Pipeline completed"
            sh 'docker exec airflow airflow dags trigger mfg_enterprise_automated_pipeline || true'
        }
        always {
            echo "--- Cleaning Workspace ---"
            sh "rm -rf $TF_BIN || true"
            // deleteDir() is standard; if it fails, 'sh rm -rf *' is the fallback
            deleteDir() 
        }
    }
}
