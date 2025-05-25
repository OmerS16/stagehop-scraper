import pandas as pd
import requests
from bs4 import BeautifulSoup
from datetime import datetime

def scrape():
    url = 'https://guitarloft.co.il/%d7%9c%d7%95%d7%97-%d7%9e%d7%95%d7%a4%d7%a2%d7%99%d7%9d/'
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    events = []
    
    for event in soup.find_all('div', class_='jet-woo-products__item jet-woo-builder-product'):
        link = event.find('a').get('href')
        inner_res = requests.get(link)
        inner_soup = BeautifulSoup(inner_res.text, 'html.parser')
        event_container = inner_soup.find('div', class_='ast-container')
        title = event_container.find('span', class_='elementor-divider-separator').get_text(strip=True)
        if title == 'מופעים נוספים יתעדכנו בקרוב':
            continue
        date = event_container.find('span', class_='jet-button__label').get_text(strip=True)
        date = date.strip('/.')
        hour_container = event_container.find(lambda tag: tag.has_attr('class') and tag.get_text(strip=True) == 'פתיחת דלתות')
        hour_container = ' '.join(hour_container.get('class'))
        hour_container = event_container.find('div', class_=hour_container)
        hour_container = hour_container.parent
        hour = (hour_container.find_all('div', 'elementor-widget-container'))[1].get_text(strip=True)
        date = date + ' ' + str(hour)
        date = datetime.strptime(date, '%d/%m %H:%M')
        date = date.replace(year=datetime.now().year)
        img = event_container.find('img').get('src')
        events.append({'show_name':title, 'date':date, 'img':img, 'link':link, 'venue':'The Guitar Loft'})
    
    events = pd.DataFrame(events)
    return events