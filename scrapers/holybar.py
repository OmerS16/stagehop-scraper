from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import pandas as pd
from PIL import Image, ImageOps
import pytesseract
import re
import requests
from datetime import datetime
from io import BytesIO
import time
import unicodedata

def extract_info(part, img_df):
    if part == 'left':
        df = img_df[img_df['left'] < segment_threshold].copy()
    if part == 'right':
        df = img_df[img_df['left'] >= segment_threshold].copy()
    df = df.sort_values(['top', 'left'])
    df = df.reset_index()
    df['dates'] = df['dates'].notna()
    df_dates_index = df.index[df['dates']]
    df_results = []
    for i in df_dates_index:
        subsequent_rows = []
        top_val = df.loc[i+1, 'top']
        candidate_rows = df.index[df.index > i]
        for j in candidate_rows:
            if df.loc[j, 'top'] != top_val:
                break
            else:
                subsequent_rows.append(df.loc[j, 'text'])
        df_results.append({'date':df.loc[i, 'text'], 'title':subsequent_rows})
    return df_results

def convert_dates(date_str):
    date_str = datetime.strptime(date_str, '%d.%m')
    date_str = date_str.replace(year=datetime.now().year)
    return date_str

chrome_options = Options()
# chrome_options.add_argument("--headless")
# chrome_options.add_argument("--disable-gpu")
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

# last_post = posts[1]
last_post = 'https://www.instagram.com/holybar/p/DGILdM2IGUs/'
driver.get(last_post)
time.sleep(5)

images = driver.find_elements(By.TAG_NAME, "img")

# for img in images:
#     img_text = img.get_attribute('alt')
#     img_text_clean = unicodedata.normalize("NFKC", img_text)
#     img_text_clean = re.sub(r'[^\x00-\x7F]+', '', img_text_clean)
#     img_text_clean = re.sub(r'^\s+', '', img_text_clean, flags=re.MULTILINE)
#     lineup = pattern.search(img_text_clean)
#     if lineup:
#         break

# day_pattern = r'^(?:Sunday|Monday|Tuesday|Wednesday|Thursday|Friday|Saturday).*'
# matches = re.findall(day_pattern, img_text_clean, flags=re.MULTILINE)
matches = 0

events = []

if matches:
    ...
    # for line in matches:
    #     date, title = line.split(' - ', 1)
    #     title = title.strip()
    #     date = date + ' 20:45'
    #     date = datetime.strptime(date, '%A, %B %d %H:%M')
    #     date = date.replace(year=datetime.now().year)
    #     events.append({'show_name':title, 'date':date, 'link':last_post})
    # events = pd.DataFrame(events)

else:
    matching_images = [img for img in images if pattern.search(img.get_attribute('alt') or '')]

    if not matching_images:
        raise IndexError('no lineup found')
        
    img_url = matching_images[0].get_attribute("src")
    
    response_img = requests.get(img_url)
    img = Image.open(BytesIO(response_img.content))
    
    img = ImageOps.grayscale(img)
    img = ImageOps.autocontrast(img)
    img = img.point(lambda x: 0 if x < 128 else 255, '1')
    
    custom_config = r'--oem 3 --psm 6'
    
    img_df = pytesseract.image_to_data(img, config=custom_config, lang='eng', output_type=pytesseract.Output.DATAFRAME)
    img_df = img_df.query('conf > 80')
    
    date_pattern = re.compile(r'(\d{1,2}[./\\]\d{1,2})')
    img_df['dates'] = img_df["text"].str.findall(date_pattern)
    img_df = img_df.explode('dates')
    img_df_dates = img_df.dropna(subset='dates')
    img_df_dates = img_df_dates.sort_values('left')
    segment_threshold = (img_df_dates['left'].min() + img_df_dates['left'].max()) / 2
        
    df_left = extract_info('left', img_df)
    df_right = extract_info('right', img_df)
    
    df = df_left + df_right
    df = pd.DataFrame(df)
    
    df['title'] = df['title'].str.join(" ")
    df['date'] = df['date'].apply(convert_dates)
    df['hour'] = '20:45'
    df['date'] = df['date'].astype(str) + " " + df['hour']
    df['date'] = df['date'].apply(lambda x: datetime.strptime(x, '%Y-%m-%d %H:%M'))
    df = df.drop('hour', axis=1)
