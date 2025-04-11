from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
from datetime import datetime
import time
import re

def scrape():
    heb_to_eng = {
        "בינו׳": "Jan",
        "בפבר׳":"Feb",
        "במרץ":"Mar",
        "באפר׳":"Apr",
        "במאי":"May",
        "ביונ׳":"Jun",
        "ביול׳":"Jul",
        "באוג׳":"Aug",
        "בספט׳":"Sep",
        "באוק׳":"Oct",
        "בנוב׳":"Nov",
        "בדצמ׳":"Dec"
        }
    
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
    chrome_options.add_argument("--no-sandbox")
    # chrome_options.add_argument("--disable-dev-shm-usage")
    # chrome_options.add_argument("--user-data-dir=/tmp/chrome-data")
    # chrome_options.add_argument("--single-process")
    # chrome_options.add_argument("--remote-debugging-port=9222")
    # chrome_options.binary_location = "/usr/local/bin/chrome-linux64/chrome"
    service = Service(r"C:\Users\Omer\Desktop\Coding\concerts project\chromedriver.exe")
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    driver.get("https://www.hameretz2.org/")
    
    wait = WebDriverWait(driver, 20)
    events_section = wait.until(EC.presence_of_element_located((By.ID, "comp-m4r7k1ni")))
    
    events = []
    
    for event in events_section.find_elements(By.CLASS_NAME, 'qElViY'):
        title = event.find_element(By.CLASS_NAME, 'DjQEyU').get_attribute('textContent')
        if any(word in title for word in ['קולנוע', 'לנדסקייפ']):
            continue
        wait = WebDriverWait(event, 20)
        button = event.find_element(By.CSS_SELECTOR, ".sr_1jEj.sFpk6n3.sUMQ4T0.oDFuHIw---priority-4-link.s__6KuQ2f")
        time.sleep(3)
        button.click()
        date_elem = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".Ke8eTf.tnxjtm")))
        date = date_elem.get_attribute('textContent').strip()
        for heb, eng in heb_to_eng.items():
            date = date.replace(heb, eng)
        date, hour = date.split(', ', 1)
        hour = hour[:5]
        date = date + ' ' + str(hour)
        date = datetime.strptime(date, '%d %b %Y %H:%M')
        link = event.find_element(By.CSS_SELECTOR, '.DjQEyU.m022zm.aUkG34').get_attribute('href')
        img = event.find_element(By.CSS_SELECTOR, '.L5u5gG.sGc29C2')
        img = img.find_element(By.TAG_NAME, 'img').get_attribute('src')
        img = img.replace('blur_2,', '')
        img = re.sub(r"w_\d+", "w_500", img)
        img = re.sub(r"h_\d+", "h_300", img)
        events.append({'show_name':title, 'date':date, 'link':link, 'img':img, 'venue':'המרץ 2'})
        
    events = pd.DataFrame(events)
    return events

events = hameretz2()