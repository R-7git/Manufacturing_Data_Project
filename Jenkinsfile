pipeline {
    agent any 

    environment {
        TF_VAR_snowflake_account  = "BKVGNQZ-UO15536"
        TF_VAR_snowflake_user     = "ROSHAN"
        // Ensure this ID matches your Jenkins Credentials Manager
        SNOWFLAKE_PASSWORD        = credentials('snowflake-user-password')
        // Industry Standard: Pointing dbt to the workspace profiles directory
        DBT_PROFILES_DIR          = "${WORKSPACE}/data_transformation/mfg_dbt_project"
    }

    stages {
        stage('Step 1: Code Linting & Setup') {
            steps {
                echo "Validating SQL standards..."
                dir('data_transformation/mfg_dbt_project') {
                    sh 'dbt clean --profiles-dir .'
                }
            }
        }

        stage('Step 2: Infrastructure Sync (Terraform)') {
            steps {
                echo "Syncing Snowflake via Terraform..."
                dir('infrastructure/terraform/snowflake') {
                    sh 'terraform init'
                    sh 'terraform apply -auto-approve'
                }
            }
        }

        stage('Step 3: Data Transformation (dbt Build)') {
            steps {
                echo "Building Medallion Layers and Running Tests..."
                dir('data_transformation/mfg_dbt_project') {
                    sh 'dbt deps --profiles-dir .'
                    sh 'dbt build --profiles-dir .' 
                }
            }
        }

        stage('Step 4: Observability (Documentation)') {
            steps {
                echo "Generating updated Lineage Graphs..."
                dir('data_transformation/mfg_dbt_project') {
                    sh 'dbt docs generate --profiles-dir .'
                }
            }
        }
    }

    post {
        success {
            echo "✅ SUCCESS: Snowflake Platform is Live!"
            echo "Triggering Airflow DAG for Data Ingestion..."
            // INDUSTRY STANDARD: Triggering the Airflow Orchestrator via the Docker Exec bridge
            sh 'docker exec airflow airflow dags trigger mfg_enterprise_automated_pipeline'
        }
        failure {
            echo "❌ ERROR: Pipeline failed. Check dbt logs for data quality violations."
        }
    }
}
