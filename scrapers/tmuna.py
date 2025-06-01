import pandas as pd
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import re

def scrape():
    """
    Fetches the Temunah events page, parses each event block, and extracts:
      - show_name: event title
      - date: parsed datetime object (day/month and time, with current year)
      - link: full URL to the event’s detail page
      - img: full URL of the event’s image
      - venue: hard-coded as 'תמונע'

    Steps:
      1. Send a GET request to the Temunah events URL.
      2. Parse the response HTML with BeautifulSoup.
      3. Define a regex (date_pattern) to capture "DD/MM" and "HH:MM" from text.
      4. Iterate over each <div class="ArticlesGalleryMatrixItem">:
         a. Find the <a> with class "titlesColor ArticlesGalleryTitle"; skip if missing.
         b. Extract the title text.
         c. Get the raw date string from the first line of <div class="ArticlesGallerySummary">.
         d. Apply the regex to split into "DD/MM" and "HH:MM", then parse into a datetime.
         e. Ensure the datetime has the current year.
         f. Build the full detail-page URL by prefixing the base domain.
         g. Build the full image URL similarly.
         h. Append a dict with these fields (including venue 'תמונע') to a list.
      5. Convert the list of event dicts into a pandas DataFrame and return it.

    Returns:
        pandas.DataFrame with columns ['show_name', 'date', 'link', 'img', 'venue']
    """

    url = 'https://www.tmu-na.org.il/?CategoryID=102'
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Pattern captures "DD/MM" followed later by "HH:MM"
    date_pattern = r"(\d{2}/\d{2}) .* (\d{2}:\d{2})"
    
    events = []
    
    for event in soup.find_all('div', class_='ArticlesGalleryMatrixItem'):
        # Locate the title link; skip if not found
        title_container = event.find('a', class_='titlesColor ArticlesGalleryTitle')
        if not title_container:
            continue

        title = title_container.get_text(strip=True)

        # Extract the raw date line and apply regex to capture date & time
        date = event.find('div', class_='ArticlesGallerySummary').get_text()
        date = date.splitlines()[0]
        date_match = re.search(date_pattern, date)
        date = date_match.group(1) + ' ' + date_match.group(2)

        # Parse into datetime and set the current year
        date = datetime.strptime(date, '%d/%m %H:%M')
        date = date.replace(year=datetime.now().year)

        # Build full URLs for the detail page and image
        link = 'https://www.tmu-na.org.il/' + title_container.get('href')
        img = 'https://www.tmu-na.org.il/' + event.find('img').get('src')
        events.append({'show_name':title, 'date':date, 'link':link, 'img':img, 'venue':'תמונע'})
    
    return pd.DataFrame(events)