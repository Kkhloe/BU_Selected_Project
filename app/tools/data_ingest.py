import argparse
import hashlib
import time
import uuid
import os
import requests
import pandas as pd
import yfinance as yf
from app.utils.logger import logger
from app.utils.metadata_db import init_db, DataMetadata
from app.utils.schema import to_standard_schema

def fetch_worldbank_data(indicator, countries, start_year, end_year):
    country_str = ";".join(countries)
    url = f"https://api.worldbank.org/v2/country/{country_str}/indicator/{indicator}"
    params = {
        "format": "json",
        "date": f"{start_year}:{end_year}",
        "per_page": 1000
    }
    
    response = requests.get(url, params=params)
    response.raise_for_status()
    
    data = response.json()
    if len(data) < 2 or not data[1]:
        return pd.DataFrame(), url
    
    df = pd.json_normalize(data[1])
    return df, response.url

def fetch_yfinance_data(symbol, start_year, end_year):
    ticker = yf.Ticker(symbol)
    df = ticker.history(start=f"{start_year}-01-01", end=f"{end_year}-12-31")
    return df, f"yfinance:{symbol}"

def main():
    parser = argparse.ArgumentParser(description="Data Ingest Tool")
    parser.add_argument("--source", required=True, choices=["worldbank", "yfinance"], help="Data source")
    parser.add_argument("--indicator", required=True, help="Indicator code or Ticker symbol")
    parser.add_argument("--countries", default="US", help="Comma separated country codes (ignored for yfinance)")
    parser.add_argument("--start", type=int, required=True, help="Start year")
    parser.add_argument("--end", type=int, required=True, help="End year")
    
    args = parser.parse_args()
    
    trace_id = str(uuid.uuid4())[:8]
    countries = args.countries.split(",")
    
    with logger.contextualize(trace_id=trace_id, source=args.source):
        start_time = time.time()
        logger.info(f"Starting ingestion for {args.indicator} from {args.source}")
        
        try:
            if args.source == "worldbank":
                df_raw, final_url = fetch_worldbank_data(args.indicator, countries, args.start, args.end)
            elif args.source == "yfinance":
                df_raw, final_url = fetch_yfinance_data(args.indicator, args.start, args.end)
            
            if df_raw.empty:
                logger.warning("No data found for the given parameters")
                return

            # Standardize Schema
            df = to_standard_schema(df_raw, args.source, args.indicator)

            # Save to Parquet
            os.makedirs("data/raw", exist_ok=True)
            filename = f"{args.source}_{args.indicator}_{args.start}_{args.end}.parquet"
            file_path = os.path.join("data/raw", filename)
            df.to_parquet(file_path, index=False)
            
            # Calculate hash
            with open(file_path, "rb") as f:
                file_hash = hashlib.md5(f.read()).hexdigest()
            
            duration = (time.time() - start_time) * 1000
            
            # Record Metadata
            session = init_db()
            metadata = DataMetadata(
                source=args.source,
                indicator=args.indicator,
                url=final_url,
                file_path=file_path,
                file_hash=file_hash,
                row_count=len(df),
                duration_ms=duration
            )
            session.add(metadata)
            session.commit()
            
            logger.bind(duration=duration).info(f"Successfully ingested {len(df)} rows to {file_path}")
            
        except Exception as e:
            logger.error(f"Ingestion failed: {str(e)}")
            raise

if __name__ == "__main__":
    main()
