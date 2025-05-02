from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json
from dateutil import parser
import pytz
import pandas as pd

def scrape():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--single-process")
    chrome_options.binary_location = "/usr/local/bin/chrome-linux64/chrome"
    service = Service('/usr/local/bin/chromedriver')
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    driver.get("https://test.hameretz2.org/")
    
    wait = WebDriverWait(driver, 20)
    
    events_elements = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'a[data-category="לייב"]')))
    urls = [e.get_attribute('href') for e in events_elements]
    
    events = []
    
    for url in urls:
        driver.get(url)
        script = wait.until(EC.presence_of_element_located((By.ID, "__NEXT_DATA__"))).get_attribute("textContent")
        data = json.loads(script)
        event_details = data['props']['pageProps']['event']
        show_name = event_details['title']
        date = event_details['startDate']
        tz = pytz.timezone("Asia/Jerusalem")
        date = parser.isoparse(date).astimezone(tz)
        date = date.strftime('%Y-%m-%d %H:%M:%S')
        img = event_details['whatsappImage']
        
        events.append({'show_name':show_name, 'date':date, 'link':url, 'img':img, 'venue':'המרץ2'})

    driver.quit()
        
    events = pd.DataFrame(events)
    return events