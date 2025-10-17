#!/usr/bin/env python3
"""
Example usage of the weather transformation functions.

This script demonstrates how to use the weather_transformation module
to convert weather data from long format to wide format.
"""

import dask.dataframe as dd
import pandas as pd
from weather_transformation import transform_long_to_wide, display_dataframe_info, save_wide_dataframe


def create_sample_data():
    """Create sample weather data for demonstration."""
    # Sample data in long format
    data = {
        'ID': ['STATION1', 'STATION1', 'STATION1', 'STATION2', 'STATION2'],
        'DATE': [20200101, 20200102, 20200103, 20200101, 20200102],
        'ELEMENT': ['TMAX', 'TMAX', 'TMAX', 'TMAX', 'TMAX'],
        'DATA_VALUE': [25.5, 26.0, 24.5, 23.0, 24.0]
    }
    
    # Convert to pandas DataFrame first, then to Dask DataFrame
    df_pandas = pd.DataFrame(data)
    df_long = dd.from_pandas(df_pandas, npartitions=1)
    
    return df_long


def main():
    """Main function demonstrating the transformation."""
    print("Weather Data Transformation Example")
    print("==================================")
    print()
    
    # Create sample data
    print("1. Creating sample weather data...")
    df_long = create_sample_data()
    print(f"   Long format shape: {df_long.shape.compute()}")
    print(f"   Columns: {list(df_long.columns)}")
    print()
    
    # Transform to wide format
    print("2. Transforming to wide format...")
    df_wide = transform_long_to_wide(df_long, aggfunc='mean', fill_missing_days=True)
    
    # Display information
    print("3. Displaying dataframe information...")
    display_dataframe_info(df_wide)
    print()
    
    # Show first few rows
    print("4. First few rows of wide format:")
    print(df_wide.head().compute())
    print()
    
    # Save to file
    print("5. Saving to file...")
    output_file = 'sample_weather_wide.parquet'
    save_wide_dataframe(df_wide, output_file)
    print()
    
    print("Example completed successfully!")


if __name__ == "__main__":
    main()
