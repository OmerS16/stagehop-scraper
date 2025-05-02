import pandas as pd
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import re

def scrape():
    months_map = {
        "בינו׳": "January", "בפבר׳": "February", "במרץ": "March", "באפר׳": "April",
        "במאי": "May", "ביוני": "June", "ביולי": "July", "באוג׳": "August",
        "בספט׳": "September", "באוק׳": "October", "בנוב׳": "November", "בדצמ׳": "December"
    }
    
    url = "https://www.cafeivri.co.il/event-list"
    
    response = requests.get(url)
    
    soup = BeautifulSoup(response.text, 'html.parser')
    
    events = []
    
    for event in soup.find_all('div', class_='mq7Mp3'):
        title_container = event.find('a', class_='DjQEyU')
        title = title_container.get_text(strip=True)
        if "מצחק" in title:
            continue
        date = event.find('div', class_='v2vbgt pRRkmP').get_text(strip=True)
        _, date = date.split(', ')
        for hebrew, english in months_map.items():
            date = date.replace(hebrew, english)
        link = title_container.get('href')
        inner_res = requests.get(link)
        inner_soup = BeautifulSoup(inner_res.text, 'html.parser')
        inner_res_html = inner_res.content
        hour = inner_soup.find('p', class_='W0S903 gUQoiT eR02y5 PUuajU').get_text(strip=True)
        pattern = re.compile(r'\bמופע[\-\u2013](\d+)\b')
        match = re.search(pattern, hour)
        if match:
            hour = match.group(1)
        else:
            hour = inner_soup.find('p', class_='ALQLki tN7ge3').get_text(strip=True)
            hour = hour.split(', ', 1)[1].split(' – ', 1)[0]
        if ':' not in hour:
            hour += ':00'
        date = date + ' ' + hour
        date = datetime.strptime(date, '%d %B %H:%M')
        date = date.replace(year=datetime.now().year)
        
        img = event.find('img').get('src')
        img = img.replace('blur_2,', '')
        img = re.sub(r"w_\d+", "w_500", img)
        img = re.sub(r"h_\d+", "h_300", img)
        events.append({'show_name':title, 'date':date, 'link':link, 'img':img, 'venue':'קפה עברי'})
    
    events = pd.DataFrame(events)
    return events