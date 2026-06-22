import os
import polars as pl
import pytest
from app.utils.schema import to_standard_schema
from app.tools.eda_report import generate_eda_report

def test_schema_consistency():
    # Mock worldbank-like data
    wb_data = pl.DataFrame({
        "date": ["2020", "2021"],
        "country.value": ["China", "China"],
        "value": [6.0, 8.1]
    }).to_pandas()
    
    # Mock yfinance-like data
    yf_data = pl.DataFrame({
        "Date": ["2023-01-01", "2023-01-02"],
        "Close": [150.0, 155.0]
    }).to_pandas().set_index("Date")
    
    wb_std = to_standard_schema(wb_data, "worldbank", "GDP")
    yf_std = to_standard_schema(yf_data, "yfinance", "AAPL")
    
    assert list(wb_std.columns) == ["date", "country", "value", "indicator", "source"]
    assert list(yf_std.columns) == ["date", "country", "value", "indicator", "source"]
    assert wb_std["country"].iloc[0] == "China"
    assert yf_std["country"].iloc[0] == "Global"

def test_eda_report_calculation():
    # Create a dummy parquet file
    path = "tests/dummy.parquet"
    df = pl.DataFrame({
        "date": pl.datetime_range(start=pl.datetime(2023, 1, 1), end=pl.datetime(2023, 1, 10), interval="1d", eager=True),
        "country": ["Global"] * 10,
        "value": [10.0, 11.0, None, 13.0, 14.0, 15.0, 16.0, 17.0, 18.0, 19.0],
        "indicator": ["TEST"] * 10,
        "source": ["test"] * 10
    })
    df.write_parquet(path)
    
    report = generate_eda_report(path)
    
    assert report["total_rows"] == 10
    assert report["missing_rate"] == 0.1
    assert report["frequency"] == "Daily"
    assert report["stats"]["min"] == 10.0
    
    os.remove(path)

def test_frequency_detection():
    # Weekly data
    path = "tests/weekly.parquet"
    df = pl.DataFrame({
        "date": pl.datetime_range(start=pl.datetime(2023, 1, 1), end=pl.datetime(2023, 2, 1), interval="1w", eager=True),
        "country": ["Global"] * 5,
        "value": [1.0] * 5,
        "indicator": ["TEST"] * 5,
        "source": ["test"] * 5
    })
    df.write_parquet(path)
    
    report = generate_eda_report(path)
    assert report["frequency"] == "Weekly"
    
    os.remove(path)
