import pandas as pd
import requests
from bs4 import BeautifulSoup
from datetime import datetime

def scrape():
    """
    Fetches Levontin 7’s main page, parses each event block, and extracts:
      - show_name: event title
      - date: datetime object combining date & time
      - link: URL to the event’s detail page
      - img: URL of the event’s thumbnail image
      - venue: hard-coded as 'לבונטין 7'

    Steps:
      1. Define a helper (convert_dates) to parse 'DD/MM' into a datetime with the current year.
      2. Send a GET request to Levontin 7’s homepage.
      3. Locate the container with class 'fat-event-sc event-masonry fat-padding-15'.
      4. For each event title div inside that container:
         a. Extract the detail-page link.
         b. Load the detail page and parse its HTML.
         c. Extract the event title from the inner 'fat-event-title' div.
         d. Extract the background-image URL from the 'fat-event-thumb' style attribute.
         e. Traverse up the DOM from the title div to grab the 'data-single-time' attribute,
            which contains "HH:MM - DD/MM".
         f. Split that string into hour and date, and accumulate all fields in a dict.
      5. Convert the list of dicts into a DataFrame.
      6. Use convert_dates to turn 'DD/MM' into a datetime, append the hour,
         then parse the combined string into a full datetime object.
      7. Drop the intermediate 'hour' column and return the DataFrame.

    Returns:
        pandas.DataFrame with columns ['show_name', 'date', 'link', 'img', 'venue']
    """

    def convert_dates(date_str):
        """
        Parse a date string in 'DD/MM' format and set its year to the current year.
        """
        date_str = datetime.strptime(date_str, '%d/%m')
        date_str = date_str.replace(year=datetime.now().year)
        return date_str
    
    url = "https://levontin7.com"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    events = []
    
    # Find the main event grid by its class name
    soup_filtered = soup.find('div', class_='fat-event-sc event-masonry fat-padding-15')
    
    # Iterate over each event title container
    for event in soup_filtered.find_all('div', class_='fat-event-title'):
        # Extract detail page link
        link = event.find('a').get('href')

        # Load detail page to grab title and image
        inner_res = requests.get(link)
        inner_soup = BeautifulSoup(inner_res.text, 'html.parser')

        # Title is in a div with class 'fat-event-title'
        title = inner_soup.find('div', 'fat-event-title').get_text(strip=True)

        # Image URL is embedded in the inline style of 'fat-event-thumb'
        # The style string looks like "background-image:url('...')"
        image = inner_soup.find('div', 'fat-event-thumb').get('style', '')[22:-1]

        # The date/time is stored in a data attribute on a parent element:
        # e.g., data-single-time="HH:MM - DD/MM"
        parent = event.parent.parent.parent.parent
        date = parent.get('data-single-time')
        hour, date = date.split(' - ')

        events.append({'show_name':title, 'date':date, 'hour':hour, 'link':link, 'img':image, 'venue':'לבונטין 7'})
        
    events = pd.DataFrame(events)
    # Parse 'DD/MM' into a datetime with current year
    events['date'] = events['date'].apply(convert_dates)
    events['date'] = events['date'].astype(str) + " " + events['hour']
    events['date'] = events['date'].apply(lambda x: datetime.strptime(x, '%Y-%m-%d %H:%M'))
    events = events.drop('hour', axis=1)

    return events