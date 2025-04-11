import pandas as pd
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import re

def scrape():
    months_map = {
        "בינו׳": "January", "בפבר׳": "February", "במרץ": "March", "באפר׳": "April",
        "במאי": "May", "ביונ׳": "June", "ביול׳": "July", "באוג׳": "August",
        "בספט׳": "September", "באוק׳": "October", "בנוב׳": "November", "בדצמ׳": "December"
    }
    
    url = "https://www.cafeivri.co.il/event-list"
    
    response = requests.get(url)
    
    soup = BeautifulSoup(response.text, 'html.parser')
    
    events = []
    
    for event in soup.find_all('div', class_='mq7Mp3'):
        title_container = event.find('a', class_='DjQEyU')
        title = title_container.get_text(strip=True)
        if title == 'ערב מצחק בעברי':
            continue
        date = event.find('div', class_='v2vbgt pRRkmP').get_text(strip=True)
        _, date = date.split(', ')
        for hebrew, english in months_map.items():
            date = date.replace(hebrew, english)
        date = datetime.strptime(date, '%d %B')
        date = date.replace(year=datetime.now().year)
        link = title_container.get('href')
        img = event.find('img').get('src')
        img = img.replace('blur_2,', '')
        img = re.sub(r"w_\d+", "w_500", img)
        img = re.sub(r"h_\d+", "h_300", img)
        events.append({'show_name':title, 'date':date, 'link':link, 'img':img, 'venue':'קפה עברי'})
    
    events = pd.DataFrame(events)
    return events