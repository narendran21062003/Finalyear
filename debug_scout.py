
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time

def debug_scout():
    print("Setting up driver...")
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    # chrome_options.add_argument('--disable-gpu') 
    # Sometimes headless is detected. 
    # Let's try adding a user agent
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36")

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    try:
        url = "https://www.google.com/search?q=restaurants+in+bangalore"
        print(f"Navigating to {url}...")
        driver.get(url)
        time.sleep(3)
        
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        
        results = soup.find_all('div', class_='g')
        print(f"Found {len(results)} results with class 'g'")
        
        # Try finding h3 directly
        h3s = soup.find_all('h3')
        print(f"Found {len(h3s)} h3 tags")
        
        for i, h3 in enumerate(h3s[:3]):
            print(f"h3 #{i}: {h3.text}")
            parent = h3.find_parent('a')
            if parent:
                print(f"  - Link: {parent.get('href')}")
            else:
                print("  - No parent link found directly")
                # Try finding closest 'a'
                # sometimes h3 is inside div inside a
                
    finally:
        driver.quit()

if __name__ == "__main__":
    debug_scout()
