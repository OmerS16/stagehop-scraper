import pandas as pd
import requests
from bs4 import BeautifulSoup
from datetime import datetime

def scrape():
    """
    Fetches the Beit Hayotzer events page, parses each <article> block, and extracts:
      - show_name: event title
      - date: combined datetime of show date & time
      - link: URL to the event details
      - img: URL of the event’s featured image
      - venue: hard-coded as 'בית היוצר'

    Returns:
        pandas.DataFrame: one row per event with columns
        ['show_name', 'date', 'link', 'img', 'venue']
    """

    url = 'https://bama.acum.org.il/'
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    events = []
    # Each event is wrapped in an <article> tag
    for event in soup.find_all('article'):
        # Title and link live under an <h2> with specific Elementor classes
        title_container = event.find('h2', class_='elementor-heading-title elementor-size-default')
        title = title_container.find('a').get_text(strip=True)

        # Date string in one <div>, time string in another
        date_str = event.find('div', class_='elementor-element elementor-element-fd06aae elementor-widget elementor-widget-text-editor').get_text(strip=True)
        hour_str = event.find('div', class_='elementor-element elementor-element-fc39e22 elementor-widget elementor-widget-text-editor').get_text(strip=True)

        # Remove prefix "תחילת מופע: " from the time text
        hour = hour.replace('תחילת מופע: ', '')

        # Combine and parse into a datetime object (format: 'DD/MM/YYYY HH:MM')
        date = datetime.strptime(f"{date_str} {hour_str}", '%d/%m/%Y %H:%M')

        # Extract the href for the event details page
        link = title_container.find('a').get('href')

        # Featured image is nested in a div with Elementor image widget classes
        img = event.find('div', class_='elementor-element elementor-element-f90359f elementor-widget elementor-widget-theme-post-featured-image elementor-widget-image').find('img').get('src')

        events.append({'show_name':title, 'date':date, 'link':link, 'img':img, 'venue':'בית היוצר'})
        
    return pd.DataFrame(events)