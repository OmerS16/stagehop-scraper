import pandas as pd
import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime

def scrape():
    """
    Fetches the Zappa Club Tel Aviv venue page, parses each event’s embedded
    JSON-LD data, filters out sold-out shows, and returns a DataFrame with:
      - show_name: title of the event (HTML <BR> tags removed)
      - date: datetime object for the event’s start (local)
      - link: URL to the event’s detail page
      - img: URL of the event’s image
      - venue: hard-coded as 'זאפה'

    Steps:
      1. Send a GET request to the venue URL with browser-like headers.
      2. Parse the HTML with BeautifulSoup and locate all event cards.
      3. For each card:
         a. Find the <script type="application/ld+json"> tag and load its JSON.
         b. Normalize the JSON into a temporary DataFrame.
         c. If the event’s availability is 'OutOfStock', skip it.
         d. Otherwise, append the cleaned row to the main DataFrame.
      4. Trim the ISO timestamp to drop timezone, then parse into a datetime.
      5. Remove the availability column, strip any '<BR>' from the name, and add a static venue.
      6. Rename columns to ['show_name', 'date', 'img', 'link', 'venue'] and return.

    Returns:
        pandas.DataFrame with columns ['show_name', 'date', 'link', 'img', 'venue']
    """

    url = "https://www.zappa-club.co.il/city/%D7%AA%D7%9C-%D7%90%D7%91%D7%99%D7%91-249/venue/%D7%96%D7%90%D7%A4%D7%94-%D7%AA%D7%9C-%D7%90%D7%91%D7%99%D7%91-%D7%9E%D7%AA%D7%97%D7%9D-%D7%9E%D7%99%D7%93%D7%98%D7%90%D7%95%D7%9F-25734/"
    # Browser-like headers to avoid simple bot-blockers
    headers = {
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "en-US,en;q=0.9",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/91.0.4472.124 Safari/537.36",
        "Sec-CH-UA": '"Not(A:Brand";v="99", "Google Chrome";v="133", "Chromium";v="133"',
        "Sec-CH-UA-Platform": '"Windows"',
    }
    
    session = requests.Session()
    response = session.get(url, headers=headers, timeout=30)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    events = pd.DataFrame()
    
    # Each event card is a div with class 'listing-item-wrapper-inside-card'
    event_cards = soup.find_all('div', class_='listing-item-wrapper-inside-card')
    for event in event_cards:
        # Locate the JSON-LD script and parse its content
        script_tag = event.find('script', type='application/ld+json')
        if not script_tag:
            continue

        event_data = json.loads(script_tag.get_text())

        df = pd.json_normalize(event_data)

        df = df[['name', 'startDate', 'image', 'url', 'offers.availability']]

        # Skip sold-out events
        if df['offers.availability'].item() == 'OutOfStock':
            continue

        events = pd.concat((events, df), ignore_index=True)

    if events.empty:
        return events
    
    # Trim timezone suffix from ISO timestamp (e.g., remove '+00:00' or 'Z')
    events['startDate'] = events['startDate'].apply(lambda x: x[:-10])
    # Parse ISO string to datetime
    events['startDate'] = events['startDate'].apply(lambda x: datetime.fromisoformat(x))

    events = events.drop('offers.availability', axis=1)

    # Clean up the show name (remove any '<BR>' tags)
    events['name'] = events['name'].str.replace('<BR>', '')

    events['venue'] = 'זאפה'
    
    events = events.rename(columns={'name':'show_name', 'startDate':'date', 'image':'img', 'url':'link'})
    
    return events