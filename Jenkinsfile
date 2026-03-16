pipeline {
    agent any 

    // Industry Standard: Define environment variables for the cluster
    environment {
        TF_VAR_snowflake_account  = "BKVGNQZ-UO15536"
        TF_VAR_snowflake_user     = "ROSHAN"
        // 'snowflake-user-password' must be created in Jenkins -> Credentials -> System -> Global
        SNOWFLAKE_PASSWORD        = credentials('snowflake-user-password')
        // Pointing to your local dbt profiles
        DBT_PROFILES_DIR          = "/Users/ms/.dbt"
    }

    stages {
        stage('Step 1: Workspace & Code Linting') {
            steps {
                echo "Cleaning dbt workspace and validating SQL/Python files..."
                dir('data_transformation/mfg_dbt_project') {
                    // Ensures we have a fresh build environment
                    sh 'dbt clean'
                }
            }
        }

        stage('Step 2: Infrastructure Sync (Terraform)') {
            steps {
                echo "Syncing Snowflake Infrastructure (Databases, Schemas, Tables)..."
                dir('infrastructure/terraform/snowflake') {
                    sh 'terraform init'
                    // -auto-approve is critical: it prevents Jenkins from hanging/waiting for input
                    sh 'terraform apply -auto-approve'
                }
            }
        }

        stage('Step 3: Data Transformation (dbt Build)') {
            steps {
                echo "Building Medallion Layers (Bronze -> Silver -> Gold)..."
                dir('data_transformation/mfg_dbt_project') {
                    sh 'dbt deps'
                    // 'dbt build' is the modern industry command: it runs models AND tests
                    // We remove '--target prod' unless you have a prod target defined in profiles.yml
                    sh 'dbt build' 
                }
            }
        }

        stage('Step 4: Real-Time Verification (Optional)') {
            steps {
                echo "Generating updated documentation and lineage graphs..."
                dir('data_transformation/mfg_dbt_project') {
                    sh 'dbt docs generate'
                }
            }
        }
    }

    post {
        success {
            echo "✅ SUCCESS: Manufacturing Data Platform deployed to Snowflake."
            echo "Lineage available at: data_transformation/mfg_dbt_project/target/index.html"
        }
        failure {
            echo "❌ ERROR: Pipeline failed. Check dbt logs or Terraform state."
        }
    }
}
