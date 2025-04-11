import pandas as pd
import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime

def scrape():
    url = "https://www.zappa-club.co.il/city/%D7%AA%D7%9C-%D7%90%D7%91%D7%99%D7%91-249/venue/%D7%96%D7%90%D7%A4%D7%94-%D7%AA%D7%9C-%D7%90%D7%91%D7%99%D7%91-%D7%9E%D7%AA%D7%97%D7%9D-%D7%9E%D7%99%D7%93%D7%98%D7%90%D7%95%D7%9F-25734/"
    headers = {
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "en-US,en;q=0.9",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/91.0.4472.124 Safari/537.36",
        "Sec-CH-UA": '"Not(A:Brand";v="99", "Google Chrome";v="133", "Chromium";v="133"',
        "Sec-CH-UA-Platform": '"Windows"',
    }
    
    session = requests.Session()
    response = session.get(url, headers=headers, timeout=30)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    events = pd.DataFrame()
    
    event_cards = soup.find_all('div', class_='listing-item-wrapper-inside-card')
    for event in event_cards:
        event_json = event.find('script', type='application/ld+json')
        event_json = event_json.get_text()
        event_data = json.loads(event_json)
        df = pd.json_normalize(event_data)
        df = df[['name', 'startDate', 'image', 'url', 'offers.availability']]
        if df['offers.availability'].item() == 'OutOfStock':
            continue
        else:
            events = pd.concat((events, df), ignore_index=True)
    
    events['startDate'] = events['startDate'].apply(lambda x: x[:-10])
    events['startDate'] = events['startDate'].apply(lambda x: datetime.fromisoformat(x))
    events = events.drop('offers.availability', axis=1)
    events['name'] = events['name'].str.replace('<BR>', '')
    events['venue'] = 'זאפה'
    
    events = events.rename(columns={'name':'show_name', 'startDate':'date', 'image':'img', 'url':'link'})
    return events