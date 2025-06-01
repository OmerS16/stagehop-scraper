from scrapers import amama, barby, beit_hayotzer, guestroom, guitar_loft, haezor, hameretz2, holybar, ivri, kissa, levontin, ozenbar, shablul, tassa, tmuna
import pandas as pd
import time
import hashlib

def run_scrape(venue) -> pd.DataFrame:
    """
    Executes the scrape() function of a given venue module, measuring its duration.

    Args:
        venue: a scraper module that defines a scrape() function returning a DataFrame.

    Returns:
        pandas.DataFrame: the DataFrame returned by venue.scrape(), or an empty DataFrame on failure.
    """

    venue_df = pd.DataFrame()
    try:
       start = time.time()
       venue_df = venue.scrape()
       print(f"{venue} took {time.time() - start:.2f} seconds")
    except Exception as e:
       print(f'{venue} failed: {e}')
    return venue_df

def make_event_hash(row, length: int = 12) -> str:
    """
    Generates a short, deterministic hash for a single event row.

    The hash is based on show_name, date, and venue, concatenated with '|',
    then hashed via SHA-256 and truncated.

    Args:
        row: A pandas Series representing one event, with fields 'show_name', 'date', and 'venue'.
        length: Number of hex characters to keep from the SHA-256 digest.

    Returns:
        str: First `length` characters of the hex digest.
    """

    base = f"{row['show_name'].strip()}|{row['date']}|{row['venue'].strip()}"
    h = hashlib.sha256(base.encode("utf-8")).hexdigest()
    return h[:length] # first 12 hex chars

def main():
    """
    Runs all venue scrapers, concatenates their outputs, and appends a unique ID column.

    Steps:
      1. Call run_scrape() for each scraper module to get individual DataFrames.
      2. Concatenate all venue DataFrames into one master DataFrame.
      3. Apply make_event_hash() to each row to assign a unique 'id'.

    Returns:
        pandas.DataFrame: Combined events across all venues with an added 'id' column.
    """

    amama_df = run_scrape(amama)
    barby_df = run_scrape(barby)
    beit_hayotzer_df = run_scrape(beit_hayotzer)
    guestroom_df = run_scrape(guestroom)
    guitar_loft_df = run_scrape(guitar_loft)
    haezor_df = run_scrape(haezor)
    hameretz_df = run_scrape(hameretz2)
    holybar_df = run_scrape(holybar)
    ivri_df = run_scrape(ivri)
    kissa_df = run_scrape(kissa)
    levontin_df = run_scrape(levontin)
    ozenbar_df = run_scrape(ozenbar)
    shablul_df = run_scrape(shablul)
    tassa_df = run_scrape(tassa)
    tmuna_df = run_scrape(tmuna)
    
    dfs = [amama_df, barby_df, beit_hayotzer_df, guestroom_df, guitar_loft_df, 
           haezor_df, hameretz_df, holybar_df, ivri_df, kissa_df, levontin_df, 
           ozenbar_df, shablul_df, tassa_df, tmuna_df]
    
    events = pd.concat(dfs, ignore_index=True)
    
    events['id'] = events.apply(make_event_hash, axis=1)

    return events