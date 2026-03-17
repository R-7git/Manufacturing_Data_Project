import snowflake.connector
import os
import csv
import logging
from faker import Faker
from datetime import datetime

# Industry Standard: Configure Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class ManufacturingDataProducer:
    def __init__(self):
        self.faker = Faker()
        self.file_name = f"mfg_sensor_batch_{datetime.now().strftime('%Y%m%d%H%M%S')}.csv"
        self.conn_params = {
            'account': 'BKVGNQZ-UO15536',
            'user': 'ROSHAN',
            'password': 'Rosh20090798395@',
            'role': 'ACCOUNTADMIN',
            'warehouse': 'INGEST_WH',
            'database': 'MFG_BRONZE_DB',
            'schema': 'RAW_DATA'
        }

    def generate_industry_data(self, row_count=100):
        """Generates realistic High-Tech Manufacturing sensor data."""
        logging.info(f"Generating {row_count} rows of realistic manufacturing data...")
        
        metrics = ['Temperature (C)', 'Pressure (PSI)', 'Vibration (mm/s)', 'Power Consumption (kW)']
        
        with open(self.file_name, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["sensor_id", "metric_name", "metric_value", "ingestion_timestamp"])
            
            for _ in range(row_count):
                writer.writerow([
                    self.faker.bothify(text='SNS-####'), # Realistic Sensor IDs like SNS-4921
                    self.faker.random_element(elements=metrics),
                    round(self.faker.pyfloat(left_digits=2, right_digits=2, positive=True, min_value=10, max_value=95), 2),
                    self.faker.date_time_this_month().strftime("%Y-%m-%d %H:%M:%S")
                ])
        return os.path.abspath(self.file_name)

    def upload_to_snowflake(self, file_path):
        """Uploads the generated file to Snowflake Internal Stage using PUT."""
        try:
            ctx = snowflake.connector.connect(**self.conn_params)
            cs = ctx.cursor()
            
            stage_path = "@MFG_BRONZE_DB.EXTERNAL_STAGES.MFG_INTERNAL_STAGE"
            logging.info(f"Uploading {self.file_name} to {stage_path}...")
            
            # Industry Standard: Use absolute paths for PUT commands
            cs.execute(f"PUT file://{file_path} {stage_path} AUTO_COMPRESS=TRUE")
            
            logging.info("SUCCESS: Data successfully moved to Snowflake Stage.")
            
        except Exception as e:
            logging.error(f"Failed to upload data: {e}")
            raise
        finally:
            cs.close()
            ctx.close()
            #if os.path.exists(file_path):
                #os.remove(file_path)
                #logging.info(f"Cleaned up local file: {file_path}")

if __name__ == "__main__":
    producer = ManufacturingDataProducer()
    file_path = producer.generate_industry_data(row_count=50)
    producer.upload_to_snowflake(file_path)
