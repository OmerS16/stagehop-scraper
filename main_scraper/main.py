from scrapers import amama, barby, beit_hayotzer, guestroom, guitar_loft, haezor, hameretz2, ivri, levontin, ozenbar, shablul, tassa, tmuna
import pandas as pd
import time

def run_scrape(venue) -> pd.DataFrame:
    venue_df = pd.DataFrame()
    try:
       start = time.time()
       venue_df = venue.scrape()
       print(f"{venue} took {time.time() - start:.2f} seconds")
    except Exception as e:
       print(f'{venue} failed: {e}')
    return venue_df

def main():
    amama_df = run_scrape(amama)
    barby_df = run_scrape(barby)
    beit_hayotzer_df = run_scrape(beit_hayotzer)
    guestroom_df = run_scrape(guestroom)
    guitar_loft_df = run_scrape(guitar_loft)
    haezor_df = run_scrape(haezor)
    hameretz_df = run_scrape(hameretz2)
    ivri_df = run_scrape(ivri)
    levontin_df = run_scrape(levontin)
    ozenbar_df = run_scrape(ozenbar)
    shablul_df = run_scrape(shablul)
    tassa_df = run_scrape(tassa)
    tmuna_df = run_scrape(tmuna)
    
    dfs = [amama_df, barby_df, beit_hayotzer_df, guestroom_df, guitar_loft_df, 
           haezor_df, hameretz_df, ivri_df, levontin_df, 
           ozenbar_df, shablul_df, tassa_df, tmuna_df]
    
    events = pd.concat(dfs, ignore_index=True)
    return events