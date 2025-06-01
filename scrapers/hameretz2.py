import json
import tempfile
import shutil
import pytz
import pandas as pd
from dateutil import parser
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def scrape():
    """
    Launches a headless Chrome instance with a temporary profile, visits the
    HaMeretz 2 test site, and extracts all events tagged as live (“לייב”).

    Steps:
      1. Create a temporary user-data directory to isolate Chrome profile.
      2. Configure ChromeOptions for headless scraping and fixed window size.
      3. Launch Chrome WebDriver.
      4. Navigate to the main calendar page and wait for all live-event links.
      5. Collect each event URL, then:
         a. Load the event detail page.
         b. Extract the embedded JSON (__NEXT_DATA__) containing event props.
         c. Pull title, startDate, and whatsappImage.
         d. Parse ISO date to Asia/Jerusalem timezone and format as string.
      6. Assemble a list of dicts and convert to a pandas DataFrame.
      7. Always quit Chrome and delete the temporary profile directory.

    Returns:
        pandas.DataFrame with columns ['show_name', 'date', 'link', 'img', 'venue']
    """
    driver = None
    try:
        # Prepare temporary Chrome profile to avoid cache conflicts
        user_data_dir = tempfile.mkdtemp(prefix="chrome-profile-", dir='/tmp')
        chrome_options = Options()
        chrome_options.add_argument("--headless=new")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-setuid-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--single-process")
        chrome_options.add_argument(f"--user-data-dir={user_data_dir}")
        chrome_options.add_argument("--no-first-run")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--disable-background-networking")
        chrome_options.add_argument("--disable-default-apps")
        chrome_options.add_argument("--disable-features=VizDisplayCompositor")
        chrome_options.binary_location = "/usr/local/bin/chrome-linux64/chrome"
        # Point to the ChromeDriver executable
        service = Service('/usr/local/bin/chromedriver')

        # Launch headless browser
        try:
            print("Launching Chrome...")
            driver = webdriver.Chrome(service=service, options=chrome_options)
            print("Chrome launched successfully!")
        except Exception as e:
            print(e)
            
        # Visit the calendar and wait for live-event links
        driver.get("https://test.hameretz2.org/")
        wait = WebDriverWait(driver, 20)
        events_elements = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'a[data-category="לייב"]')))
        urls = [e.get_attribute('href') for e in events_elements]
        
        events = []
        tz = pytz.timezone("Asia/Jerusalem")
        
        for url in urls:
            driver.get(url)
            # The __NEXT_DATA__ script tag holds JSON with event info
            script = wait.until(EC.presence_of_element_located((By.ID, "__NEXT_DATA__"))).get_attribute("textContent")
            data = json.loads(script)
            event_details = data['props']['pageProps']['event']

            # Extract and normalize fields
            show_name = event_details['title']

            # Parse ISO timestamp to local tz and format
            date = parser.isoparse(data["startDate"]).astimezone(tz)
            date = date.strftime('%Y-%m-%d %H:%M:%S')
            img = event_details['whatsappImage']
            
            events.append({'show_name':show_name, 'date':date, 'link':url, 'img':img, 'venue':'המרץ 2'})

        # Convert to DataFrame for downstream use
        return pd.DataFrame(events)

    finally:
        # Clean up: close browser and remove temp profile
        if driver:
            driver.quit()
        shutil.rmtree(user_data_dir, ignore_errors=True)