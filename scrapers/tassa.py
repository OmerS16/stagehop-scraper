import pandas as pd
import requests
from bs4 import BeautifulSoup
from datetime import datetime

def scrape():
    """
    Fetches the TASSA TLV “הופעות” collection page, visits each individual
    event detail page, and extracts:
      - show_name: event title (from the image alt text)
      - date: parsed datetime combining the date and start time
      - link: full URL to the event’s detail page
      - img: URL of the event’s poster image
      - venue: hard-coded as 'TASSA'

    Steps:
      1. Define possible datetime formats (dd.mm.yyyy HH:MM and dd/mm/yyyy HH:MM).
      2. Send a GET request to the main “הופעות” collection URL.
      3. Locate each event card by its CSS classes.
      4. For each card:
         a. Extract title and relative link from the <a> wrapper and build the full URL.
         b. Request the detail page, then find the `<p>` tags for date and time.
         c. Remove Hebrew labels (": תאריך" and ": תחילת מופע") and concatenate.
         d. Try parsing the combined string using the defined datetime formats.
         e. Grab the image src from the same `<img>` tag used for the alt text.
      5. Accumulate all events in a list of dicts and convert to a DataFrame.

    Returns:
        pandas.DataFrame with columns ['show_name', 'date', 'link', 'img', 'venue']
    """
    
    FORMATS = [
        '%d.%m.%Y %H:%M',
        '%d/%m/%Y %H:%M',
    ]
    
    # Main “הופעות” (shows) collection page on TASSA TLV
    url = 'https://tassatlv.co.il/collections/%D7%94%D7%95%D7%A4%D7%A2%D7%95%D7%AA'
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    events = []
    
    # Each event card has a very specific set of CSS classes
    for event in soup.find_all('div', class_='card custom-product-card-template--17836924371080__main-collection product-card product-card--card grid leading-none relative overflow-hidden'):
        # The <a> tag wraps the poster <img>—its alt text is the show title
        title_container = event.find('a', class_='block relative media media--adapt overflow-hidden')
        title = title_container.find('img').get('alt')

        # Build the absolute URL to the event detail page
        link = title_container.get('href')
        link = 'https://tassatlv.co.il/' + link

        # Visit the detail page to extract date and time info
        inner_res = requests.get(link)
        inner_soup = BeautifulSoup(inner_res.text, 'html.parser')

        # Extract the date string and strip the Hebrew label ": תאריך"
        date = inner_soup.find('p', class_='custom-icon-2 product__text rte text-base').get_text(strip=True)
        date = date.replace(': תאריך', '')

        # Extract the time string and strip the Hebrew label ": תחילת מופע"
        hour = inner_soup.find('p', class_='custom-icon-3 product__text rte text-base').get_text(strip=True)
        hour = hour.replace(': תחילת מופע', '')
        date = date + ' ' + hour

        # Try parsing using each format until one works
        for frmt in FORMATS:
            try:
                date = datetime.strptime(date, frmt)
                break
            except ValueError:
                continue
        
        # Use the same <img> tag’s src for the poster image URL
        img = title_container.find('img').get('src')

        events.append({'show_name':title, 'date':date, 'link':link, 'img':img, 'venue':'TASSA'})
        
    return pd.DataFrame(events)