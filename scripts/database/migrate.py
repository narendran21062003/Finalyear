# Add project root to path
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

import mysql.connector
from src.config.db_config import get_db_connection

def migrate_database():
    print("Starting database migration...")
    conn = get_db_connection()
    if not conn:
        print("Failed to connect to database.")
        return

    cursor = conn.cursor()
    
    # Check if columns exist
    cursor.execute("SHOW COLUMNS FROM leads")
    columns = [column[0] for column in cursor.fetchall()]
    print(f"Current columns: {columns}")
    
    # Add 'phone' if missing
    if 'phone' not in columns:
        print("Adding 'phone' column...")
        try:
            cursor.execute("ALTER TABLE leads ADD COLUMN phone VARCHAR(50)")
            print("  [+] Added 'phone'")
        except Exception as e:
            print(f"  [!] Error adding 'phone': {e}")
    else:
        print("  [=] 'phone' column already exists.")
        
    # Add 'email' if missing
    if 'email' not in columns:
        print("Adding 'email' column...")
        try:
            cursor.execute("ALTER TABLE leads ADD COLUMN email VARCHAR(100)")
            print("  [+] Added 'email'")
        except Exception as e:
            print(f"  [!] Error adding 'email': {e}")
    else:
        print("  [=] 'email' column already exists.")

    # Remove 'contact_status' if it's still there (optional, but clean)
    if 'contact_status' in columns:
        print("Removing deprecated 'contact_status' column...")
        try:
            # Copy data first? Nah, user cleared DB anyway.
            cursor.execute("ALTER TABLE leads DROP COLUMN contact_status")
            print("  [-] Dropped 'contact_status'")
        except Exception as e:
            print(f"  [!] Error dropping 'contact_status': {e}")
            
    conn.commit()
    cursor.close()
    conn.close()
    print("Migration complete.")

if __name__ == "__main__":
    migrate_database()
