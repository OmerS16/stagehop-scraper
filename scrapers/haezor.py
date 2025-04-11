import pandas as pd
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import re

def scrape():
    def convert_dates(date_str):
        date_str = datetime.strptime(date_str, '%a %B %d')
        date_str = date_str.replace(year=datetime.now().year)
        return date_str
    
    url = 'https://haezor.com/en/calendar/'
    
    response = requests.get(url)
    
    soup = BeautifulSoup(response.text, 'html.parser')
    
    events = []
    
    url_pattern = r"url\(['\"]?(.*?)['\"]?\)"
    
    for event in soup.find_all('div', class_='clsItem'):
        date = (event.find('div', class_='clsDate').get_text(strip=True))
        title = event.find('a', class_='clsYellowLink').get_text(strip=True)
        description = event.find('div', class_='clsDesc').get_text(strip=True)
        hour = event.find('div', class_='clsTime').get_text(strip=True)
        link = event.find('a', class_='clsYellowLink').get('href')
        inner_res = requests.get(link)
        inner_soup = BeautifulSoup(inner_res.text, 'html.parser')
        img = inner_soup.find('div', class_='clsBG').get('style')
        img = re.search(url_pattern, img).group(1)
        events.append({'show_name':title, 'date':date, 'hour':hour, 'link':link, 'img':img, 'venue':'מועדון האזור'})
        
    events = pd.DataFrame(events)
    events['date'] = events['date'].apply(convert_dates)
    events['date'] = events['date'].astype(str) + " " + events['hour']
    events['date'] = events['date'].apply(lambda x: datetime.strptime(x, '%Y-%m-%d %H:%M'))
    events = events.drop('hour', axis=1)
    return events