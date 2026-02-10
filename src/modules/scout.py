"""
Scout Module - Data Acquisition
Handles web scraping from Google Maps with human-like interaction
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import requests
import time
import random
import re

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0"
]

class WebScout:
    def __init__(self):
        self.driver = None
        self.wait = None
        
    def setup_driver(self):
        """Initialize Selenium WebDriver with visible Chrome"""
        print("    Invoking Chrome Browser...")
        chrome_options = Options()
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--start-maximized')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        
        # Add experimental options to remove "Chrome is being controlled by automated test software" bar
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        # Anti-Bot: Set Random User agent
        user_agent = random.choice(USER_AGENTS)
        chrome_options.add_argument(f'user-agent={user_agent}')
        
        # Check for Headless Mode (Required for Cloud Hosting)
        import os
        if os.getenv('HEADLESS_MODE') == 'true':
            print("    [!] Running in Headless Mode (Cloud Compatibility)...")
            chrome_options.add_argument('--headless')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument("--window-size=1920,1080")
        
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        self.wait = WebDriverWait(self.driver, 20)
        
    def _slow_type(self, element, text):
        """Simulate human typing by sending keys one by one with delay"""
        for char in text:
            element.send_keys(char)
            time.sleep(random.uniform(0.1, 0.3))

    def extract_areas(self, text_content):
        """
        Extract potential area names from text content (address).
        """
        if not text_content: 
            return []
            
        import re
        potential_areas = set()
        
        # Split by common delimiters
        parts = re.split(r'[,|\-]', text_content)
        
        for part in parts:
            clean_part = part.strip()
            # If it looks like a location (Capitalized, not too long, not a common word)
            if clean_part and len(clean_part) > 3 and len(clean_part) < 30:
                # Basic check: title case and no numbers (unless it's like "Sector 5")
                # Also exclude common state names or "India" to be safe, though caller should filter too
                if clean_part[0].isupper() and not any(char.isdigit() for char in clean_part if char not in [' ', '-']):
                     potential_areas.add(clean_part)
        
        return list(potential_areas)
            
    def find_leads(self, search_query, max_results=3, location_context=None):
        """
        Scrape business leads from Google Maps interactively
        """
        leads = []
        found_areas = set()
        
        try:
            if not self.driver:
                self.setup_driver()
            
            # 1. Go to Google Maps Home
            print("    Navigating to Google Maps...")
            self.driver.get("https://www.google.com/maps")
            print("    Waiting for page to load...")
            time.sleep(5) # Allow redirects and full load

            # Handle "Accept Cookies" or "Sign in" popups if they obscure the view
            try:
                # Common consent buttons
                buttons = self.driver.find_elements(By.CSS_SELECTOR, "button")
                for btn in buttons:
                    if "accept" in btn.text.lower() or "agree" in btn.text.lower():
                        print("    [!] Closing consent popup...")
                        btn.click()
                        time.sleep(2)
                        break
            except:
                pass
            
            # 2. Find Search Box
            print("    Locating search box...")
            search_box = None
            selectors = [
                (By.ID, "searchboxinput"),
                (By.NAME, "q"),
                (By.CSS_SELECTOR, "input#searchboxinput"),
                (By.XPATH, "//input[@id='searchboxinput']"),
                (By.CSS_SELECTOR, "input[aria-label='Search Google Maps']")
            ]
            
            for by, value in selectors:
                try:
                    search_box = self.wait.until(EC.element_to_be_clickable((by, value)))
                    print(f"    [+] Found search box using {by}='{value}'")
                    break
                except:
                    continue
            
            if not search_box:
                print("    [!] CRITICAL: Could not find search box with any selector!")
                return self._generate_mock_leads(max_results)

            # 3. Type Query Slowly
            print(f"    Typing query: '{search_query}'...")
            try:
                search_box.click() # Ensure focus
            except:
                pass
            search_box.clear()
            self._slow_type(search_box, search_query)
            time.sleep(1)
            
            # verify text entered
            entered_text = search_box.get_attribute("value")
            if not entered_text:
                 print("    [!] Text entry failed! Retrying with direct send_keys...")
                 search_box.send_keys(search_query)
            
            # Try clicking search button instead of just Enter
            try:
                search_button = self.driver.find_element(By.ID, "searchbox-searchbutton")
                search_button.click()
            except:
                search_box.send_keys(Keys.ENTER)
            
            # 4. Wait for Results and Deep Scroll
            print("    Waiting for results...")
            try:
                self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div[role="feed"]')))
            except:
                time.sleep(5)

            print(f"    Scanning for up to {max_results} results (Deep Scroll)...")
            last_count = 0
            retries = 0
            while True:
                elements = self.driver.find_elements(By.CSS_SELECTOR, 'a[href^="https://www.google.com/maps/place"]')
                if len(elements) >= max_results:
                    print(f"    [+] Loaded {len(elements)} results.")
                    break
                
                if len(elements) == last_count:
                    retries += 1
                    if retries > 10: break
                else:
                    retries = 0
                
                last_count = len(elements)
                self._scroll_results()
                time.sleep(1.5) # Allow items to load
                
            # 5. Process Results One by One
            print("    Extracting business information...")
            processed_count = 0
            main_window = self.driver.current_window_handle
            
            while processed_count < max_results:
                try:
                    # Re-locate elements
                    elements = self.driver.find_elements(By.CSS_SELECTOR, 'a[href^="https://www.google.com/maps/place"]')
                    
                    if not elements:
                        print("    [!] No results found.")
                        if processed_count == 0:
                            return self._generate_mock_leads(max_results)
                        break
                        
                    if processed_count >= len(elements):
                        self._scroll_results()
                        time.sleep(2)
                        elements = self.driver.find_elements(By.CSS_SELECTOR, 'a[href^="https://www.google.com/maps/place"]')
                        
                    if processed_count >= len(elements):
                        print("    [!] No more results loaded.")
                        break
                        
                    target_element = elements[processed_count]
                    
                    # Scroll into view
                    self.driver.execute_script("arguments[0].scrollIntoView(true);", target_element)
                    time.sleep(1)
                    
                    # Get Name from list before clicking (as fallback)
                    name = target_element.get_attribute('aria-label')
                    if not name:
                        processed_count += 1
                        continue

                    print(f"    [>] Processing {processed_count + 1}/{max_results}: {name}")
                    
                    # Human-like jitter delay
                    time.sleep(random.uniform(1.5, 3.5))
                    
                    try:
                        target_element.click()
                    except:
                        self.driver.execute_script("arguments[0].click();", target_element)
                        
                    time.sleep(2.5) # Wait for details panel
                    
                    # Extract Rating
                    rating = 0.0
                    review_count = 0
                    try:
                        rating_elm = self.driver.find_element(By.CSS_SELECTOR, 'div[role="img"][aria-label*="stars"]')
                        rating_text = rating_elm.get_attribute("aria-label").split(" ")[0]
                        rating = float(rating_text)
                    except:
                        pass
                        
                    # Extract Reviews if Rating is low/mid (to find pain points)
                    reviews_text = "No textual reviews found."
                    if rating > 0 and rating < 4.8:
                        try:
                            # Click "Reviews" tab
                            print(f"       [?] Rating is {rating}. Checking reviews...")
                            buttons = self.driver.find_elements(By.TAG_NAME, "button")
                            for btn in buttons:
                                if "Reviews" in btn.text:
                                    self.driver.execute_script("arguments[0].click();", btn)
                                    time.sleep(2)
                                    break
                            
                            # Scrape review text (class 'wiI7pd' is common for review text)
                            review_elms = self.driver.find_elements(By.CLASS_NAME, "wiI7pd")
                            extracted_reviews = [elm.text for elm in review_elms[:3] if elm.text.strip()]
                            if extracted_reviews:
                                reviews_text = " | ".join(extracted_reviews)
                                print(f"       [+] Extracted {len(extracted_reviews)} reviews.")
                        except Exception as e:
                            print(f"       [!] detailed review scrape failed: {str(e)[:50]}")
                            # Go back to 'Overview' (next click will reset)
                    
                    # Website
                    website = "Not listed"
                    try:
                        website_btn = self.driver.find_element(By.CSS_SELECTOR, '[data-item-id="authority"]')
                        website = website_btn.get_attribute('href')
                    except:
                        pass
                    
                    # Phone
                    phone = "Not listed"
                    try:
                        phone_btns = self.driver.find_elements(By.CSS_SELECTOR, 'button[data-item-id^="phone:"]')
                        if phone_btns:
                            phone = phone_btns[0].get_attribute('aria-label')
                            if phone:
                                phone = phone.replace("Phone: ", "").strip()
                    except:
                        pass
                        
                    # Verify website
                    status = self.verify_website(website) if website != "Not listed" else "N/A"
                    
                    # Extract Email
                    email = self.extract_email_from_website(website) if website != "Not listed" else None
                    if email:
                        print(f"       [+] Found Email: {email}")

                    # Extract Address for Area Detection
                    address = "Not listed"
                    detected_areas = []
                    try:
                        # Look for address button (usually aria-label starts with "Address:")
                        address_btn = self.driver.find_element(By.CSS_SELECTOR, 'button[data-item-id="address"]')
                        address = address_btn.get_attribute("aria-label")
                        if address:
                            address = address.replace("Address: ", "").strip()
                            detected_areas = self.extract_areas(address)
                            
                            if location_context:
                                ignore_terms = [location_context.get('district', '').lower(), location_context.get('state', '').lower(), 'india', 'limit', 'road']
                                detected_areas = [area for area in detected_areas if area.lower() not in ignore_terms]
                                found_areas.update(detected_areas)
                    except:
                        pass

                    lead = {
                        'business_name': name,
                        'website_url': website,
                        'technical_status': status,
                        'reviews_snippet': f"Rating: {rating}. Reviews: {reviews_text}",
                        'phone': phone,
                        'email': email,
                        'address': address,
                        'detected_areas': detected_areas
                    }
                    leads.append(lead)
                    print(f"       [+] Extracted: {name} | {website} | {phone} | {email}")
                    
                    processed_count += 1
                    time.sleep(2) # Pause before next
                    
                except Exception as e:
                    print(f"    [!] Error processing result {processed_count}: {e}")
                    processed_count += 1
                    continue
            
            if len(leads) == 0:
                return self._generate_mock_leads(max_results)
                    
        except Exception as e:
            print(f"Error in find_leads: {e}")
            if len(leads) == 0:
                 return self._generate_mock_leads(max_results)
        
        return leads
    
    def _scroll_results(self):
        """Scroll the results pane"""
        if not self.driver:
            return
            
        try:
            feed = self.driver.find_element(By.CSS_SELECTOR, 'div[role="feed"]')
            self.driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", feed)
        except:
            # Fallback: Scroll window
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

    def verify_website(self, url):
        return "Active" # Placeholder

    def extract_email_from_website(self, url):
        """Visit the website and scrape for email addresses"""
        if not url or "http" not in url:
            return None
        
        main_tab = self.driver.current_window_handle
        
        try:
            print(f"       [?] Opening {url} in new tab...")
            
            # Open new tab
            self.driver.execute_script(f"window.open('{url}', '_blank');")
            time.sleep(1)
            
            # Switch to new tab
            new_tab = [h for h in self.driver.window_handles if h != main_tab][-1]
            self.driver.switch_to.window(new_tab)
            
            # Set short timeout for the website load
            self.driver.set_page_load_timeout(12)
            try:
                if self.driver.current_url == "about:blank":
                    self.driver.get(url)
            except:
                pass
                
            time.sleep(3) # Wait for content
            
            page_source = self.driver.page_source
            emails = re.findall(r'[a-zA-Z0-9._%+-]+@\S+\.\S+', page_source)
            # Refined regex for email
            emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', page_source)
            
            unique_emails = list(set(emails))
            
            for email in unique_emails:
                if not any(x in email for x in ['.png', '.jpg', '.jpeg', 'sentry', 'example', 'gif']):
                    return email
            return None
            
        except Exception as e:
            print(f"       [!] Email extraction error: {str(e)[:50]}")
            return None
        finally:
            # Always close the new tab and switch back
            try:
                if len(self.driver.window_handles) > 1:
                    self.driver.close()
                self.driver.switch_to.window(main_tab)
            except:
                pass
            self.driver.set_page_load_timeout(30)
    
    def _generate_mock_leads(self, count):
        """Generate mock leads for demonstration if scraping fails"""
        mock_leads = []
        business_types = ['Bistro', 'Cafe', 'Restaurant', 'Diner', 'Grill']
        locations = ['Downtown', 'Uptown', 'Central', 'Plaza', 'Street']
        
        for i in range(count):
            name = f"{random.choice(locations)} {random.choice(business_types)} {i+1}"
            mock_leads.append({
                'business_name': name,
                'website_url': f"http://www.example-{i}.com",
                'technical_status': 'Active',
                'reviews_snippet': 'Mock data (Scraping fallback)',
                'phone': f"555-010{i}",
                'email': f"contact@example-{i}.com",
                'detected_areas': []
            })
        return mock_leads
    
    def close(self):
        """Close the WebDriver to free resources"""
        if self.driver:
            self.driver.quit()
            self.driver = None
