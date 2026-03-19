import os
import glob
import socket  # Added to check environment
from minio import Minio
from minio.error import S3Error

# --- CONFIGURATION ---
# Check if we are running inside Docker or on the local Mac
try:
    # If this resolves, we are inside the Docker network
    socket.gethostbyname('minio')
    MINIO_URL = "minio:9000"
except socket.gaierror:
    # If it fails, we are running locally on the Mac
    MINIO_URL = "localhost:9000"

ACCESS_KEY = "admin"
SECRET_KEY = "password123"

# Professional Migration Layers
RAW_BUCKET = "raw"
CURATED_BUCKET = "curated"

def upload_to_datalake():
    client = Minio(
        MINIO_URL,
        access_key=ACCESS_KEY,
        secret_key=SECRET_KEY,
        secure=False
    )
    
    # --- IMPORTANT: Fix the path for Mac vs Docker ---
    # Inside Docker it's /opt/airflow/project/landing_zone
    # On Mac it's the relative landing_zone folder
    if os.path.exists("/opt/airflow/project/landing_zone"):
        landing_path = "/opt/airflow/project/landing_zone"
    else:
        # Fallback to local path relative to where you run the script
        landing_path = "./landing_zone" 

    try:
        # 1. ENSURE LAYERS EXIST
        for bucket in [RAW_BUCKET, CURATED_BUCKET]:
            if not client.bucket_exists(bucket):
                client.make_bucket(bucket)
                print(f"📁 Created layer: {bucket}")

        # 2. ROUTE RAW DATA (CSVs)
        csv_files = glob.glob(f"{landing_path}/*.csv")
        for local_file in csv_files:
            file_name = os.path.basename(local_file)
            client.fput_object(RAW_BUCKET, file_name, local_file)
            print(f"📦 RAW: Uploaded {file_name}")

        # 3. ROUTE CURATED DATA (Parquet)
        parquet_files = glob.glob(f"{landing_path}/*.parquet")
        for local_file in parquet_files:
            file_name = os.path.basename(local_file)
            client.fput_object(CURATED_BUCKET, file_name, local_file)
            print(f"💎 CURATED: Uploaded {file_name}")

    except S3Error as err:
        print(f"❌ MinIO Error: {err}")

if __name__ == "__main__":
    upload_to_datalake()
