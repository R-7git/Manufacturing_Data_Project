terraform {
  required_providers {
    snowflake = {
      source  = "snowflakedb/snowflake"
      version = "~> 0.86.0"
    }
  }
}

# ---------------- VARIABLES ----------------
variable "snowflake_account"  { type = string }
variable "snowflake_user"     { type = string }
variable "snowflake_password" {
  type      = string
  sensitive = true
}

# ---------------- PROVIDER ----------------
provider "snowflake" {
  account  = var.snowflake_account
  user     = var.snowflake_user
  password = var.snowflake_password
  role     = "ACCOUNTADMIN"
}

# ---------------- 1. BRONZE INFRA (KAFKA LANDING) ----------------

resource "snowflake_database" "mfg_bronze_db" {
  name    = "MFG_BRONZE_DB"
  comment = "Landing zone for raw Kafka ingestion"
}

resource "snowflake_schema" "kafka_ingest" {
  database = snowflake_database.mfg_bronze_db.name
  name     = "KAFKA_INGEST"
}

resource "snowflake_table" "manufacturing_data" {
  database = snowflake_database.mfg_bronze_db.name
  schema   = snowflake_schema.kafka_ingest.name
  name     = "MANUFACTURING_DATA"

  column {
    name = "RECORD_METADATA"
    type = "VARIANT"
  }

  column {
    name = "RECORD_CONTENT"
    type = "VARIANT"
  }
}

resource "snowflake_warehouse" "ingest_wh" {
  name           = "INGEST_WH"
  warehouse_size = "XSMALL"
  auto_suspend   = 60
  auto_resume    = true
}

# ---------------- 2. EXISTING DATABASES (Managed via DBT) ----------------

resource "snowflake_database" "stg_db" {
  name = "STG_DB"
  lifecycle { ignore_changes = all }
}

resource "snowflake_database" "dw_db" {
  name = "DW_DB"
  lifecycle { ignore_changes = all }
}

# ---------------- 3. SCHEMAS ----------------

resource "snowflake_schema" "stg_schema" {
  database = snowflake_database.stg_db.name
  name     = "STG_SCHEMA"
  lifecycle { ignore_changes = all }
}

resource "snowflake_schema" "rpt_schema" {
  database = snowflake_database.dw_db.name
  name     = "RPT_SCHEMA"
  lifecycle { ignore_changes = all }
}

# ---------------- 4. STORAGE & STAGING ----------------

resource "snowflake_stage" "minio_stage" {
  name     = "MINIO_RAW_STAGE"
  database = snowflake_database.stg_db.name
  schema   = snowflake_schema.stg_schema.name
  lifecycle { ignore_changes = all }
}

resource "snowflake_table" "stg_sensor_data" {
  database = snowflake_database.stg_db.name
  schema   = snowflake_schema.stg_schema.name
  name     = "STG_SENSOR_DATA"

  column {
    name = "SENSOR_ID"
    type = "VARCHAR"
  }
  column {
    name = "METRIC_NAME"
    type = "VARCHAR"
  }
  column {
    name = "METRIC_VALUE"
    type = "FLOAT"
  }
  column {
    name = "INGESTION_TIMESTAMP"
    type = "TIMESTAMP_NTZ"
  }
  column {
    name = "METADATA_FILENAME"
    type = "VARCHAR"
  }

  lifecycle { ignore_changes = all }
}

# ---------------- 5. DATA WAREHOUSE LAYER ----------------

resource "snowflake_table" "dw_sensor_master" {
  database = snowflake_database.dw_db.name
  schema   = snowflake_schema.rpt_schema.name
  name     = "DW_SENSOR_MASTER"

  column {
    name     = "SENSOR_ID"
    type     = "VARCHAR"
    nullable = false
  }
  column {
    name = "METRIC_NAME"
    type = "VARCHAR"
  }
  column {
    name = "METRIC_VALUE"
    type = "FLOAT"
  }
  column {
    name = "LAST_UPDATED_AT"
    type = "TIMESTAMP_NTZ"
  }

  lifecycle { ignore_changes = all }
}

# ---------------- 6. WAREHOUSES ----------------

resource "snowflake_warehouse" "mfg_wh" {
  name           = "MFG_WH"
  warehouse_size = "XSMALL"
  auto_suspend   = 60
  auto_resume    = true
  lifecycle { ignore_changes = all }
}
