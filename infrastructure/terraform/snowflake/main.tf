terraform {
  required_providers {
    snowflake = {
      # Updated source to the official registry
      source  = "snowflakedb/snowflake"
      version = "0.87.0"
    }
  }
}

provider "snowflake" {
  account  = "BKVGNQZ-UO15536"
  user     = "ROSHAN"
  password = "Rosh20090798395@"
  role     = "ACCOUNTADMIN" 
}

# --- 1. DATABASES ---
resource "snowflake_database" "stg_db" { name = "STG_DB" }
resource "snowflake_database" "dw_db"  { name = "DW_DB" }

# --- 2. SCHEMAS ---
resource "snowflake_schema" "stg_schema" {
  database = snowflake_database.stg_db.name
  name     = "STG_SCHEMA"
}
resource "snowflake_schema" "rpt_schema" {
  database = snowflake_database.dw_db.name
  name     = "RPT_SCHEMA"
}

# --- 3. EXTERNAL STAGE (MinIO S3-Compatible) ---
resource "snowflake_stage" "minio_stage" {
  name     = "MINIO_RAW_STAGE"
  database = snowflake_database.stg_db.name
  schema   = snowflake_schema.stg_schema.name
  url      = "s3://manufacturing-landing-zone/"
  credentials = "AWS_KEY_ID='admin' AWS_SECRET_KEY='password123'"
  # REMOVED: endpoint = "http://minio:9000" (Unsupported in this resource)
}

# --- 4. STAGING TABLE ---
resource "snowflake_table" "stg_sensor_data" {
  database = snowflake_database.stg_db.name
  schema   = snowflake_schema.stg_schema.name
  name     = "STG_SENSOR_DATA"

  column { name = "SENSOR_ID"; type = "VARCHAR(16777216)" }
  column { name = "METRIC_NAME"; type = "VARCHAR(16777216)" }
  column { name = "METRIC_VALUE"; type = "FLOAT" }
  column { name = "INGESTION_TIMESTAMP"; type = "TIMESTAMP_NTZ(9)" }
  column { name = "METADATA_FILENAME"; type = "VARCHAR(16777216)" }
}

# --- 5. THE STREAM ---
resource "snowflake_stream" "sensor_stream" {
  database = snowflake_database.stg_db.name
  schema   = snowflake_schema.stg_schema.name
  name     = "SENSOR_DATA_STREAM"
  on_table = "${snowflake_database.stg_db.name}.${snowflake_schema.stg_schema.name}.${snowflake_table.stg_sensor_data.name}"
  append_only = false 
  depends_on = [snowflake_table.stg_sensor_data]
}

# --- 6. TARGET TABLE ---
resource "snowflake_table" "dw_sensor_master" {
  database = snowflake_database.dw_db.name
  schema   = snowflake_schema.rpt_schema.name
  name     = "DW_SENSOR_MASTER"

  column { name = "SENSOR_ID"; type = "VARCHAR"; nullable = false }
  column { name = "METRIC_NAME"; type = "VARCHAR" }
  column { name = "METRIC_VALUE"; type = "FLOAT" }
  column { name = "LAST_UPDATED_AT"; type = "TIMESTAMP_NTZ" }
}

# --- 7. WAREHOUSE ---
resource "snowflake_warehouse" "mfg_wh" {
  name           = "MFG_WH"
  warehouse_size = "X-SMALL"
  auto_suspend   = 60
}
