import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

import mysql.connector
from src.config.db_config import get_db_connection

def clear_leads():
    """Truncate the leads table to clear all records"""
    conn = get_db_connection()
    if not conn:
        print("Failed to connect to database.")
        return False
    
    try:
        cursor = conn.cursor()
        print("Clearing all records from 'leads' table...")
        # TRUNCATE works regardless of column changes
        cursor.execute("TRUNCATE TABLE leads")
        conn.commit()
        cursor.close()
        print("[OK] Database cleared successfully (Phone/Email columns preserved).")
        return True
    except Exception as e:
        print(f"Error clearing database: {e}")
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    clear_leads()
