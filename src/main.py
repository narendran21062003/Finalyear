"""
Main Orchestrator - Central Pipeline Coordinator
Coordinates data flow between modules and manages database operations
"""

import mysql.connector
from datetime import datetime
from src.modules.scout import WebScout
from src.modules.analyst import AIAnalyst
from src.config.db_config import get_db_connection

class LeadOrchestrator:
    def __init__(self):
        self.scout = WebScout()
        self.analyst = AIAnalyst()
        self.connection = None
        
    def initialize_database(self):
        """Initialize database connection and ensure table exists"""
        try:
            connection = get_db_connection()
            if not connection:
                print("Failed to connect to database")
                return False
            
            self.connection = connection
            cursor = connection.cursor()
            
            # Create table if not exists
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
                phone VARCHAR(50),
                email VARCHAR(100)
            )
            """
            cursor.execute(create_table_query)
            
            # Migration: Ensure new columns exist if table already exists
            try:
                cursor.execute("ALTER TABLE leads ADD COLUMN phone VARCHAR(50)")
                cursor.execute("ALTER TABLE leads ADD COLUMN email VARCHAR(100)")
            except:
                pass # Already exists
            
            # Migration: Add UNIQUE constraints for deduplication
            try:
                # Add unique index on website_url
                cursor.execute("CREATE UNIQUE INDEX idx_website ON leads(website_url)")
            except mysql.connector.Error as err:
                 pass # Already exists or duplicates prevent it

            try:
                # Add unique index on business_name
                cursor.execute("CREATE UNIQUE INDEX idx_business_name ON leads(business_name)")
            except mysql.connector.Error as err:
                 pass # Already exists
                
            self.connection.commit()
            cursor.close()
            
            print("[OK] Database initialized successfully")
            return True
            
        except mysql.connector.Error as err:
            print(f"Database initialization error: {err}")
            return False
    
    def process_leads(self, search_query, max_results=5):
        """
        Main processing pipeline
        """
        print(f"\n{'='*60}")
        print(f"Starting Lead Identification Pipeline")
        print(f"Search Query: {search_query}")
        print(f"{'='*60}\n")
        
        # Step 1: Initialize database
        if not self.initialize_database():
            return
        
        # Step 2: Acquire leads through web scraping
        print("[>] Step 1: Acquiring leads...")
        leads = self.scout.find_leads(search_query, max_results)
        print(f"[OK] Found {len(leads)} potential leads")
        
        # Step 3: Close browser to free resources
        print("\n[>] Freeing browser resources...")
        import time
        time.sleep(2) # Give a moment to see the final state
        self.scout.close()
        
        # Step 4: Analyze each lead with AI
        print("\n[>] Step 2: Analyzing leads with AI...")
        
        for idx, lead in enumerate(leads, 1):
            print(f"\n  Processing lead {idx}/{len(leads)}: {lead['business_name']}")
            
            # Simulate review text
            sample_reviews = f"Reviews for {lead['business_name']}: Some customers mentioned service issues."
            lead['reviews_snippet'] = sample_reviews
            
            # AI Analysis
            analysis = self.analyst.analyze_reviews(sample_reviews)
            lead['pain_point'] = analysis['pain_point']
            
            # Generate email draft
            lead['email_draft'] = self.analyst.generate_email_draft(
                lead['business_name'],
                lead['pain_point']
            )
            
            # Extract Phone and Email
            lead['phone'] = lead.get('phone', 'Not listed')
            lead['email'] = lead.get('email', 'Not listed')
            
            # Step 5: Save to database
            self._save_lead_to_db(lead)
            print(f"    [OK] Pain Point: {lead['pain_point']}")
            print(f"    [OK] Status: {lead['technical_status']}")
            print(f"    [->] Draft Msg: {lead['email_draft'][:100]}...") # Show preview
        
        print(f"\n{'='*60}")
        print(f"[OK] Pipeline completed successfully!")
        print(f"Total leads processed: {len(leads)}")
        print(f"{'='*60}\n")
        
    def _save_lead_to_db(self, lead):
        """Save lead data to MySQL database"""
        try:
            if not self.connection:
                print("    [X] Database connection lost.")
                return

            cursor = self.connection.cursor()
            
            insert_query = """
            INSERT IGNORE INTO leads (
                business_name, website_url, technical_status,
                reviews_snippet, pain_point, email_draft, phone, email
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            
            values = (
                lead['business_name'],
                lead['website_url'],
                lead['technical_status'],
                lead['reviews_snippet'],
                lead['pain_point'],
                lead['email_draft'],
                lead['phone'],
                lead['email']
            )
            
            cursor.execute(insert_query, values)
            self.connection.commit()
            cursor.close()
            
        except mysql.connector.Error as err:
            print(f"    [X] Database insert error: {err}")
    
    def close(self):
        """Clean up resources"""
        if self.connection:
            self.connection.close()
        self.scout.close()


def main():
    """Main entry point"""
    print("    ==================================================")
    print("      Autonomous Customer Lead Identification System")
    print("      Using Data Analytics & AI")
    print("    ==================================================")
    
    # Initialize orchestrator
    orchestrator = LeadOrchestrator()
    
    try:
        # Interactive user input
        print("\n" + "="*50)
        search_query = input(" What do you want to search? (e.g., 'hotels in bangalore'): ")
        
        if not search_query.strip():
            search_query = "restaurants in bangalore" # Default
            print(f"Using default query: {search_query}")
            
        orchestrator.process_leads(search_query, max_results=5)
        
    except KeyboardInterrupt:
        print("\n\n Process interrupted by user")
    except Exception as e:
        print(f"\n Error: {e}")
    finally:
        orchestrator.close()
        print("\n System shutdown complete")


if __name__ == "__main__":
    main()
