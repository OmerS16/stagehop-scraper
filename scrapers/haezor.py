import pandas as pd
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import re

def scrape():
    """
    Fetches the HaEzor English calendar, extracts each event’s:
      - show_name: title of the event
      - date: parsed datetime of event day & time
      - link: URL to the event detail page
      - img: URL of the background image for the event
      - venue: hard-coded as 'מועדון האזור'

    Steps:
      1. Load the calendar page and parse HTML.
      2. For each event block (.clsItem):
         a. Extract raw date text, title, description, time, and detail-page URL.
         b. Visit the detail page to grab the CSS background image URL.
      3. Use a regex to pull the image URL out of the inline `style` attribute.
      4. Convert date strings like 'Mon March 02' to a datetime (injecting current year).
      5. Combine date and hour into a single datetime column.
      6. Drop the temporary hour column and return a DataFrame.
    
    Returns:
        pandas.DataFrame with columns ['show_name', 'date', 'link', 'img', 'venue']
    """

    def convert_dates(date_str):
        """
        Parse a date string of the form 'Mon March 02' into a datetime,
        setting the year to the current year.
        """
        date_str = datetime.strptime(date_str, '%a %B %d')
        date_str = date_str.replace(year=datetime.now().year)
        return date_str
    
    # Base calendar URL
    url = 'https://haezor.com/en/calendar/'
    
    response = requests.get(url)
    
    soup = BeautifulSoup(response.text, 'html.parser')
    
    events = []

    # Regex to pull URL from CSS: url("…") or url('…')
    url_pattern = r"url\(['\"]?(.*?)['\"]?\)"
    
    # Iterate over each event listing
    for event in soup.find_all('div', class_='clsItem'):
        date = (event.find('div', class_='clsDate').get_text(strip=True))
        title = event.find('a', class_='clsYellowLink').get_text(strip=True)
        hour = event.find('div', class_='clsTime').get_text(strip=True)
        link = event.find('a', class_='clsYellowLink').get('href')

        # Visit detail page to extract background image URL from inline CSS
        details = requests.get(link)
        details = BeautifulSoup(details.text, 'html.parser')
        img = details.find('div', class_='clsBG').get('style')
        img = re.search(url_pattern, img).group(1)

        events.append({'show_name':title, 'date':date, 'hour':hour, 'link':link, 'img':img, 'venue':'מועדון האזור'})
    
    # Build DataFrame and normalize date column
    events = pd.DataFrame(events)
    events['date'] = events['date'].apply(convert_dates) # parse day/month → datetime
    # Append time string and re-parse into full datetime
    events['date'] = events['date'].astype(str) + " " + events['hour']
    events['date'] = events['date'].apply(lambda x: datetime.strptime(x, '%Y-%m-%d %H:%M'))

    events = events.drop('hour', axis=1)
    
    return events