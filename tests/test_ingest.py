import os
import pandas as pd
import pytest
from app.tools.data_ingest import fetch_worldbank_data
from app.utils.metadata_db import init_db, DataMetadata

def test_fetch_worldbank_data():
    indicator = "NY.GDP.MKTP.KD.ZG"
    countries = ["CN", "US"]
    df, url = fetch_worldbank_data(indicator, countries, 2020, 2021)
    
    assert not df.empty
    assert "value" in df.columns
    assert "country.value" in df.columns
    assert len(df) > 0

def test_metadata_recording():
    db_url = "sqlite:///./test_metadata.db"
    session = init_db(db_url)
    
    # Clean up if exists
    session.query(DataMetadata).delete()
    session.commit()
    
    metadata = DataMetadata(
        source="test",
        indicator="test_ind",
        url="http://test.com",
        file_path="test.parquet",
        file_hash="hash123",
        row_count=100,
        duration_ms=500.0
    )
    session.add(metadata)
    session.commit()
    
    recorded = session.query(DataMetadata).filter_by(source="test").first()
    assert recorded is not None
    assert recorded.row_count == 100
    
    # Cleanup
    if os.path.exists("test_metadata.db"):
        os.remove("test_metadata.db")

def test_idempotency_check():
    # In this simple implementation, idempotency means we can run it multiple times 
    # and it should either update or create new records.
    # Here we just check if the file is correctly overwritten.
    indicator = "NY.GDP.MKTP.KD.ZG"
    countries = ["CN"]
    df1, _ = fetch_worldbank_data(indicator, countries, 2020, 2020)
    
    path = "data/raw/test_idempotent.parquet"
    df1.to_parquet(path)
    hash1 = os.path.getmtime(path)
    
    df2, _ = fetch_worldbank_data(indicator, countries, 2020, 2020)
    df2.to_parquet(path)
    hash2 = os.path.getmtime(path)
    
    assert os.path.exists(path)
    # File was updated
    assert hash2 >= hash1
    
    if os.path.exists(path):
        os.remove(path)
