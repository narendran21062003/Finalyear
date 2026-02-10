import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

from src.modules.scout import WebScout
from src.modules.analyst import AIAnalyst
import time

def test_review_analysis():
    print("Testing Review Extraction & AI Analysis...")
    scout = WebScout()
    analyst = AIAnalyst()
    
    # "Post Office" usually has mixed/bad reviews, good for testing "Service/Quality" pain points
    query = "Post Office in New York" 
    
    try:
        leads = scout.find_leads(query, max_results=3)
        
        print(f"\n[SUMMARY] Successfully scraped {len(leads)} leads.")
        for lead in leads:
            print(f"Business: {lead['business_name']}")
            print(f"Snippet: {lead['reviews_snippet']}")
            
            # Test Analysis
            analysis = analyst.analyze_reviews(lead['reviews_snippet'])
            print(f"AI Result: {analysis}")
            print("---")
            
    except Exception as e:
        print(f"CRITICAL ERROR: {e}")
    finally:
        scout.close()

if __name__ == "__main__":
    test_review_analysis()
