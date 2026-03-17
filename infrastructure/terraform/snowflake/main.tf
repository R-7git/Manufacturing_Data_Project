terraform {
  required_providers {
    snowflake = {
      source  = "snowflake-labs/snowflake"
      version = "0.87.0"
    }
    minio = {
      source  = "aminueza/minio"
      version = "3.3.0"
    }
  }
}

# --- PROVIDER CONFIGS ---

provider "snowflake" {
  account  = "BKVGNQZ-UO15536"
  user     = "ROSHAN"
  password = "Rosh20090798395@"
  role     = "ACCOUNTADMIN" # Boss role to perform grants
}

provider "minio" {
  minio_server   = "minio:9000"
  minio_user     = "admin"
  minio_password = "password123"
  minio_ssl      = false
}

# --- 1. DATABASES ---
resource "snowflake_database" "bronze" { name = "MFG_BRONZE_DB" }
resource "snowflake_database" "silver" { name = "MFG_SILVER_DB" }
resource "snowflake_database" "gold"   { name = "MFG_GOLD_DB" }

# --- 2. WAREHOUSES ---
resource "snowflake_warehouse" "ingest_wh" {
  name           = "INGEST_WH"
  warehouse_size = "X-SMALL"
  auto_suspend   = 60
}

resource "snowflake_warehouse" "dbt_wh" {
  name           = "DBT_TRANSFORM_WH"
  warehouse_size = "X-SMALL"
  auto_suspend   = 60
}

# --- 3. SCHEMAS ---
resource "snowflake_schema" "bronze_raw" { 
  database = snowflake_database.bronze.name
  name     = "RAW_DATA" 
}
resource "snowflake_schema" "silver_stg" { 
  database = snowflake_database.silver.name
  name     = "STAGING_CLEANED" 
}
resource "snowflake_schema" "gold_marts" { 
  database = snowflake_database.gold.name
  name     = "DATA_MARTS" 
}
resource "snowflake_schema" "external_stages" { 
  database = snowflake_database.bronze.name
  name     = "EXTERNAL_STAGES" 
}
resource "snowflake_schema" "kafka_ingest" {
  database = snowflake_database.bronze.name
  name     = "KAFKA_INGEST"
}

# --- 4. PERMISSIONS (The Fix for Task 4) ---
# Grant SYSADMIN permission to use and create objects in these schemas
resource "snowflake_schema_grant" "grants" {
  for_each = {
    "raw"    = snowflake_schema.bronze_raw.name,
    "stg"    = snowflake_schema.silver_stg.name,
    "marts"  = snowflake_schema.gold_marts.name,
    "kafka"  = snowflake_schema.kafka_ingest.name,
    "stages" = snowflake_schema.external_stages.name
  }

  database_name = snowflake_database.bronze.name # Update if silver/gold are separate DBs
  schema_name   = each.value
  privilege     = "ALL PRIVILEGES" # Gives USAGE, CREATE TABLE, CREATE VIEW, etc.
  roles         = ["SYSADMIN"]
}

# --- 5. BATCH LANDING TABLE ---
resource "snowflake_table" "sensor_landing" {
  database = snowflake_database.bronze.name
  schema   = snowflake_schema.bronze_raw.name
  name     = "SENSOR_DATA_LANDING"

  column { name = "SENSOR_ID"; type = "VARCHAR(16777216)" }
  column { name = "METRIC_NAME"; type = "VARCHAR(16777216)" }
  column { name = "METRIC_VALUE"; type = "FLOAT" }
  column { name = "INGESTION_TIMESTAMP"; type = "TIMESTAMP_NTZ(9)" }
}

# --- 6. INTERNAL STAGE ---
resource "snowflake_stage" "mfg_internal_landing" {
  name     = "MFG_INTERNAL_STAGE"
  database = snowflake_database.bronze.name
  schema   = snowflake_schema.external_stages.name
}

# --- 7. KAFKA STREAMING TABLE ---
resource "snowflake_table" "raw_sensor_stream" {
  database = snowflake_database.bronze.name
  schema   = snowflake_schema.kafka_ingest.name
  name     = "RAW_SENSOR_STREAM"

  column { name = "RECORD_CONTENT"; type = "VARIANT" }
  column { name = "RECORD_METADATA"; type = "VARIANT" }
  column { 
    name = "INGESTED_AT"
    type = "TIMESTAMP_NTZ(9)"
    default { expression = "CURRENT_TIMESTAMP()" }
  }
}

# --- 8. MINIO BUCKET ---
resource "minio_s3_bucket" "landing_bucket" {
  bucket = "manufacturing-landing-zone"
  acl    = "public"
}
