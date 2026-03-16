# Snowflake Manufacturing Data Platform (Medallion Architecture)

An enterprise-grade, fully automated data platform built to process high-tech manufacturing sensor data. This project implements a **Medallion Architecture** (Bronze, Silver, Gold) using a modern data stack.

## 🏗️ Technical Stack
- **Data Warehouse:** Snowflake (Cloud)
- **Infrastructure as Code:** Terraform
- **Transformation:** dbt (Data Build Tool)
- **Orchestration:** Apache Airflow (Dockerized)
- **Storage:** MinIO (Local S3-compatible Landing Zone)
- **Data Generation:** Python (Faker library)

## 📐 Architecture Overview
1. **Bronze (Raw):** Ingests raw CSV sensor data from an automated landing zone. Materialized as Views.
2. **Silver (Cleaned):** Standardizes metric names, casts data types, and applies business logic (Health Status flags). Materialized as Tables.
3. **Gold (Analytics):** Aggregates sensor performance, peak readings, and critical event counts for Executive Dashboards.

## 🚀 Key Features
- **Idempotent Infrastructure:** Entire Snowflake environment (DBs, Warehouses, Roles) and MinIO buckets are provisioned via **Terraform**.
- **Automated Ingestion:** Custom **dbt Macros** handle the `COPY INTO` logic from internal stages to landing tables.
- **Data Quality:** Integrated **dbt tests** ensure schema integrity and value range validation (Unique, Not Null, Accepted Values).
- **End-to-End Orchestration:** Airflow DAGs manage the full lifecycle: `Generate Data` -> `Ingest` -> `Transform` -> `Test`.

## 🛠️ Local Setup (Mac M2)
1. **Clone the Repo:**
   ```bash
   git clone <your-repo-link>
   cd snowflake-manufacturing-data-platform
