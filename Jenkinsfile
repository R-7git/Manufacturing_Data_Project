pipeline {
    agent any 

    environment {
        TF_VAR_snowflake_account  = "BKVGNQZ-UO15536"
        TF_VAR_snowflake_user     = "ROSHAN"
        // Credentials stored in Jenkins -> Credentials -> 'snowflake-user-password'
        SNOWFLAKE_PASSWORD        = credentials('snowflake-user-password')
        
        /* 
           INDUSTRY FIX: Point dbt to look for profiles.yml 
           INSIDE the project folder instead of a local Mac path.
        */
        DBT_PROFILES_DIR          = "${WORKSPACE}/data_transformation/mfg_dbt_project"
    }

    stages {
        stage('Step 1: Workspace & Code Linting') {
            steps {
                echo "Cleaning dbt workspace..."
                dir('data_transformation/mfg_dbt_project') {
                    // Force dbt to use the local profiles directory
                    sh 'dbt clean --profiles-dir .'
                }
            }
        }

        stage('Step 2: Infrastructure Sync (Terraform)') {
            steps {
                echo "Syncing Snowflake Infrastructure via Terraform..."
                dir('infrastructure/terraform/snowflake') {
                    sh 'terraform init'
                    sh 'terraform apply -auto-approve'
                }
            }
        }

        stage('Step 3: Data Transformation (dbt Build)') {
            steps {
                echo "Building Medallion Layers (Bronze -> Silver -> Gold)..."
                dir('data_transformation/mfg_dbt_project') {
                    sh 'dbt deps --profiles-dir .'
                    // 'dbt build' runs both transformations and data quality tests
                    sh 'dbt build --profiles-dir .' 
                }
            }
        }

        stage('Step 4: Documentation') {
            steps {
                echo "Generating updated lineage docs..."
                dir('data_transformation/mfg_dbt_project') {
                    sh 'dbt docs generate --profiles-dir .'
                }
            }
        }
    }

    post {
        success {
            echo "✅ SUCCESS: Manufacturing Data Platform deployed to Snowflake."
        }
        failure {
            echo "❌ ERROR: Pipeline failed. Check logs for schema violations."
        }
    }
}
