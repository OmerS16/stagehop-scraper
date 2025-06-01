import pandas as pd
import requests
from bs4 import BeautifulSoup
from datetime import datetime

def scrape():
    """
    Fetches Shablul’s event page, parses each show block, and extracts:
      - show_name: title of the event (skipping “הירשמו לעדכונים” placeholders)
      - date: datetime object parsed from Hebrew month names and time
      - link: full URL to the event’s detail page
      - img: full URL of the event’s poster image
      - venue: hard-coded as 'שבלול'

    Steps:
      1. Define a map to translate Hebrew month names to English (for datetime parsing).
      2. Request the main Shablul Smarticket page and parse its HTML.
      3. Iterate over each <div class="show_cube …"> block:
         a. Extract the show title; if it equals 'הירשמו לעדכונים', skip.
         b. Combine the date text and time text, remove the prefix ' בשעה'.
         c. Strip off any leading text before the first comma.
         d. Replace Hebrew month names with English equivalents.
         e. Parse the resulting string into a datetime object.
         f. Build full URLs for the show link and image (prefixing with Shablul’s domain).
      4. Collect these fields into a list of dicts and return a pandas DataFrame.

    Returns:
        pandas.DataFrame with columns ['show_name', 'date', 'link', 'img', 'venue']
    """

    # Map Hebrew month abbreviations to English month names for datetime parsing
    months_map = {'January':'ינואר', 'February':'פברואר', 'March':'מרץ', 'April':'אפריל',
                  'May':'מאי', 'June':'יוני', 'July':'יולי', 'August':'אוגוסט',
                  'September':'ספטמבר', 'October':'אוקטובר', 'November':'נובמבר', 'December':'דצמבר'}
    
    url = "https://shablul.smarticket.co.il/"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    events = []
    
    # Each show block is a <div> with class 'show_cube col-lg-4 col-sm-6 col-xs-12'
    for show_num, event in enumerate(soup.find_all('div', class_='show_cube col-lg-4 col-sm-6 col-xs-12'), 1):
        # The title lives in a <div> with id "show_name_{show_num}"
        title = event.find('div', id=f'show_name_{show_num}').get_text(strip=True)
        # Skip registration placeholders
        if title == 'הירשמו לעדכונים':
            continue

        # Extract raw date (with Hebrew month) and time text
        date = event.find('div', class_='show_date').get_text(strip=True)
        hour = event.find('div', class_='show_time').get_text(strip=True)

        # Combine and remove " בשעה" prefix
        date = date + ' ' + hour
        date = date.replace(' בשעה', '')

        # Remove any leading part before the first comma
        _, date = date.split(', ', 1)

        # Replace Hebrew month names with English equivalents
        for english, hebrew in months_map.items():
            date = date.replace(hebrew, english)
        
        # Parse into a datetime object (format: 'DD Month YYYY HH:MM')
        date = datetime.strptime(date, '%d %B %Y %H:%M')

        # Build the full link to the show’s Smarticket detail page
        link = event.find('a').get('href')
        link = 'https://shablul.smarticket.co.il/' + link

        # The image URL is in an <img> nested under a <div class="pic img-rounded">
        img = event.find('div', class_='pic img-rounded').find('img').get('data-src')
        img = 'https://shablul.smarticket.co.il/' + img
        events.append({'show_name':title, 'date':date, 'link':link, 'img':img, 'venue':'שבלול'})
    
    return pd.DataFrame(events)