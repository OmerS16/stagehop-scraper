import pandas as pd
import requests
from bs4 import BeautifulSoup
from datetime import datetime

def scrape():
    """
    Fetches the Ozen Bar homepage, extracts event blocks matching specific
    terms (data-terms '34,20'), and returns a DataFrame with:
      - show_name: the event title
      - date: datetime object combining the day/month (with current year) and time
      - link: URL to the event’s detail page
      - img: URL of the event’s image
      - venue: static 'מועדון האוזן'

    Steps:
      1. Define convert_dates to parse 'DD.MM' strings into datetime with current year.
      2. Request the main page and parse HTML with BeautifulSoup.
      3. For each <a> tag whose class includes 'ozen-partial__event-block' and data-terms '34,20':
         a. Locate the inner <div> containing title and <time> text.
         b. Extract the title from the <strong> tag.
         c. Grab the raw date/time string, split on ' | ' to separate date and hour.
         d. Extract the event’s link (href) and image src.
         e. Append these fields to a list with a fixed venue name.
      4. Convert the list to a pandas DataFrame.
      5. Apply convert_dates to the date column, append the hour string,
         and parse the combined string into a full datetime.
      6. Drop the intermediate 'hour' column and return the DataFrame.

    Returns:
        pandas.DataFrame with columns ['show_name', 'date', 'link', 'img', 'venue']
    """

    def convert_dates(date_str):
        """
        Parse a date string in 'DD.MM' format and set its year to the current year.
        """
        date_str = datetime.strptime(date_str, '%d.%m')
        date_str = date_str.replace(year=datetime.now().year)
        return date_str
    
    url = "https://ozentelaviv.com/"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    events = []
    
    # Find all <a> tags that represent event blocks with the desired data-terms
    for event in soup.find_all('a', class_='ozen-partial ozen-partial__event-block', attrs={'data-terms':'34,20'}):
        # Inside each event block, find the div containing title and time
        event_body = event.find('div', class_='ozen-partial__event-block_body')
        title = event_body.find('strong').get_text(strip=True)

        # <time> tag holds a string like "DD.MM | HH:MM"
        date = event_body.find('time')
        date = date.find(string=True, recursive=False).strip()
        date, hour = date.split(' | ')

        link = event.get('href')
        img = event.find('img').get('src')

        events.append({'show_name':title, 'date':date, 'hour':hour, 'link':link, 'img':img, 'venue':'מועדון האוזן'})
        
    events = pd.DataFrame(events)
    # Parse 'DD/MM' into a datetime with current year
    events['date'] = events['date'].apply(convert_dates)
    events['date'] = events['date'].astype(str) + " " + events['hour']
    events['date'] = events['date'].apply(lambda x: datetime.strptime(x, '%Y-%m-%d %H:%M'))
    events = events.drop('hour', axis=1)
    return events