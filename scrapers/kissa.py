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
from openai import OpenAI
import os, tempfile, shutil
import json

def scrape():
    """
    Navigate Jazz Kissa’s Instagram to pull the latest post, find the image
    containing the current month’s lineup, and ask OpenAI to extract show names
    and dates.

    Steps:
      1. Launch headless Chrome with a temporary user profile.
      2. Open a known Jazz Kissa post to collect all post URLs.
      3. Load the second-most-recent post and slide through carousel images until
         one matches the current month & year in its alt text.
      4. Send that lineup image to OpenAI with a prompt to return JSON of
         {'show_name', 'date', 'hour'} entries.
      5. Parse the JSON into a DataFrame, combine date & hour into a datetime
         column, and add metadata (link, img, venue).
      6. Clean up browser and temporary files.

    Returns:
        pandas.DataFrame with columns:
        ['show_name', 'date', 'link', 'img', 'venue']
    """

    def find_matches(driver, pattern):
        """
        Advance through the Instagram carousel until an <img> alt-text matches
        the regex `pattern`. Returns the matching image URL or False.
        """
        wait = WebDriverWait(driver, 5)
        
        while True:
            images = driver.find_elements(By.TAG_NAME, "img")
            for img in images:
                alt = img.get_attribute('alt') or ''
                if pattern.search(alt):
                    return img.get_attribute('src')
                
            try:
                # Click the "Next" button in the carousel
                next_btn = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[aria-label='Next']")))
                next_btn.click()
                time.sleep(1)
            except (NoSuchElementException, TimeoutException):
                break
            
        return False
    try:
        # Prepare temporary Chrome profile to avoid cache conflicts
        user_data_dir = tempfile.mkdtemp(prefix="chrome-data-")
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

        # Go to a sample post to gather all Jazz Kissa post URLs
        driver.get('https://www.instagram.com/jazzkissa.telaviv/p/DH50V0fNiq-/?img_index=1')
        time.sleep(20)
        links = [a.get_attribute('href') for a in driver.find_elements(By.TAG_NAME, 'a')]
        post_pattern = re.compile(r'https://www.instagram.com/jazzkissa.telaviv/p/')
        posts = [url for url in links if post_pattern.search(url or '')]
        
        # Visit the second-most-recent post
        last_post = posts[1]
        driver.get(last_post)
        time.sleep(5)

        # Find the carousel image matching current month & year
        today = datetime.today()
        current_month = today.strftime('%B')
        current_year = today.strftime('%Y')

        pattern = re.compile(rf'{current_month} {current_year}', re.IGNORECASE)
        
        matching_img = find_matches(driver, pattern)
        if not matching_img:
            raise IndexError('no lineup found')
        
        # Ask OpenAI to extract show details from the matching image
        client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
        try:
            response = client.responses.create(
                model="gpt-4.1-mini",
                input=[{
                    "role": "user",
                    "content": [
                        {"type": "input_text", "text": "Extract all the live shows' or jam sessions (not records) names and dates to json with keys: show_name, date, hour. if the show doesn't have an hour next to it, the default is 22:00. date format is %Y-%m-%d. Do not add any text to the response so I could convert your response to json."},
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
        events['date'] = pd.to_datetime(events['date'] + ' ' + events['hour'], format='%Y-%m-%d %H:%M')
        events = events.drop('hour', axis=1)
        events['link'] = last_post
        events['img'] = matching_img
        events['venue'] = 'Jazz Kissa'

    finally:
        # Ensure cleanup of browser process and temp data
        driver.quit()
        shutil.rmtree(user_data_dir, ignore_errors=True)

    return events