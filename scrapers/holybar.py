import re
import json
import time
import calendar
import tempfile
import shutil
import unicodedata
import os
from datetime import datetime, date as Date
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from openai import OpenAI

def scrape():
    """
    Navigate Holy Bar’s Instagram to extract upcoming shows.

    Steps:
      1. Configure headless Chrome with a temporary profile.
      2. Open a sample post to dismiss overlays, then locate the latest Holy Bar post.
      3. Attempt to extract lines beginning with a weekday from the post’s body:
         - Normalize text, strip non-ASCII, and regex-match weekdays.
         - Split each matching line into date and title.
      4. If no matches found:
         a. Scan carousel images for keywords (“session” or “lineup”).
         b. Send the matching image to OpenAI to OCR extract JSON of shows.
      5. Parse or receive a list of {'show_name', 'date'} dicts.
      6. Convert dates to `datetime`, enforce current year, and build a DataFrame.
      7. Add columns:
         - link: URL of the Instagram post
         - img: matched carousel image URL (or first image)
         - venue: static 'Holy Bar'
      8. Quit Chrome and delete the temp profile.

    Returns:
        pandas.DataFrame with columns ['show_name', 'date', 'link', 'img', 'venue']
    """

    # Possible date formats found in captions
    FORMATS = ["%A, %B %d", "%A %B %d", "%A %d.%m", "%A"]
    
    # XPaths to look for post body text after the profile link
    POST_PATHS = ["../../following-sibling::*[h1]/h1", "../following-sibling::span"]
    
    def find_matches(driver, pattern):
        """
        Iterate through carousel images until we find one whose alt text matches
        the provided regex pattern. Return the src URL or None.
        """
        match = False
        
        while True:
            filtered_imgs = driver.find_elements(By.XPATH, "(//div[@class='_ap3a _aaco _aacw _aacy _aad6'])[1]/preceding::img")
            for img in filtered_imgs:
                alt = img.get_attribute('alt') or ''
                if pattern.search(alt):
                    return img.get_attribute('src')
                
            # Click "Next" if available, else break  
            try:
                next_btn = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[aria-label='Next']")))
                next_btn.click()
                time.sleep(1)
            except (NoSuchElementException, TimeoutException):
                return None

    try: 
        # Prepare temporary Chrome profile to avoid cache conflicts
        user_data_dir = tempfile.mkdtemp(prefix="chrome-profile-") 
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
        service = Service('/usr/local/bin/chromedriver')  

        try:
            print("Launching Chrome...")
            driver = webdriver.Chrome(service=service, options=chrome_options)
            print("Chrome launched successfully!")
        except Exception as e:
            print(e)

        # Load a random Holy Bar post to override login popup
        random_post = 'https://www.instagram.com/holybar/p/DF2QTMlIsGL/?img_index=1'
        driver.get(random_post)
        time.sleep(10)
        wait = WebDriverWait(driver, 5)
        button_overlay = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "svg[aria-label='Close']")))
        button_overlay.click()
        
        # Regex to detect "session(s)" or "lineup" keywords 
        pattern = re.compile(r'(sessions?|lineup)', re.IGNORECASE)
        
        # Collect all links with images on the page
        links = driver.find_elements(By.TAG_NAME, 'a')
        links_url = [[link.get_attribute('href'), link.find_element(By.TAG_NAME, 'img').get_attribute('src')] for link in links if link.find_elements(By.TAG_NAME, 'img')]
        
        # Filter to Instagram post URLs
        post_pattern = re.compile(r'https://www.instagram.com/holybar/(?:p|reel)/')
        posts = [(href,src) for href, src in links_url if post_pattern.search(href or '')]
        
        # Choose the most recent post and navigate to it
        last_post_url, last_post_img = posts[0]
        driver.get(last_post_url)
        time.sleep(15)

        # Extract caption text lines that start with a weekday name
        profile_links = driver.find_elements(By.CSS_SELECTOR, "a[href='/holybar/']")
        match = None
        for elem in profile_links:
            for path in POST_PATHS:
                try:
                    post_body = elem.find_element(By.XPATH, path).text
                except:
                    continue
                # Normalize and strip non-ASCII
                clean = unicodedata.normalize("NFKC", post_body)
                clean = re.sub(r'[^\x00-\x7F]+', '', clean)
                clean = re.sub(r'^\s+', '', clean, flags=re.MULTILINE)
                lines = re.findall(r'^(?:Sunday|Monday|Tuesday|Wednesday|Thursday|Friday|Saturday).*', clean, flags=re.MULTILINE)
                if lines:
                    match = lines
                    break
            if match:
                break
        
        events = []
        matching_img = None
                
        # If caption text yielded event lines, parse them
        if match:
            post_date = driver.find_element(By.TAG_NAME, 'time').get_attribute('datetime')
            post_date = datetime.strptime(post_date, "%Y-%m-%dT%H:%M:%S.%fZ")
            for line in match:
                # Try splitting into date and title
                for sep in [' - ', '  ']:
                    try:
                        date, title = line.split(sep, 1)
                        title = title.strip()
                        # Attempt each date format until one works
                        for frmt in FORMATS:
                            try:
                                if frmt == "%A":
                                    # Convert weekday-only to next week's date
                                    day = list(calendar.day_name).index(date) + 1
                                    year, week, _ = post_date.isocalendar()
                                    if day != 7:
                                        week += 1
                                    date = Date.fromisocalendar(year, week, day)
                                else:
                                    date = datetime.strptime(date, frmt)
                            except ValueError:
                                continue    

                        # Ensure current year
                        date = date.replace(year=datetime.now().year)
                        events.append({'show_name':title, 'date':date})
                    except:
                        continue

        else:
            # Fallback: scan images then call OpenAI to OCR
            print("No lineup found in post's body..\nActivating AI..")
            matching_img = find_matches(driver, pattern)
        
            if not matching_img:
                raise IndexError('no lineup found')
            
            client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
            try:
                response = client.responses.create(
                    model="gpt-4.1-mini",
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
        
        # Build DataFrame and finalize columns
        events = pd.DataFrame(events)
        events['date'] = pd.to_datetime(events['date'], format='%Y-%m-%d %H:%M', errors='coerce')
        events['date'] = events['date'].apply(lambda x: x.replace(year=datetime.now().year))
        events['link'] = last_post_url[0]
        events['img'] = matching_img or last_post_img
        events['venue'] = 'Holy Bar'

        return events

    finally:
        # Clean up browser and temp files
        driver.quit()
        shutil.rmtree(user_data_dir, ignore_errors=True)