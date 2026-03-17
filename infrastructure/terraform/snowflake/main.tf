terraform {
  required_providers {
    snowflake = {
      source  = "snowflakedb/snowflake"
      version = "~> 0.87.0"
    }
  }
}

# ---------------- VARIABLES ----------------
variable "snowflake_account" {
  type = string
}

variable "snowflake_user" {
  type = string
}

variable "snowflake_password" {
  type      = string
  sensitive = true
}

# ---------------- PROVIDER ----------------
provider "snowflake" {
  # Use the concatenated ORG-ACCOUNT format for this version
  account  = var.snowflake_account
  user     = var.snowflake_user
  password = var.snowflake_password
  role     = "ACCOUNTADMIN"
}

# ---------------- DATABASES ----------------
resource "snowflake_database" "stg_db" {
  name = "STG_DB"
}

resource "snowflake_database" "dw_db" {
  name = "DW_DB"
}

# ---------------- SCHEMAS ----------------
resource "snowflake_schema" "stg_schema" {
  database = snowflake_database.stg_db.name
  name     = "STG_SCHEMA"
}

resource "snowflake_schema" "rpt_schema" {
  database = snowflake_database.dw_db.name
  name     = "RPT_SCHEMA"
}

# ---------------- EXTERNAL STAGE ----------------
resource "snowflake_stage" "minio_stage" {
  name     = "MINIO_RAW_STAGE"
  database = snowflake_database.stg_db.name
  schema   = snowflake_schema.stg_schema.name
  url      = "s3://manufacturing-landing-zone/"

  # Fixed: Single credentials string
  credentials = "AWS_KEY_ID='admin' AWS_SECRET_KEY='password123'"
}

# ---------------- STAGING TABLE ----------------
resource "snowflake_table" "stg_sensor_data" {
  database = snowflake_database.stg_db.name
  schema   = snowflake_schema.stg_schema.name
  name     = "STG_SENSOR_DATA"

  # Fixed: Removed semicolons and separated arguments onto new lines
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
}

# ---------------- STREAM ----------------
resource "snowflake_stream" "sensor_stream" {
  database    = snowflake_database.stg_db.name
  schema      = snowflake_schema.stg_schema.name
  name        = "SENSOR_DATA_STREAM"
  on_table    = snowflake_table.stg_sensor_data.name
  append_only = false
}

# ---------------- DW TABLE ----------------
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
}

# ---------------- WAREHOUSE ----------------
resource "snowflake_warehouse" "mfg_wh" {
  name           = "MFG_WH"
  warehouse_size = "X-SMALL"
  auto_suspend   = 60
  auto_resume    = true
}
