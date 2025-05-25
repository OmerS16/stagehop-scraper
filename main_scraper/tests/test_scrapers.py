# tests/test_scrapers.py
import pytest
import pandas as pd

from scrapers import (
    amama,
    barby,
    beit_hayotzer,
    guestroom,
    guitar_loft,
    haezor,
    hameretz2,
    holybar,
    ivri,
    kissa,
    levontin,
    ozenbar,
    shablul,
    tassa,
    tmuna,
)

ALL_SCRAPERS = [
    amama,
    barby,
    beit_hayotzer,
    guestroom,
    guitar_loft,
    haezor,
    hameretz2,
    holybar,
    ivri,
    kissa,
    levontin,
    ozenbar,
    shablul,
    tassa,
    tmuna,
]

REQUIRED_COLUMNS = {"show_name", "date", "venue"}

@pytest.mark.parametrize("scraper_module", ALL_SCRAPERS)
def test_scraper_returns_dataframe(scraper_module):
    """
    Each scraper.scrape() should return a pandas DataFrame,
    containing at least the columns in REQUIRED_COLUMNS.
    """
    df = scraper_module.scrape()
    assert isinstance(df, pd.DataFrame), f"{scraper_module.__name__}.scrape() did not return a DataFrame"
    # even if no events, schema should be correct
    assert REQUIRED_COLUMNS.issubset(df.columns), (
        f"{scraper_module.__name__} missing columns: "
        f"{REQUIRED_COLUMNS - set(df.columns)}"
    )
