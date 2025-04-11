import pandas as pd
from datetime import datetime, timedelta

def scrape():
    title = 'Jazz Show'
    
    today = datetime.today().date()
    
    days_until_tuesday = (1 - today.weekday()) % 7
    
    date = str(today + timedelta(days=days_until_tuesday))
    date = date + ' 20:00'
    date = datetime.strptime(date, '%Y-%m-%d %H:%M')
    
    events = pd.DataFrame({'show_name': [title], 'date': [date], 'link': 'https://www.instagram.com/guestroomtlv/', 'img':'https://scontent.ftlv7-1.fna.fbcdn.net/v/t39.30808-6/305645277_602085274844509_3644686847235487262_n.jpg?_nc_cat=103&ccb=1-7&_nc_sid=6ee11a&_nc_ohc=EaWFzvxQNl8Q7kNvgG5GiG4&_nc_oc=AdkpY0a5xk2263XSRLlYR1ZrfU7oQKY--aaEcnnKGekbBPX2Fho3sqPAVstJcu8urD0&_nc_zt=23&_nc_ht=scontent.ftlv7-1.fna&_nc_gid=DvozFRDP98u8v27tGA5Bfg&oh=00_AYHCmsLu6gdQ7INtioRRQ2P3GQMkBoBvQmGeyniZ0b-zCg&oe=67E8C47E', 'venue':'Guestroom'})
    return events