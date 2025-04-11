import pandas as pd
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import re

def scrape():
    url = 'https://www.tmu-na.org.il/?CategoryID=102'
    
    response = requests.get(url)
    
    soup = BeautifulSoup(response.text, 'html.parser')
    
    date_pattern = r"(\d{2}/\d{2}) .* (\d{2}:\d{2})"
    
    events = []
    
    for event in soup.find_all('div', class_='ArticlesGalleryMatrixItem'):
        title_container = event.find('a', class_='titlesColor ArticlesGalleryTitle')
        if not title_container:
            continue
        title = title_container.get_text(strip=True)
        date = event.find('div', class_='ArticlesGallerySummary').get_text()
        date = date.splitlines()[0]
        date_match = re.search(date_pattern, date)
        date = date_match.group(1) + ' ' + date_match.group(2)
        date = datetime.strptime(date, '%d/%m %H:%M')
        date = date.replace(year=datetime.now().year)
        link = 'https://www.tmu-na.org.il/' + title_container.get('href')
        img = 'https://www.tmu-na.org.il/' + event.find('img').get('src')
        events.append({'show_name':title, 'date':date, 'link':link, 'img':img, 'venue':'תמונע'})
    
    events = pd.DataFrame(events)
    return events