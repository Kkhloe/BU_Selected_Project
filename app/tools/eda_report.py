import argparse
import json
import os
import polars as pl
from app.utils.logger import logger

def generate_eda_report(input_path):
    logger.info(f"Generating EDA report for: {input_path}")
    df = pl.read_parquet(input_path)
    
    # 自动识别频率
    df = df.sort("date")
    date_diffs = df["date"].diff().drop_nulls()
    if len(date_diffs) > 0:
        # Polars diff on datetime results in Duration
        # For Polars 1.x, we can use total_days() or similar
        # Let's use a more robust way to get days
        # In Polars 1.x, median() on Duration returns a Duration (timedelta-like)
        median_duration = date_diffs.median()
        # Convert duration to total seconds then to days
        # If it's a python timedelta
        import datetime
        if isinstance(median_duration, datetime.timedelta):
            total_seconds = median_duration.total_seconds()
        else:
            # If it's a polars duration, it might have .total_milliseconds() or similar
            # For safety, let's use the property if it exists or convert
            try:
                total_seconds = median_duration.total_seconds()
            except:
                total_seconds = float(median_duration) / 1e6 # microseconds to seconds
        
        median_diff_days = total_seconds / (60 * 60 * 24)
        
        if median_diff_days <= 1.5:
            freq = "Daily"
        elif median_diff_days <= 7.5:
            freq = "Weekly"
        elif median_diff_days <= 31.5:
            freq = "Monthly"
        else:
            freq = "Quarterly/Yearly"
    else:
        freq = "Unknown"

    report = {
        "filename": os.path.basename(input_path),
        "total_rows": len(df),
        "missing_rate": df["value"].null_count() / len(df),
        "start_date": df["date"].min().isoformat() if len(df) > 0 else None,
        "end_date": df["date"].max().isoformat() if len(df) > 0 else None,
        "frequency": freq,
        "stats": {
            "mean": float(df["value"].mean()) if len(df) > 0 else None,
            "std": float(df["value"].std()) if len(df) > 0 else None,
            "min": float(df["value"].min()) if len(df) > 0 else None,
            "max": float(df["value"].max()) if len(df) > 0 else None,
        }
    }
    
    return report

def main():
    parser = argparse.ArgumentParser(description="EDA Report Tool")
    parser.add_argument("--input", required=True, help="Input processed parquet file")
    
    args = parser.parse_args()
    
    report = generate_eda_report(args.input)
    
    os.makedirs("reports", exist_ok=True)
    report_filename = os.path.basename(args.input).replace(".parquet", "_eda.json")
    report_path = os.path.join("reports", report_filename)
    
    with open(report_path, "w") as f:
        json.dump(report, f, indent=4)
        
    logger.info(f"EDA report saved to {report_path}")

if __name__ == "__main__":
    main()
