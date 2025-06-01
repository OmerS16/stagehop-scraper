import pandas as pd
import requests
from bs4 import BeautifulSoup
from datetime import datetime

def scrape():
    """
    Fetches the Guitar Loft events page, follows each show’s detail link to
    grab title, date/time, image, and assembles a DataFrame with columns:
      - show_name: the event title
      - date: datetime object (day/month plus current year and time)
      - link: URL to the event detail page
      - img: URL of the event’s image
      - venue: static value 'The Guitar Loft'

    Returns:
        pandas.DataFrame: one row per show
    """

    # Main listing URL
    url = 'https://guitarloft.co.il/%d7%9c%d7%95%d7%97-%d7%9e%d7%95%d7%a4%d7%a2%d7%99%d7%9d/'
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    events = []

    # Each event appears in a div with these builder classes
    for event in soup.find_all('div', class_='jet-woo-products__item jet-woo-builder-product'):
        # Get the detail page link and fetch it
        link = event.find('a').get('href')
        details = requests.get(link)
        details = BeautifulSoup(details.text, 'html.parser')

        # Container holding title, date, image, etc.
        event_container = details.find('div', class_='ast-container')

        # Extract the show title
        title = event_container.find('span', class_='elementor-divider-separator').get_text(strip=True)
        # Skip placeholder entries
        if title == 'מופעים נוספים יתעדכנו בקרוב':
            continue

        # Date string (day/month) and clean up
        date_str = event_container.find('span', class_='jet-button__label').get_text(strip=True).strip('/.')

        # Locate the "opening doors" label to find corresponding time
        label_tag = event_container.find(lambda tag: tag.name == 'div' and tag.get_text(strip=True) == 'פתיחת דלתות')

        # The time lives in the next widget container
        time_div = label_tag.parent.find_all('div', class_='elementor-widget-container')[1]
        time_str = time_div.get_text(strip=True)

        # Combine date and time, parse, and set current year
        date = datetime.strptime(f"{date_str} {time_str}", '%d/%m %H:%M')
        date = date.replace(year=datetime.now().year)

        # Extract the event image URL
        img = event_container.find('img').get('src')

        events.append({'show_name':title, 'date':date, 'img':img, 'link':link, 'venue':'The Guitar Loft'})
    
    return pd.DataFrame(events)