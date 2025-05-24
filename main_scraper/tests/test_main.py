import pandas as pd
from main_scraper.main import main

def test_main_returns_dataframe():
    df = main()
    assert isinstance(df, pd.DataFrame)
    assert not df.empty
    for col in ["show_name", "date", "venue", "id"]:
        assert col in df.columns, f"Missing column: {col}"
    assert df["id"].is_unique, "Found duplicate event IDs"