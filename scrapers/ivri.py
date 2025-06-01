import pandas as pd
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import re

def scrape():
    """
    Fetches Cafe Ivri event listings, translates Hebrew month abbreviations,
    visits each event’s detail page to extract show time, cleans image URLs,
    and returns a DataFrame with:
      - show_name: event title (skips shows containing 'מצחק')
      - date: full datetime object for the show
      - link: URL to the event’s page
      - img: cleaned poster image URL
      - venue: static 'קפה עברי'

    Returns:
        pandas.DataFrame
    """

    # Map Hebrew month abbreviations to English month names for parsing
    months_map = {
        "בינו׳": "January", "בפבר׳": "February", "במרץ": "March", "באפר׳": "April",
        "במאי": "May", "ביוני": "June", "ביולי": "July", "באוג׳": "August",
        "בספט׳": "September", "באוק׳": "October", "בנוב׳": "November", "בדצמ׳": "December"
    }
    
    # Main event list page
    url = "https://www.cafeivri.co.il/event-list"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    events = []
    
    # Each event is inside a div.mq7Mp3
    for event in soup.find_all('div', class_='mq7Mp3'):
        title_container = event.find('a', class_='DjQEyU')
        title = title_container.get_text(strip=True)

        # Skip comedy shows (contain 'מצחק')
        if "מצחק" in title:
            continue

        # Extract and normalize the date string
        date = event.find('div', class_='v2vbgt pRRkmP').get_text(strip=True)
        # Remove prefix before comma
        _, date = date.split(', ')
        for hebrew, english in months_map.items():
            date = date.replace(hebrew, english)
        
        # Visit detail page to fetch show time
        link = title_container.get('href')
        details = requests.get(link)
        details = BeautifulSoup(details.text, 'html.parser')

        # Attempt to extract time via regex; fallback to alternate <p> element
        hour = details.find('p', class_='W0S903 gUQoiT eR02y5 PUuajU').get_text(strip=True)
        match = re.search(r'\bמופע[\-\u2013](\d+)\b', hour)
        if match:
            hour = match.group(1)
        else:
            hour = details.find('p', class_='ALQLki tN7ge3').get_text(strip=True)
            # Strip leading label and trailing parts
            hour = hour.split(', ', 1)[1].split(' – ', 1)[0]

        # Ensure minutes are present
        if ':' not in hour:
            hour += ':00'
        
        # Parse into datetime and inject current year
        date = datetime.strptime(f"{date} {hour}", '%d %B %H:%M')
        date = date.replace(year=datetime.now().year)
        
        # Clean image URL for consistent dimensions
        img = event.find('img').get('src')
        img = img.replace('blur_2,', '')
        img = re.sub(r"w_\d+", "w_500", img)
        img = re.sub(r"h_\d+", "h_300", img)

        events.append({'show_name':title, 'date':date, 'link':link, 'img':img, 'venue':'קפה עברי'})
    
    # Convert to DataFrame for downstream concatenation
    return pd.DataFrame(events)