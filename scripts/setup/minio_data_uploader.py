import os
import glob
import socket
from minio import Minio
from minio.error import S3Error

# --- CONFIGURATION ---
try:
    socket.gethostbyname('minio')
    MINIO_URL = "minio:9000"
except socket.gaierror:
    MINIO_URL = "localhost:9000"

ACCESS_KEY = "admin"
SECRET_KEY = "password123"

RAW_BUCKET = "raw"
CURATED_BUCKET = "curated"

def upload_to_datalake():
    client = Minio(MINIO_URL, access_key=ACCESS_KEY, secret_key=SECRET_KEY, secure=False)
    
    if os.path.exists("/opt/airflow/project/landing_zone"):
        landing_path = "/opt/airflow/project/landing_zone"
    else:
        landing_path = "./landing_zone" 

    try:
        # 1. ENSURE BUCKETS EXIST
        for bucket in [RAW_BUCKET, CURATED_BUCKET]:
            if not client.bucket_exists(bucket):
                client.make_bucket(bucket)
                print(f"📁 Created: {bucket}")

        # 2. ROUTE PARQUET DATA TO BOTH LAYERS
        parquet_files = glob.glob(f"{landing_path}/*.parquet")
        for local_file in parquet_files:
            file_name = os.path.basename(local_file)
            
            # Upload to RAW (The Landing Copy)
            client.fput_object(RAW_BUCKET, file_name, local_file)
            print(f"📦 RAW: Uploaded {file_name}")
            
            # Upload to CURATED (The Processed Copy)
            client.fput_object(CURATED_BUCKET, file_name, local_file)
            print(f"💎 CURATED: Uploaded {file_name}")

    except S3Error as err:
        print(f"❌ MinIO Error: {err}")

if __name__ == "__main__":
    upload_to_datalake()
