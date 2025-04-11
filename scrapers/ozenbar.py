import pandas as pd
import requests
from bs4 import BeautifulSoup
from datetime import datetime

def scrape():
    def convert_dates(date_str):
        date_str = datetime.strptime(date_str, '%d.%m')
        date_str = date_str.replace(year=datetime.now().year)
        return date_str
    
    url = "https://ozentelaviv.com/"
    
    response = requests.get(url)
    
    soup = BeautifulSoup(response.text, 'html.parser')
    
    events = []
    
    for event in soup.find_all('a', class_='ozen-partial ozen-partial__event-block', attrs={'data-terms':'34,20'}):
        event_body = event.find('div', class_='ozen-partial__event-block_body')
        title = event_body.find('strong').get_text(strip=True)
        date = event_body.find('time')
        date = date.find(string=True, recursive=False).strip()
        date, hour = date.split(' | ')
        link = event.get('href')
        img = event.find('img').get('src')
        events.append({'show_name':title, 'date':date, 'hour':hour, 'link':link, 'img':img, 'venue':'מועדון האוזן'})
        
    events = pd.DataFrame(events)
    events['date'] = events['date'].apply(convert_dates)
    events['date'] = events['date'].astype(str) + " " + events['hour']
    events['date'] = events['date'].apply(lambda x: datetime.strptime(x, '%Y-%m-%d %H:%M'))
    events = events.drop('hour', axis=1)
    return events