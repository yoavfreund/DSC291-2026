#!/usr/bin/env python3
"""
Concatenate Weather Data Script

This script concatenates weather parquet files for a specified range of years.

Usage:
    python concatenate_weather_data.py --data_dir data --start_year 1950 --end_year 1954
    python concatenate_weather_data.py --data_dir /path/to/data --start_year 2020 --end_year 2022
"""

import argparse
import dask.dataframe as dd
import os
from datetime import datetime


def main():
    """Main function to concatenate weather data files."""
    parser = argparse.ArgumentParser(description='Concatenate weather parquet files for a range of years')
    parser.add_argument('--data_dir', type=str, required=True, 
                       help='Path to the data directory containing parquet files')
    parser.add_argument('--start_year', type=int, required=True,
                       help='Starting year (inclusive)')
    parser.add_argument('--end_year', type=int, required=True,
                       help='Ending year (inclusive)')
    parser.add_argument('--output_name', type=str, default=None,
                       help='Output filename (default: weather_{start_year}_{end_year}_combined.parquet)')
    
    args = parser.parse_args()
    
    # Validate arguments
    if args.start_year > args.end_year:
        print("Error: start_year must be <= end_year")
        return 1
    
    if not os.path.exists(args.data_dir):
        print(f"Error: Data directory '{args.data_dir}' does not exist")
        return 1
    
    print(f"Starting concatenation at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Data directory: {args.data_dir}")
    print(f"Year range: {args.start_year} to {args.end_year}")
    
    # Generate list of years
    years = list(range(args.start_year, args.end_year + 1))
    print(f"Processing {len(years)} years: {years}")
    
    # Collect file paths
    file_paths = []
    missing_years = []
    
    for year in years:
        file_path = os.path.join(args.data_dir, f"weather_{year}_wide.parquet")
        if os.path.exists(file_path):
            file_paths.append(file_path)
            print(f"✓ Found: {year}")
        else:
            missing_years.append(year)
            print(f"✗ Missing: {year}")
    
    if not file_paths:
        print("Error: No parquet files found for the specified years")
        return 1
    
    if missing_years:
        print(f"Warning: {len(missing_years)} years missing: {missing_years}")
    
    print(f"\nFound {len(file_paths)} files to concatenate")
    
    # Load and concatenate files in batches to avoid memory issues
    print("Loading and concatenating files...")
    
    # Process files in batches of 10 to avoid memory issues with large datasets
    batch_size = 10
    all_dataframes = []
    
    for i in range(0, len(file_paths), batch_size):
        batch_files = file_paths[i:i + batch_size]
        print(f"  Processing batch {i//batch_size + 1}/{(len(file_paths) + batch_size - 1)//batch_size} ({len(batch_files)} files)")
        
        batch_dataframes = []
        for file_path in batch_files:
            try:
                df = dd.read_parquet(file_path)
                batch_dataframes.append(df)
                print(f"    Loaded: {os.path.basename(file_path)}")
            except Exception as e:
                print(f"    Error loading {os.path.basename(file_path)}: {e}")
                continue
        
        if batch_dataframes:
            # Concatenate this batch
            batch_combined = dd.concat(batch_dataframes, ignore_index=True)
            all_dataframes.append(batch_combined)
    
    if not all_dataframes:
        print("Error: No dataframes could be loaded")
        return 1
    
    # Concatenate all batches
    print("Combining all batches...")
    df_combined = dd.concat(all_dataframes, ignore_index=True)
    print(f"\nConcatenated: {df_combined.shape[0]} rows × {len(df_combined.columns)} columns")
    
    # Generate output filename
    if args.output_name:
        output_filename = args.output_name
    else:
        output_filename = f"weather_{args.start_year}_{args.end_year}_combined.parquet"
    
    output_file = os.path.join(args.data_dir, output_filename)
    
    # Save the combined data
    print(f"Saving to: {output_file}")
    
    df_combined.to_parquet(output_file)
    print("✓ Saved successfully")
    
    # Check file size
    if os.path.exists(output_file):
        file_size = os.path.getsize(output_file) / (1024 * 1024)
        print(f"File size: {file_size:.1f} MB")
    
    # Quick verification
    print("Verifying saved file...")
    verification_df = dd.read_parquet(output_file)
    print(f"✓ Verification: {verification_df.shape[0]} rows × {len(verification_df.columns)} columns")
    
    print(f"\nCompleted at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("✓ All done!")
    
    return 0


if __name__ == "__main__":
    exit(main())








