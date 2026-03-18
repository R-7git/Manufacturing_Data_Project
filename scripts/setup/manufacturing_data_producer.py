import pandas as pd
import os
import random
from faker import Faker
from datetime import datetime

# Initialize Faker
fake = Faker()

def generate_sensor_data(num_rows=100):
    """Generates fake manufacturing sensor data."""
    data = []
    for _ in range(num_rows):
        data.append({
            "sensor_id": f"SENSOR_{random.randint(100, 999)}",
            "temperature": round(random.uniform(20.0, 100.0), 2),
            "vibration": round(random.uniform(0.1, 5.0), 4),
            "pressure": round(random.uniform(900, 1100), 2),
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
    return pd.DataFrame(data)

def client_utility_process(file_path):
    """Simulates splitting large files and converting CSV to Parquet."""
    if not os.path.exists(file_path):
        print(f"❌ Error: {file_path} not found!")
        return None
        
    df = pd.read_csv(file_path)
    df['processed_at'] = pd.Timestamp.now()
    
    parquet_path = file_path.replace(".csv", ".parquet")
    df.to_parquet(parquet_path, index=False)
    
    print(f"✅ Utility: Converted {file_path} to {parquet_path}")
    return parquet_path

if __name__ == "__main__":
    # 1. Define the filename pattern Airflow is looking for
    file_name = f"mfg_sensor_batch_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    file_path = os.path.join("/opt/airflow/project", file_name)

    # 2. Generate and Save CSV
    print(f"🚀 Generating data for {file_name}...")
    df = generate_sensor_data(150)
    df.to_csv(file_path, index=False)
    print(f"💾 Saved CSV to {file_path}")

    # 3. Process with Utility
    client_utility_process(file_path)
