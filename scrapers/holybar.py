from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
import pandas as pd
import re
from datetime import datetime
import time
import unicodedata
from openai import OpenAI
import os
import json

def find_matches(driver, pattern):
    match = False
    wait = WebDriverWait(driver, 5)
    
    while True:
        images = driver.find_elements(By.TAG_NAME, "img")
        for img in images:
            alt = img.get_attribute('alt') or ''
            if pattern.search(alt):
                match = img.get_attribute('src')
                return match
            
        try:
            next_btn = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[aria-label='Next']")))
            next_btn.click()
            time.sleep(1)
        except (NoSuchElementException, TimeoutException):
            break
        
        return match

chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--window-size=1920,1080")
chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
chrome_options.add_argument("--no-sandbox")
# chrome_options.add_argument("--disable-dev-shm-usage")
# chrome_options.add_argument("--user-data-dir=/tmp/chrome-data")
# chrome_options.binary_location = "/usr/local/bin/chrome-linux64/chrome"
service = Service(r"C:\Users\Omer\Desktop\Coding\concerts project\scraper\chromedriver.exe")
driver = webdriver.Chrome(service=service, options=chrome_options)

driver.get('https://www.instagram.com/holybar/p/DF2QTMlIsGL/?img_index=1')

time.sleep(5)

pattern = re.compile(r'(sessions?|lineup)', re.IGNORECASE)

links = driver.find_elements(By.TAG_NAME, 'a')
links_url = [link.get_attribute('href') for link in links]

post_pattern = re.compile(r'https://www.instagram.com/holybar/p/')
posts = [link.get_attribute('href') for link in links if post_pattern.search(link.get_attribute('href') or '')] 

last_post = posts[1]
driver.get(last_post)
time.sleep(5)

profile_links = driver.find_elements(By.CSS_SELECTOR, "a[href='/holybar/']")
for elem in profile_links:
    try:
        print("Elem class:" + elem.get_attribute('class')[:32])
        post_body = elem.find_element(By.XPATH, "../../following-sibling::*[h1]/h1")
        print("post body found")
        post_text = post_body.text
        post_text_clean = unicodedata.normalize("NFKC", post_text)
        post_text_clean = re.sub(r'[^\x00-\x7F]+', '', post_text_clean)
        post_text_clean = re.sub(r'^\s+', '', post_text_clean, flags=re.MULTILINE)
        lineup = pattern.search(post_text_clean)
        if lineup:
            print('lineup found!')
            break
    except:
        print('not found, continuing..')
        continue

day_pattern = r'^(?:Sunday|Monday|Tuesday|Wednesday|Thursday|Friday|Saturday).*'
matches = re.findall(day_pattern, post_text_clean, flags=re.MULTILINE)

events = []

if matches:
    for line in matches:
        try:
            date, title = line.split(' - ', 1)
        except:
            date, title = line.split('  ', 1)
        title = title.strip()
        date = date + ' 20:45'
        date = datetime.strptime(date, '%A, %B %d %H:%M')
        date = date.replace(year=datetime.now().year)
        events.append({'show_name':title, 'date':date, 'link':last_post})
    events = pd.DataFrame(events)

else:
    matching_img = find_matches(driver, pattern)

    if not matching_img:
        raise IndexError('no lineup found')
    
    client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
    response = client.responses.create(
        model="gpt-4o-mini",
        input=[{
            "role": "user",
            "content": [
                {"type": "input_text", "text": "Extract all the shows' names and dates to json with keys: show_name, date"},
                {
                    "type": "input_image",
                    "image_url": matching_img,
                },
            ],
        }],
    )
    response_text = response.output_text
    response_json = response_text.strip('`').strip('json').strip()
    events = json.loads(response_json)
