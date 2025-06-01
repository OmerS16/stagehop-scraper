import pandas as pd
from datetime import datetime, timedelta

def scrape():
    """
    Constructs a single-row DataFrame for the next Tuesday’s Jazz Show:
      - show_name: static title 'Jazz Show'
      - date: datetime object set to the coming Tuesday at 20:00 local date
      - link: URL to Guestroom TLV’s Instagram page
      - img: URL of the show’s promo image
      - venue: static venue name 'Guestroom'

    Returns:
        pandas.DataFrame with columns ['show_name', 'date', 'link', 'img', 'venue']
    """

    # Title of the recurring show
    title = 'Jazz Show'
    
    # Today's date
    today = datetime.today().date()
    
    # Calculate days until next Tuesday (weekday() Monday=0 … Sunday=6; Tuesday=1)
    days_until_tuesday = (1 - today.weekday()) % 7
    
    # Build the show’s datetime string for 20:00 on Tuesday
    next_tuesday = today + timedelta(days=days_until_tuesday)
    date_str = f"{next_tuesday} 20:00"
    date = datetime.strptime(date_str, '%Y-%m-%d %H:%M')
    
    events = pd.DataFrame({'show_name': [title], 'date': [date], 'link': 'https://www.instagram.com/guestroomtlv/', 'img':'https://scontent.ftlv7-1.fna.fbcdn.net/v/t39.30808-6/305645277_602085274844509_3644686847235487262_n.jpg?_nc_cat=103&ccb=1-7&_nc_sid=6ee11a&_nc_ohc=EaWFzvxQNl8Q7kNvgG5GiG4&_nc_oc=AdkpY0a5xk2263XSRLlYR1ZrfU7oQKY--aaEcnnKGekbBPX2Fho3sqPAVstJcu8urD0&_nc_zt=23&_nc_ht=scontent.ftlv7-1.fna&_nc_gid=DvozFRDP98u8v27tGA5Bfg&oh=00_AYHCmsLu6gdQ7INtioRRQ2P3GQMkBoBvQmGeyniZ0b-zCg&oe=67E8C47E', 'venue':'Guestroom'})
    return events