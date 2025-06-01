import pandas as pd
from datetime import datetime
import requests

def scrape():
    """
    Calls the Barby shows API, transforms the JSON payload into a DataFrame
    with only available shows, and normalizes column names for downstream use.

    Steps:
      1. Perform HTTP GET to the /api/shows/find endpoint with browser-like headers.
      2. Parse JSON and extract the list of shows.
      3. Build a DataFrame and select only the fields we care about:
         - showId, showDate, showTime, showSold, showSoldMaxBuy, showPrice,
           showName, showImage, showTitle
      4. Construct:
         - link: URL to the show’s details page
         - showImage: full URL to the show’s image asset
      5. Merge showDate & showTime into a single datetime column.
      6. Convert numeric columns to int and filter out sold-out events.
      7. Drop unused columns, rename for consistency, and add a static venue name.

    Returns:
        pandas.DataFrame with columns:
          ['show_name', 'date', 'link', 'img', 'venue']
    """

    # API endpoint for Barby shows
    url = "https://barby.co.il/api/shows/find"

    # Mimic a real browser to avoid simple bot-blockers
    headers = {
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "en-US,en;q=0.9",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/91.0.4472.124 Safari/537.36",
        "Sec-CH-UA": '"Not(A:Brand";v="99", "Google Chrome";v="133", "Chromium";v="133"',
        "Sec-CH-UA-Mobile": "?0",
        "Sec-CH-UA-Platform": '"Windows"',
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "Referer": "https://barby.co.il/",
    }

    # Fetch & parse JSON
    session = requests.Session()
    response = session.get(url, headers=headers).json()
    
    # Load raw shows list into a DataFrame
    events = pd.DataFrame(response['returnShow']['show'])
    
    # Keep only relevant columns for our use case
    events = events[['showId', 'showDate', 'showTime', 'showSold', 'showSoldMaxBuy', 'showPrice', 'showName', 'showImage', 'showTitle']]

    # Build a direct link to the show page and full image URL
    events['link'] = events['showId'].apply(lambda id: f"https://barby.co.il/show/{id}")
    events['showImage'] = events['showImage'].apply(lambda img: f"https://images.barby.co.il/Logos/{img}")

    # Combine date + time strings and parse into a datetime object
    events['showDate'] = events['showDate'] + ' ' + events['showTime']
    events['showDate'] = events['showDate'].apply(lambda x: datetime.strptime(x, '%d/%m/%Y %H:%M'))
    events = events.drop('showTime', axis=1)

    # Ensure numeric fields are ints, then filter out sold-out shows
    events[['showSold', 'showSoldMaxBuy']] = events[['showSold', 'showSoldMaxBuy']].astype(int)
    events = events.query('showSold < showSoldMaxBuy')
    events = events.query("showName != 'מייל שירות הלקוחות'")
    
    # Drop extras, rename for consistency with other scrapers
    events = events[['showName', 'showDate', 'link', 'showImage']]
    events = events.rename(columns={'showName':'show_name', 'showDate':'date', 'showImage':'img'})
    events['venue'] = 'בארבי'

    return events