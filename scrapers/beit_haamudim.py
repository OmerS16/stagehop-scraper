import pandas as pd
from PIL import Image
import pytesseract
import re
import difflib
import requests
from datetime import datetime
from bs4 import BeautifulSoup
from io import BytesIO

def fix_typo(typo, word_list, n=1, cutoff=0.6):
    match = difflib.get_close_matches(typo, word_list, n, cutoff)
    if match:
        return match[0] if n == 1 else match
    else:
        return None
    
def convert_dates(date_str):
    if pd.notna(date_str):
        for frmt in ('%d/%m', '%d.%m'):
            try:
                date_str = datetime.strptime(date_str, frmt)
                break
            except ValueError:
                continue
        date_str = date_str.replace(year=datetime.now().year)
    return date_str

def validate_dates(date, day, year_week):
    if pd.notna(date):
        date_day = date.strftime('%A').upper()
        if day and date_day != day:
            day_num = day_map.get(day,'')
            date = f"{year_week}{day_num}"
            date = datetime.strptime(date, '%Y%U%w')
    else:
        day_num = day_map.get(day,'')
        date = f"{year_week}{day_num}"
        date = datetime.strptime(date, '%Y%U%w')
    return date
    

url = "https://www.beithaamudim.com/he"
response = requests.get(url)
soup = BeautifulSoup(response.text, 'html.parser')
img_html = soup.find('wow-image', id='img_comp-lroweu7j').find('img').get('src')
img_url = img_html[:82]
response_img = requests.get(img_url)
img = Image.open(BytesIO(response_img.content))

text = pytesseract.image_to_string(img)

lines = text.splitlines()
lines = [line for line in lines if line.strip() != ""]

pattern = re.compile(r'(\d{1,2}[./\\]\d{1,2})' r'|(\d{1,2}:\d{2})')

days = ['SUNDAY', 'MONDAY', 'TUESDAY', 'WEDNESDAY', 'THURSDAY', 'FRIDAY', 'SATURDAY']

day_map = {
    "SUNDAY": 0,
    "MONDAY": 1,
    "TUESDAY": 2,
    "WEDNESDAY": 3,
    "THURSDAY": 4,
    "FRIDAY": 5,
    "SATURDAY": 6,
}

events = []

for idx, line in enumerate(lines):
    band_name, date_line, hour_line, day_line = (None,None,None,None)
    match = pattern.search(line)
    if match:
        date_line = match.group(1)
        times = re.findall(r'\d{1,2}:\d{2}', line)
        hour_line = times
        prev_idx = idx - 1
        if prev_idx >= 0:
            day_candidate = lines[prev_idx]
            day_line = fix_typo(day_candidate, days)
        next_idx = idx + 1
        if next_idx < len(lines):
            band_name = lines[next_idx].strip()
            events.append({'title':band_name, 'date':date_line, 'hour':hour_line, 'day':day_line})
        

events = pd.DataFrame(events)

events['date'] = events['date'].apply(convert_dates)

year_week = events['date'].dt.strftime('%Y%U').mode()[0]

events['date'] = events.apply(lambda x: validate_dates(x['date'], x['day'], year_week), axis=1)
events = events.explode('hour')
events['date'] = events['date'].astype(str) + " " + events['hour']
events['date'] = events['date'].apply(lambda x: datetime.strptime(x, '%Y-%m-%d %H:%M'))
events = events.drop(['hour', 'day'], axis=1)