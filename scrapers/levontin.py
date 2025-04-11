import pandas as pd
import requests
from bs4 import BeautifulSoup
from datetime import datetime

def scrape():
    def convert_dates(date_str):
        date_str = datetime.strptime(date_str, '%d/%m')
        date_str = date_str.replace(year=datetime.now().year)
        return date_str
    
    url = "https://levontin7.com"
    
    response = requests.get(url)
    
    soup = BeautifulSoup(response.text, 'html.parser')
    
    events = []
    
    soup_filtered = soup.find('div', class_='fat-event-sc event-masonry fat-padding-15')
    
    for event in soup_filtered.find_all('div', class_='fat-event-title'):
        link = event.find('a').get('href')
        inner_res = requests.get(link)
        inner_soup = BeautifulSoup(inner_res.text, 'html.parser')
        title = inner_soup.find('div', 'fat-event-title').get_text(strip=True)
        image = inner_soup.find('div', 'fat-event-thumb').get('style', '')[22:-1]
        parent = event.parent.parent.parent.parent
        date = parent.get('data-single-time')
        hour, date = date.split(' - ')
        events.append({'show_name':title, 'date':date, 'hour':hour, 'link':link, 'img':image, 'venue':'לבונטין 7'})
        
    events = pd.DataFrame(events)
    events['date'] = events['date'].apply(convert_dates)
    events['date'] = events['date'].astype(str) + " " + events['hour']
    events['date'] = events['date'].apply(lambda x: datetime.strptime(x, '%Y-%m-%d %H:%M'))
    events = events.drop('hour', axis=1)
    return events