import pandas as pd
import requests
from bs4 import BeautifulSoup
from datetime import datetime

def scrape():
    
    FORMATS = [
        '%d.%m.%Y %H:%M',
        '%d/%m/%Y %H:%M',
        ]
    
    url = 'https://tassatlv.co.il/collections/%D7%94%D7%95%D7%A4%D7%A2%D7%95%D7%AA'
    
    response = requests.get(url)
    
    soup = BeautifulSoup(response.text, 'html.parser')
    
    events = []
    
    for event in soup.find_all('div', class_='card custom-product-card-template--17836924371080__main-collection product-card product-card--card grid leading-none relative overflow-hidden'):
        title_container = event.find('a', class_='block relative media media--adapt overflow-hidden')
        title = title_container.find('img').get('alt')
        link = title_container.get('href')
        link = 'https://tassatlv.co.il/' + link
        inner_res = requests.get(link)
        inner_soup = BeautifulSoup(inner_res.text, 'html.parser')
        date = inner_soup.find('p', class_='custom-icon-2 product__text rte text-base').get_text(strip=True)
        date = date.replace(': תאריך', '')
        hour = inner_soup.find('p', class_='custom-icon-3 product__text rte text-base').get_text(strip=True)
        hour = hour.replace(': תחילת מופע', '')
        date = date + ' ' + hour
        for frmt in FORMATS:
            try:
                date = datetime.strptime(date, frmt)
                break
            except ValueError:
                continue
        img = title_container.find('img').get('src')
        events.append({'show_name':title, 'date':date, 'link':link, 'img':img, 'venue':'TASSA'})
        
    events = pd.DataFrame(events)
    return events