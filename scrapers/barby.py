import pandas as pd
from datetime import datetime
import requests

def scrape():
    url = "https://barby.co.il/api/shows/find"
    
    headers = {
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "en-US,en;q=0.9",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/91.0.4472.124 Safari/537.36",
        "Sec-CH-UA": '"Not(A:Brand";v="99", "Google Chrome";v="133", "Chromium";v="133"',
        "Sec-CH-UA-Mobile": "?0",
        "Sec-CH-UA-Platform": '"Windows"',
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "Referer": "https://barby.co.il/",
    }
    
    session = requests.Session()
    response = session.get(url, headers=headers)
    response = response.json()
    
    events = pd.DataFrame(response['returnShow']['show'])
    events = events[['showId', 'showDate', 'showTime', 'showSold', 'showSoldMaxBuy', 'showPrice', 'showName', 'showImage', 'showTitle']]
    events['link'] = events.apply(lambda x: f"https://barby.co.il/show/{x['showId']}", axis=1)
    events['showImage'] = events.apply(lambda x: f"https://images.barby.co.il/Logos/{x['showImage']}", axis=1)
    events['showDate'] = events['showDate'] + ' ' + events['showTime']
    events['showDate'] = events['showDate'].apply(lambda x: datetime.strptime(x, '%d/%m/%Y %H:%M'))
    events = events.drop('showTime', axis=1)
    events[['showSold', 'showSoldMaxBuy']] = events[['showSold', 'showSoldMaxBuy']].astype(int)
    events = events.query('showSold < showSoldMaxBuy')
    events = events.query("showName != 'מייל שירות הלקוחות'")
    
    events = events[['showName', 'showDate', 'link', 'showImage']]
    events = events.rename(columns={'showName':'show_name', 'showDate':'date', 'showImage':'img'})
    events['venue'] = 'בארבי'
    return events