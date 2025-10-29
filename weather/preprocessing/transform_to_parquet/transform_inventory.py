#!/usr/bin/env python3
"""
Transform ghcnd-inventory.txt to parquet format
"""

import pandas as pd
import dask.dataframe as dd
import os
import argparse

def transform_inventory_to_parquet():
    """Transform GHCN inventory file to parquet format."""
    
    # Define paths
    weather_info_dir = '../weather_info'
    input_file = os.path.join(weather_info_dir, 'ghcnd-inventory.txt')
    output_file = os.path.join(weather_info_dir, 'inventory_dask.parquet')
    
    print("GHCN INVENTORY TRANSFORMATION")
    print("=" * 40)
    print(f"Input: {input_file}")
    print(f"Output: {output_file}")
    
    # Check if input file exists
    if not os.path.exists(input_file):
        print(f"Error: Input file {input_file} not found!")
        return False
    
    try:
        print("Reading inventory file...")
        
        # Read the inventory file with fixed-width format
        # Format: ID(11) Lat(8) Lon(9) Element(4) FirstYear(4) LastYear(4)
        df_pandas = pd.read_fwf(
            input_file,
            colspecs=[(0, 11), (12, 20), (21, 30), (31, 35), (36, 40), (41, 45)],
            names=['station_id', 'latitude', 'longitude', 'element', 'first_year', 'last_year'],
            na_values=['', ' '],
            keep_default_na=True
        )
        
        print(f"✓ Loaded {len(df_pandas):,} inventory records")
        
        # Convert to Dask DataFrame
        print("Converting to Dask DataFrame...")
        inventory_df = dd.from_pandas(df_pandas, npartitions=4)
        
        # Save as parquet
        print("Saving as parquet...")
        inventory_df.to_parquet(output_file)
        
        print(f"✓ Saved inventory parquet: {output_file}")
        print(f"Records: {len(df_pandas):,}")
        print(f"Elements: {df_pandas['element'].nunique()}")
        print(f"Stations: {df_pandas['station_id'].nunique():,}")
        print(f"Southern Hemisphere: {(df_pandas['latitude'] < 0).sum():,} records")
        
        # Show top elements
        element_counts = df_pandas['element'].value_counts()
        print(f"\nTop 5 elements:")
        for element, count in element_counts.head(5).items():
            print(f"  {element}: {count:,} records")
        
        return True
        
    except Exception as e:
        print(f"Error during transformation: {e}")
        return False

if __name__ == "__main__":
    success = transform_inventory_to_parquet()
    exit(0 if success else 1)
