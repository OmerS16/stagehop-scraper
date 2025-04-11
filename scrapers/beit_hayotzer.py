import pandas as pd
import requests
from bs4 import BeautifulSoup
from datetime import datetime

def scrape():
    url = 'https://bama.acum.org.il/'
    
    response = requests.get(url)
    
    soup = BeautifulSoup(response.text, 'html.parser')
    
    events = []
    
    for event in soup.find_all('article'):
        title_container = event.find('h2', class_='elementor-heading-title elementor-size-default')
        title = title_container.find('a').get_text(strip=True)
        date = event.find('div', class_='elementor-element elementor-element-fd06aae elementor-widget elementor-widget-text-editor').get_text(strip=True)
        hour = event.find('div', class_='elementor-element elementor-element-fc39e22 elementor-widget elementor-widget-text-editor').get_text(strip=True)
        hour = hour.replace('תחילת מופע: ', '')
        date = date + ' ' + hour
        date = datetime.strptime(date, '%d/%m/%Y %H:%M')
        link = title_container.find('a').get('href')
        img = event.find('div', class_='elementor-element elementor-element-f90359f elementor-widget elementor-widget-theme-post-featured-image elementor-widget-image').find('img').get('src')
        events.append({'show_name':title, 'date':date, 'link':link, 'img':img, 'venue':'בית היוצר'})
        
    events = pd.DataFrame(events)
    return events