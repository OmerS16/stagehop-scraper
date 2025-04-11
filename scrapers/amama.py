import pandas as pd
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import re
import json

def scrape():
    url = "https://www.goshow.co.il/pages/place/1780"
    
    response = requests.get(url)
    
    soup = BeautifulSoup(response.text, 'html.parser')
    
    events = []
    
    date_pattern = r"(\d{2}\.\d{2}\.\d{4}) .* (\d{2}:\d{2})"
    
    for event in soup.find_all('div', class_='resultData'):
        title_container = event.find('div', class_='resultLiText')
        title = title_container.find('a').get_text(strip=True)
        date = event.find('span', class_='closeShowDateNew').get_text(strip=True)
        date_match = re.search(date_pattern, date)
        date = date_match.group(1) + ' ' + date_match.group(2)
        date = datetime.strptime(date, '%d.%m.%Y %H:%M')
        link = title_container.find('a').get('href')
        img = event.find_previous_sibling('div').find('a').find('img').get('src')
        events.append({'show_name':title, 'date':date, 'link':link, 'img':img, 'venue':'Amama Jazz Room'})
        
    events = pd.DataFrame(events)
    return events