pipeline {
agent any

```
environment {
    // Snowflake Terraform Provider Variables
    TF_VAR_snowflake_account  = "BKVGNQZ-UO15536"
    TF_VAR_snowflake_user     = "ROSHAN"

    // Jenkins Credential
    SNOWFLAKE_PASSWORD        = credentials('snowflake-user-password')
    TF_VAR_snowflake_password = "${SNOWFLAKE_PASSWORD}"

    // dbt variables
    DBT_PROFILES_DIR          = "${WORKSPACE}/data_transformation/mfg_dbt_project"
    DBT_VENV                  = "${WORKSPACE}/data_transformation/mfg_dbt_project/venv"
}

stages {

    stage('Step 1: Setup Environment & Install dbt') {
        steps {
            dir('data_transformation/mfg_dbt_project') {
                sh '''
                    echo "Creating Python virtual environment..."

                    python3 -m venv venv

                    echo "Upgrading pip..."
                    venv/bin/pip install --upgrade pip

                    echo "Installing dbt-snowflake..."
                    venv/bin/pip install --cache-dir .pip-cache dbt-snowflake

                    echo "Checking dbt version..."
                    venv/bin/dbt --version

                    echo "Cleaning previous dbt artifacts..."
                    venv/bin/dbt clean --profiles-dir .

                    echo "Installing dbt dependencies..."
                    venv/bin/dbt deps --profiles-dir .
                '''
            }
        }
    }

    stage('Step 2: Infrastructure Provisioning (Terraform)') {
        steps {
            dir('infrastructure/terraform/snowflake') {
                sh '''
                    echo "Checking Terraform version..."
                    terraform --version

                    echo "Initializing Terraform..."
                    terraform init

                    echo "Running Terraform Plan..."
                    terraform plan -out=tfplan

                    echo "Applying Terraform Infrastructure..."
                    terraform apply -auto-approve tfplan
                '''
            }
        }
    }

    stage('Step 3: Data Transformation (dbt Build)') {
        steps {
            dir('data_transformation/mfg_dbt_project') {
                sh '''
                    echo "Running dbt build..."

                    venv/bin/dbt build --profiles-dir .
                '''
            }
        }
    }

    stage('Step 4: Data Tests') {
        steps {
            dir('data_transformation/mfg_dbt_project') {
                sh '''
                    echo "Running dbt tests..."

                    venv/bin/dbt test --profiles-dir .
                '''
            }
        }
    }

    stage('Step 5: Documentation & Observability') {
        steps {
            dir('data_transformation/mfg_dbt_project') {
                sh '''
                    echo "Generating dbt documentation..."

                    venv/bin/dbt docs generate --profiles-dir .
                '''
            }
        }
    }
}

post {

    success {
        echo "SUCCESS: Pipeline completed successfully. Triggering Airflow DAG..."

        sh '''
            docker exec airflow airflow dags trigger mfg_enterprise_automated_pipeline
        '''
    }

    failure {
        echo "ERROR: Pipeline failed. Archiving logs..."

        archiveArtifacts artifacts: 'data_transformation/mfg_dbt_project/logs/*.log', allowEmptyArchive: true
    }

    always {
        echo "Cleaning Jenkins workspace..."

        cleanWs()
    }
}
```

}
