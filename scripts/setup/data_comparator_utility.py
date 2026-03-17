import snowflake.connector
import logging

# Configure Logging for the Utility
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class RapidDataComparator:
    def __init__(self):
        self.conn_params = {
            'account': 'BKVGNQZ-UO15536',
            'user': 'ROSHAN',
            'password': 'Rosh20090798395@',
            'role': 'ACCOUNTADMIN',
            'warehouse': 'MFG_WH'
        }

    def validate_migration(self):
        """Compares Source (STG) vs Target (DW) for Data Integrity."""
        try:
            ctx = snowflake.connector.connect(**self.conn_params)
            cs = ctx.cursor()

            # 1. Get Source Count (Staging Database)
            cs.execute("SELECT COUNT(*) FROM STG_DB.STG_SCHEMA.STG_SENSOR_DATA")
            source_count = cs.fetchone()[0]

            # 2. Get Target Count (Data Warehouse Database - SCD Type 1)
            cs.execute("SELECT COUNT(*) FROM DW_DB.RPT_SCHEMA.DW_SENSOR_MASTER")
            target_count = cs.fetchone()[0]

            logging.info(f"--- MIGRATION VALIDATION REPORT ---")
            logging.info(f"Source (STG_DB) Count: {source_count}")
            logging.info(f"Target (DW_DB) Count:  {target_count}")

            if source_count == target_count:
                logging.info("✅ SUCCESS: Data Migration is 100% Consistent.")
            else:
                diff = abs(source_count - target_count)
                logging.warning(f"⚠️ DISCREPANCY: Found a difference of {diff} rows!")

        except Exception as e:
            logging.error(f"Validation Failed: {e}")
        finally:
            cs.close()
            ctx.close()

if __name__ == "__main__":
    comparator = RapidDataComparator()
    comparator.validate_migration()
