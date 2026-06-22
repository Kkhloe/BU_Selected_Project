import pandas as pd

def to_standard_schema(df, source, indicator_name):
    """
    将不同来源的数据转换为统一的 Schema:
    columns: [date, country, value, indicator, source]
    """
    if source == "worldbank":
        # World Bank schema typically has 'date', 'country.value', 'value'
        standard_df = pd.DataFrame({
            "date": pd.to_datetime(df["date"]),
            "country": df["country.value"],
            "value": pd.to_numeric(df["value"]),
            "indicator": indicator_name,
            "source": source
        })
    elif source == "yfinance":
        # yfinance schema typically has Date as index, 'Close' as value
        df = df.reset_index()
        standard_df = pd.DataFrame({
            "date": pd.to_datetime(df["Date"]),
            "country": "Global", 
            "value": pd.to_numeric(df["Close"]),
            "indicator": indicator_name,
            "source": source
        })
    else:
        raise ValueError(f"Unsupported source: {source}")
    
    return standard_df
