import pandas as pd
import requests
from bs4 import BeautifulSoup
from datetime import datetime

def scrape():
    months_map = {'January':'ינואר', 'February':'פברואר', 'March':'מרץ', 'April':'אפריל',
                  'May':'מאי', 'June':'יוני', 'July':'יולי', 'August':'אוגוסט',
                  'September':'ספטמבר', 'October':'אוקטובר', 'November':'נובמבר', 'December':'דצמבר'}
    
    url = "https://shablul.smarticket.co.il/"
    
    response = requests.get(url)
    
    soup = BeautifulSoup(response.text, 'html.parser')
    
    events = []
    
    for show_num, event in enumerate(soup.find_all('div', class_='show_cube col-lg-4 col-sm-6 col-xs-12'), 1):
        title = event.find('div', id=f'show_name_{show_num}').get_text(strip=True)
        if title == 'הירשמו לעדכונים':
            continue
        date = event.find('div', class_='show_date').get_text(strip=True)
        hour = event.find('div', class_='show_time').get_text(strip=True)
        date = date + ' ' + hour
        date = date.replace(' בשעה', '')
        _, date = date.split(', ', 1)
        for english, hebrew in months_map.items():
            date = date.replace(hebrew, english)
        date = datetime.strptime(date, '%d %B %Y %H:%M')
        link = event.find('a').get('href')
        link = 'https://shablul.smarticket.co.il/' + link
        img = event.find('div', class_='pic img-rounded').find('img').get('data-src')
        img = 'https://shablul.smarticket.co.il/' + img
        events.append({'show_name':title, 'date':date, 'link':link, 'img':img, 'venue':'שבלול'})
    
    events = pd.DataFrame(events)
    return events