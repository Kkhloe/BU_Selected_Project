import argparse
import os
import polars as pl
import duckdb
from app.utils.logger import logger

def clean_with_polars(input_path, output_path):
    logger.info(f"Cleaning data with Polars: {input_path}")
    df = pl.read_parquet(input_path)
    
    # 基础清洗：去重、处理缺失值、时间排序
    df_clean = (
        df.unique(subset=["date", "country", "indicator"])
        .drop_nulls(subset=["value"])
        .sort("date")
    )
    
    df_clean.write_parquet(output_path)
    return len(df_clean)

def clean_with_duckdb(input_path, output_path):
    logger.info(f"Cleaning data with DuckDB: {input_path}")
    con = duckdb.connect()
    
    # 使用 SQL 进行清洗
    query = f"""
    COPY (
        SELECT DISTINCT date, country, CAST(value AS DOUBLE) as value, indicator, source
        FROM read_parquet('{input_path}')
        WHERE value IS NOT NULL
        ORDER BY date
    ) TO '{output_path}' (FORMAT PARQUET);
    """
    con.execute(query)
    
    count = con.execute(f"SELECT COUNT(*) FROM read_parquet('{output_path}')").fetchone()[0]
    return count

def main():
    parser = argparse.ArgumentParser(description="Data Clean Tool")
    parser.add_argument("--input", required=True, help="Input parquet file")
    parser.add_argument("--engine", choices=["polars", "duckdb"], default="polars", help="Processing engine")
    
    args = parser.parse_args()
    
    filename = os.path.basename(args.input)
    output_path = os.path.join("data/processed", filename)
    os.makedirs("data/processed", exist_ok=True)
    
    if args.engine == "polars":
        count = clean_with_polars(args.input, output_path)
    else:
        count = clean_with_duckdb(args.input, output_path)
        
    logger.info(f"Cleaned data saved to {output_path}, total rows: {count}")

if __name__ == "__main__":
    main()
