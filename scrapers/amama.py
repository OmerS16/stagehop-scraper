import pandas as pd
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import re

def scrape():
    """
    Fetches and parses the Amama Jazz Room events page, extracting:
      - show_name: the title of the event
      - date: a datetime object of show date & time
      - link: relative URL to the show's detail page
      - img: URL of the show’s poster image
      - venue: hard-coded as 'Amama Jazz Room'

    Returns:
        pandas.DataFrame: one row per show, columns = 
        ['show_name', 'date', 'link', 'img', 'venue']
    """

    url = "https://www.goshow.co.il/pages/place/1780"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    events = []
    # Pattern captures "dd.mm.yyyy" then skips text until "HH:MM"
    date_pattern = r"(\d{2}\.\d{2}\.\d{4}) .* (\d{2}:\d{2})"
    
    # Each event block is in a <div class="resultData">
    for event in soup.find_all('div', class_='resultData'):
        # Title and link live inside a nested div with class 'resultLiText'
        title_container = event.find('div', class_='resultLiText')
        title = title_container.find('a').get_text(strip=True)
        
        # Raw date string lives in a <span class="closeShowDateNew">
        raw_date = event.find('span', class_='closeShowDateNew').get_text(strip=True)
        match = re.search(date_pattern, raw_date)
        # Combine captured date & time, then parse into datetime
        dt_str = f"{match.group(1)} {match.group(2)}"
        date = datetime.strptime(dt_str, '%d.%m.%Y %H:%M')

        # Relative link to the show's detail page
        link = title_container.find('a').get('href')

        # The poster image is in the previous sibling div under an <img> tag
        img = event.find_previous_sibling('div').find('a').find('img').get('src')

        events.append({'show_name':title, 'date':date, 'link':link, 'img':img, 'venue':'Amama Jazz Room'})
        
    return pd.DataFrame(events)