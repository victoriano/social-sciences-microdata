"""Spain-specific trend analysis for PISA data."""

import polars as pl
from pathlib import Path

def analyze_spain_trends():
    """Analyze Spain's performance trends across PISA years."""
    # Download processed data from HuggingFace
    data_path = Path("data/pisa/processed/spain_trends/spain_trends_2006_2022.parquet")
    
    if data_path.exists():
        df = pl.read_parquet(data_path)
        
        # Analysis code here
        print("Spain PISA Trends Analysis")
        print("=" * 50)
        
        # Show average scores by year
        trends = df.group_by("year").agg([
            pl.col("math_score").mean().alias("avg_math"),
            pl.col("reading_score").mean().alias("avg_reading"),
            pl.col("science_score").mean().alias("avg_science")
        ]).sort("year")
        
        print(trends)
    else:
        print("❌ Spain trends data not found. Run preprocessing first.")

if __name__ == "__main__":
    analyze_spain_trends()
