pipeline {
    agent any

    environment {
        TF_VAR_snowflake_account  = "BKVGNQZ-UO15536"
        TF_VAR_snowflake_user     = "ROSHAN"
        SNOWFLAKE_PASSWORD        = credentials('snowflake-user-password')
        TF_VAR_snowflake_password = "${env.SNOWFLAKE_PASSWORD}"
        
        // Path for portable terraform
        TF_BIN = "${WORKSPACE}/terraform_bin"
    }

    stages {
        stage('Step 0: Setup Terraform Binary') {
            steps {
                sh '''
                    echo "--- Downloading Portable Terraform ---"
                    mkdir -p $TF_BIN
                    curl -SL https://releases.hashicorp.com -o terraform.zip
                    unzip -o terraform.zip -d $TF_BIN
                    chmod +x $TF_BIN/terraform
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
                        dbt deps --profiles-dir . &&
                        dbt clean --profiles-dir .
                    "
                '''
            }
        }

        stage('Step 2: Infrastructure (Terraform)') {
            steps {
                dir('infrastructure/terraform/snowflake') {
                    sh '''
                        echo "--- Provisioning Snowflake Objects ---"
                        # Use the portable binary we just downloaded
                        $TF_BIN/terraform init
                        $TF_BIN/terraform plan -out=tfplan
                        $TF_BIN/terraform apply -auto-approve tfplan
                    '''
                }
            }
        }

        stage('Step 3: Medallion Transformation') {
            steps {
                echo "--- Running Medallion Build via Airflow Container ---"
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
            echo "✅ SUCCESS: Pipeline finished. Triggering Airflow DAG..."
            sh 'docker exec airflow airflow dags trigger mfg_enterprise_automated_pipeline || true'
        }
        always {
            echo "--- Cleaning Workspace ---"
            sh "rm -rf $TF_BIN"
            deleteDir()
        }
    }
}
