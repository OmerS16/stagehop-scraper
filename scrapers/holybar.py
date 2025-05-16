from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
import pandas as pd
import re
from datetime import datetime, date as Date
import time
import unicodedata
from openai import OpenAI
import os
import json
import calendar

def scrape():
    
    FORMATS = [
        "%A, %B %d",
        "%A %B %d",
        "%A %d.%m",
        "%A"
        ]
    
    POST_PATHS = [
        "../../following-sibling::*[h1]/h1",
        "../following-sibling::span"
        ]
    
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
    try:
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
        
        random_post = 'https://www.instagram.com/holybar/p/DF2QTMlIsGL/?img_index=1'
        driver.get(random_post)
        
        time.sleep(10)
        
        pattern = re.compile(r'(sessions?|lineup)', re.IGNORECASE)
        
        links = driver.find_elements(By.TAG_NAME, 'a')
        links_url = [[link.get_attribute('href'), link.find_element(By.TAG_NAME, 'img').get_attribute('src')] for link in links if link.find_elements(By.TAG_NAME, 'img')]
        
        post_pattern = re.compile(r'https://www.instagram.com/holybar/(?:p|reel)/')
        posts = [(href,src) for href, src in links_url if post_pattern.search(href or '')]
        
        last_post = posts[1]
        last_post_img = last_post[1]
        driver.get(last_post[0])
        time.sleep(15)
    
     
        profile_links = driver.find_elements(By.CSS_SELECTOR, "a[href='/holybar/']")
        
        match = None

        for elem in profile_links:
            for path in POST_PATHS:
                try:
                    post_body = elem.find_element(By.XPATH, path)
                    print("post body found")
                    post_text = post_body.text
                    post_text_clean = unicodedata.normalize("NFKC", post_text)
                    post_text_clean = re.sub(r'[^\x00-\x7F]+', '', post_text_clean)
                    post_text_clean = re.sub(r'^\s+', '', post_text_clean, flags=re.MULTILINE)
                    day_pattern = r'^(?:Sunday|Monday|Tuesday|Wednesday|Thursday|Friday|Saturday).*'
                    match = re.findall(day_pattern, post_text_clean, flags=re.MULTILINE)
                except:
                    print('not found, continuing..')
                    continue
                if match:
                    break
            if match:
                break
        
        events = []
        matching_img = None
        
        post_date = driver.find_element(By.TAG_NAME, 'time').get_attribute('datetime')
        post_date = datetime.strptime(post_date, "%Y-%m-%dT%H:%M:%S.%fZ")
                
        
        if match:
            for line in match:
                for symbol in [' - ', '  ']:
                    try:
                        date, title = line.split(symbol, 1)
                        title = title.strip()
                        for frmt in FORMATS:
                            try:
                                if frmt == "%A":
                                    day = list(calendar.day_name).index(date) + 1
                                    year, week, _ = post_date.isocalendar()
                                    if day != 7:
                                        week += 1
                                    date = Date.fromisocalendar(year, week, day)
                                else:
                                    date = datetime.strptime(date, frmt)
                            except ValueError:
                                continue    
                                
                        date = date.replace(year=datetime.now().year)
                        events.append({'show_name':title, 'date':date})
                    except:
                        continue

        else:
            print("No lineup found in post's body..\nActivating AI..")
            matching_img = find_matches(driver, pattern)
        
            if not matching_img:
                raise IndexError('no lineup found')
            
            client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
            try:
                response = client.responses.create(
                    model="gpt-4o-mini",
                    input=[{
                        "role": "user",
                        "content": [
                            {"type": "input_text", "text": "Extract all the shows' names and dates to json with keys: show_name, date. The default hour is 20:45, return date in format %Y-%m-%d %H:%M. Do not add any text to the response so I could convert your response to json."},
                            {
                                "type": "input_image",
                                "image_url": matching_img,
                            },
                        ],
                    }],
                )
                if response:
                    print('AI successfully responded')
            except:
                print('AI failed to respond')

            response_text = response.output_text
            response_json = response_text.strip('`').strip('json').strip()
            print(response_json)

            try:
                events = json.loads(response_json)
            except:
                print('Bad JSON given by AI')
            
        events = pd.DataFrame(events)
        events['date'] = pd.to_datetime(events['date'], format='%Y-%m-%d %H:%M', errors='coerce')
        events['date'] = events['date'].apply(lambda x: x.replace(year=datetime.now().year))
        events['link'] = last_post[0]
        events['img'] = matching_img or last_post_img
        events['venue'] = 'Holy Bar'

    finally:
        driver.close()
        driver.quit()

    return events