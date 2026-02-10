
import os
import mysql.connector
from src.config.db_config import get_db_connection
import sys

# Force stdout to use utf-8 to avoid Windows encoding errors
sys.stdout.reconfigure(encoding='utf-8')

host = os.getenv('DB_HOST', 'localhost')
user = os.getenv('DB_USER', 'root')
password = os.getenv('DB_PASSWORD', '')
port = int(os.getenv('DB_PORT', 3306))
database = os.getenv('DB_NAME', 'lead_management')

print(f"Attempting to connect to MySQL at {host}:{port} with user '{user}'...")

try:
    # 1. Try connecting without database to check server access
    pf = mysql.connector.connect(
        host=host,
        user=user,
        password=password,
        port=port
    )
    print("✅ MySQL Server connection successful!")
    
    cursor = pf.cursor()
    
    # 2. Check if database exists
    cursor.execute("SHOW DATABASES LIKE 'lead_management'")
    result = cursor.fetchone()
    if result:
        print(f"✅ Database '{database}' exists.")
    else:
        print(f"❌ Database '{database}' does NOT exist.")
        print("   Attempting to create it...")
        try:
            cursor.execute(f"CREATE DATABASE {database}")
            print(f"   ✅ Database '{database}' created successfully.")
        except Exception as e:
            print(f"   ❌ Failed to create database: {e}")
            pf.close()
            exit(1)

    cursor.close()
    pf.close()

    # 3. Connect to specific database and check table
    print(f"Connecting to database '{database}'...")
    conn = mysql.connector.connect(
        host=host,
        user=user,
        password=password,
        port=port,
        database=database
    )
    
    cursor = conn.cursor()
    cursor.execute("SHOW TABLES LIKE 'leads'")
    result = cursor.fetchone()
    
    if result:
        print("✅ Table 'leads' exists.")
        
        # Optional: Check table structure
        cursor.execute("DESCRIBE leads")
        columns = [column[0] for column in cursor.fetchall()]
        print(f"   Columns found: {', '.join(columns)}")
        
    else:
        print("❌ Table 'leads' does NOT exist.")
        print("   Attempting to create it using schema from main.py logic...")
        
        create_table_query = """
        CREATE TABLE IF NOT EXISTS leads (
            id INT AUTO_INCREMENT PRIMARY KEY,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            business_name VARCHAR(255),
            website_url VARCHAR(255),
            technical_status VARCHAR(50),
            reviews_snippet TEXT,
            pain_point VARCHAR(100),
            email_draft TEXT,
            contact_status VARCHAR(50)
        )
        """
        cursor.execute(create_table_query)
        conn.commit()
        print("   ✅ Table 'leads' created successfully.")

    cursor.close()
    conn.close()
    print("\n🎉 Database setup verification COMPLETE. You are ready to run main.py!")

except mysql.connector.Error as err:
    print(f"❌ Connection Failed: {err}")
    if err.errno == 1045:
        print("   -> Access Denied. Please check your DB_PASSWORD in the .env file.")
    elif err.errno == 2003:
        print("   -> Can't connect to MySQL server. Is the service running?")

except Exception as e:
    print(f"❌ An unexpected error occurred: {e}")
