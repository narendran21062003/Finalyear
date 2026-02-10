import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

import mysql.connector
from src.config.db_config import get_db_connection

def fix_schema_length():
    print("Starting schema fix for column length...")
    conn = get_db_connection()
    if not conn:
        print("Failed to connect to database.")
        return

    cursor = conn.cursor()
    
    # Check current column type (optional, but good for logs)
    cursor.execute("DESCRIBE leads")
    columns = cursor.fetchall()
    for col in columns:
        if col[0] == 'website_url':
            print(f"Current 'website_url' type: {col[1]}")
            
    # Alter table to TEXT (65,535 chars)
    print("Modifying 'website_url' to TEXT...")
    try:
        cursor.execute("ALTER TABLE leads MODIFY COLUMN website_url TEXT")
        print("  [+] Successfully updated 'website_url' to TEXT")
    except Exception as e:
        print(f"  [!] Error updating 'website_url': {e}")
        
    # Also update business_name just in case (some names are long with keywords)
    print("Modifying 'business_name' to VARCHAR(500)...")
    try:
        cursor.execute("ALTER TABLE leads MODIFY COLUMN business_name VARCHAR(500)")
        print("  [+] Successfully updated 'business_name'")
    except Exception as e:
        print(f"  [!] Error updating 'business_name': {e}")

    conn.commit()
    cursor.close()
    conn.close()
    print("Schema fix complete.")

if __name__ == "__main__":
    fix_schema_length()
