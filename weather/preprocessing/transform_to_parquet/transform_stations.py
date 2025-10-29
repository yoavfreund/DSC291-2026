#!/usr/bin/env python3
"""
Transform ghcnd-stations.txt to parquet format
"""

import pandas as pd
import dask.dataframe as dd
import os
import argparse

def transform_stations_to_parquet():
    """Transform GHCN stations file to parquet format."""
    
    # Define paths
    weather_info_dir = '../weather_info'
    input_file = os.path.join(weather_info_dir, 'ghcnd-stations.txt')
    output_file = os.path.join(weather_info_dir, 'stations_dask.parquet')
    
    print("GHCN STATIONS TRANSFORMATION")
    print("=" * 40)
    print(f"Input: {input_file}")
    print(f"Output: {output_file}")
    
    # Check if input file exists
    if not os.path.exists(input_file):
        print(f"Error: Input file {input_file} not found!")
        return False
    
    try:
        print("Reading stations file...")
        
        # Read the stations file with fixed-width format
        # Format: ID(11) Lat(8) Lon(9) Elev(6) State(2) Name(30) GSN(3) HCN(3) WMO(5)
        df_pandas = pd.read_fwf(
            input_file,
            colspecs=[(0, 11), (12, 20), (21, 30), (31, 37), (38, 40), (41, 71), (72, 75), (76, 79), (80, 85)],
            names=['station_id', 'latitude', 'longitude', 'elevation', 'state', 'name', 'gsn_flag', 'hcn_crn_flag', 'wmo_id'],
            na_values=['', ' '],
            keep_default_na=True
        )
        
        print(f"✓ Loaded {len(df_pandas):,} stations")
        
        # Convert to Dask DataFrame
        print("Converting to Dask DataFrame...")
        stations_df = dd.from_pandas(df_pandas, npartitions=4)
        
        # Save as parquet
        print("Saving as parquet...")
        stations_df.to_parquet(output_file)
        
        print(f"✓ Saved stations parquet: {output_file}")
        print(f"Stations: {len(df_pandas):,}")
        print(f"Geographic range: {df_pandas['latitude'].min():.2f} to {df_pandas['latitude'].max():.2f} lat")
        print(f"Southern Hemisphere: {(df_pandas['latitude'] < 0).sum():,} stations")
        
        return True
        
    except Exception as e:
        print(f"Error during transformation: {e}")
        return False

if __name__ == "__main__":
    success = transform_stations_to_parquet()
    exit(0 if success else 1)
