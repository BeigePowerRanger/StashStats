import pandas as pd
from stashies.mock_analytics import get_mock_analytics_dataframe, get_mock_animated_analytics_dataframe

def test_mock_analytics_dataframe():
    df = get_mock_analytics_dataframe(days=100)
    assert not df.empty
    expected_cols = [
        "date", "yards", "meters", "skeins", "grams",
        "cumulative_yards", "cumulative_meters", "cumulative_skeins", "cumulative_grams"
    ]
    for col in expected_cols:
        assert col in df.columns
    assert isinstance(df["date"].iloc[0], pd.Timestamp)

def test_mock_animated_analytics_dataframe():
    df = get_mock_animated_analytics_dataframe(days=100)
    assert not df.empty
    expected_cols = [
        "date", "category", "yards", "meters", "skeins", "grams",
        "cumulative_yards", "cumulative_meters", "cumulative_skeins",
        "cumulative_grams", "size_skeins", "frame_date"
    ]
    for col in expected_cols:
        assert col in df.columns
    assert set(df["category"].unique()) == {"Lace", "Fingering", "DK", "Worsted", "Bulky"}
