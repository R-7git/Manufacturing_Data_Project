import pandas as pd
import os

def client_utility_process(file_path):
    """Simulates splitting large files and converting CSV to Parquet."""
    df = pd.read_csv(file_path)
    
    # Industry Practice: Adding metadata columns before landing in Lake
    df['processed_at'] = pd.Timestamp.now()
    
    # Convert to Parquet (Industry standard for Enriched Layer)
    parquet_path = file_path.replace(".csv", ".parquet")
    df.to_parquet(parquet_path, index=False)
    
    print(f"✅ Utility: Converted {file_path} to {parquet_path}")
    return parquet_path
