#!/usr/bin/env python3
"""
Process Multiple Years of Weather Data

This script processes weather data for multiple years, transforming each year from long to wide format
and then concatenating all results into a single sorted dataset. Uses Dask distributed computing
for parallel processing.

Usage:
    # Basic usage with default cluster (20 workers, 4GB each)
    python process_multiple_years.py --start_year 2020 --end_year 2022
    
    # Custom cluster configuration
    python process_multiple_years.py --start_year 2020 --end_year 2022 --n_workers 16 --memory_per_worker 8GB
    
    # Single year processing
    python process_multiple_years.py --start_year 2020 --end_year 2020
"""

import os
import argparse
import s3fs
import dask.dataframe as dd
import pandas as pd
from datetime import datetime
import time
from cluster_utils import setup_dask_cluster, close_dask_cluster
from weather_transformation import transform_long_to_wide, display_dataframe_info, save_wide_dataframe


def setup_data_directory():
    """Create the data directory if it doesn't exist."""
    data_dir = "data"
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
        print(f"Created directory: {data_dir}")
    return data_dir




def load_weather_data_for_year(year: int) -> dd.DataFrame:
    """
    Load weather data for a specific year from S3.
    
    Args:
        year: Year to load data for
        
    Returns:
        Dask DataFrame with weather data for the specified year
    """
    print(f"Loading weather data for year {year}...")
    
    # Setup S3 filesystem
    s3 = s3fs.S3FileSystem(anon=True)
    bucket_path = 's3://noaa-ghcn-pds/parquet/by_year/'
    
    # Define measurements to load
    measurements = ['TOBS', 'TAVG','TMAX', 'TMIN', 'PRCP', 'SNOW', 'SNWD']
    
    # Collect all file paths for the year
    all_files = []
    for measurement in measurements:
        file_path = f"{bucket_path}YEAR={year}/ELEMENT={measurement}/"
        try:
            files = s3.glob(f"{file_path}*.parquet")
            all_files.extend([f"s3://{f}" for f in files])
        except Exception as e:
            print(f"Warning: Could not access {file_path}: {e}")
    
    if not all_files:
        print(f"Warning: No files found for year {year}")
        # Return empty DataFrame with expected schema
        empty_df = pd.DataFrame(columns=['ID', 'DATE', 'ELEMENT', 'DATA_VALUE'])
        return dd.from_pandas(empty_df, npartitions=1)
    
    print(f"Found {len(all_files)} files for year {year}")
    
    # Read all files into a single Dask DataFrame with S3 storage options
    try:
        df_long = dd.read_parquet(all_files, storage_options={'anon': True})
    except Exception as e:
        print(f"Error reading parquet files: {e}")
        print("Trying to read files individually...")
        
        # Try reading files one by one to identify problematic files
        valid_files = []
        for file_path in all_files:
            try:
                test_df = dd.read_parquet(file_path, storage_options={'anon': True})
                valid_files.append(file_path)
            except Exception as file_error:
                print(f"Skipping problematic file: {file_path}")
                print(f"  Error: {file_error}")
        
        if not valid_files:
            print("No valid files found")
            empty_df = pd.DataFrame(columns=['ID', 'DATE', 'ELEMENT', 'DATA_VALUE'])
            return dd.from_pandas(empty_df, npartitions=1)
        
        print(f"Found {len(valid_files)} valid files out of {len(all_files)}")
        df_long = dd.read_parquet(valid_files, storage_options={'anon': True})
    
    # Select only the columns we need
    required_columns = ['ID', 'DATE', 'ELEMENT', 'DATA_VALUE']
    available_columns = [col for col in required_columns if col in df_long.columns]
    df_long = df_long[available_columns]
    
    return df_long


def process_single_year(year: int, data_dir: str) -> str:
    """
    Process a single year of weather data.
    
    Args:
        year: Year to process
        data_dir: Directory to save the output file
        
    Returns:
        Path to the saved parquet file
    """
    print(f"\n{'='*50}")
    print(f"Processing year {year}")
    print(f"{'='*50}")
    
    start_time = time.time()
    
    try:
        # Load data for the year
        df_long = load_weather_data_for_year(year)
        
        # Check if we have any data
        if df_long.npartitions == 0 or len(df_long.columns) == 0:
            print(f"No data available for year {year}")
            return None
        
        # Display info about loaded data
        shape = df_long.shape
        if hasattr(shape[0], 'compute'):
            rows = shape[0].compute()
        else:
            rows = shape[0]
            
        if hasattr(shape[1], 'compute'):
            cols = shape[1].compute()
        else:
            cols = shape[1]
        print(f"Loaded data: {rows:,} rows × {cols} columns")
        
        # Transform to wide format
        print("Transforming to wide format...")
        df_wide = transform_long_to_wide(df_long, aggfunc='mean', fill_missing_days=True)
        
        # Display transformation info
        display_dataframe_info(df_wide)
        
        # Save to file
        output_file = os.path.join(data_dir, f"weather_{year}_wide.parquet")
        save_wide_dataframe(df_wide, output_file)
        
        # Report processing time
        end_time = time.time()
        processing_time = end_time - start_time
        print(f"\n⏱️  Year {year} processed in {processing_time:.1f} seconds ({processing_time/60:.1f} minutes)")
        
        return output_file
        
    except Exception as e:
        end_time = time.time()
        processing_time = end_time - start_time
        print(f"Error processing year {year}: {e}")
        print(f"⏱️  Failed after {processing_time:.1f} seconds ({processing_time/60:.1f} minutes)")
        return None


def concatenate_and_sort_files(file_paths: list, data_dir: str) -> str:
    """
    Concatenate all parquet files and sort by year, measurement, then station.
    
    Args:
        file_paths: List of parquet file paths to concatenate
        data_dir: Directory to save the final concatenated file
        
    Returns:
        Path to the final concatenated file
    """
    print(f"\n{'='*50}")
    print("Concatenating and sorting all files")
    print(f"{'='*50}")
    
    start_time = time.time()
    
    # Filter out None values
    valid_files = [f for f in file_paths if f is not None]
    
    if not valid_files:
        print("No valid files to concatenate")
        return None
    
    print(f"Concatenating {len(valid_files)} files...")
    
    try:
        # Read all parquet files
        df_list = []
        for file_path in valid_files:
            print(f"Reading {file_path}...")
            df = dd.read_parquet(file_path)
            df_list.append(df)
        
        # Ensure all DataFrames have the same column structure
        print("Ensuring consistent column structure...")
        expected_columns = ['ID', 'year', 'ELEMENT'] + [f'day_{i}' for i in range(1, 366)]
        
        # Standardize columns for each DataFrame
        standardized_dfs = []
        for i, df in enumerate(df_list):
            print(f"  Standardizing columns for DataFrame {i+1}...")
            current_cols = list(df.columns)
            
            # Check if columns match expected structure
            if current_cols != expected_columns:
                print(f"    Column mismatch detected. Expected {len(expected_columns)} columns, got {len(current_cols)}")
                print(f"    Expected: {expected_columns[:10]}...")
                print(f"    Got: {current_cols[:10]}...")
                
                # Check for missing columns
                missing_cols = set(expected_columns) - set(current_cols)
                extra_cols = set(current_cols) - set(expected_columns)
                
                if missing_cols:
                    print(f"    Missing columns: {sorted(list(missing_cols))[:10]}...")
                if extra_cols:
                    print(f"    Extra columns: {sorted(list(extra_cols))[:10]}...")
                
                try:
                    # Reorder columns to match expected structure
                    df_standardized = df[expected_columns]
                    standardized_dfs.append(df_standardized)
                    print(f"    ✓ Standardized to expected column structure")
                except KeyError as e:
                    print(f"    ❌ Error standardizing columns: {e}")
                    print(f"    Available columns: {sorted(current_cols)}")
                    raise
            else:
                standardized_dfs.append(df)
                print(f"    ✓ Columns already match expected structure")
        
        # Concatenate all standardized DataFrames
        print("Concatenating standardized DataFrames...")
        df_combined = dd.concat(standardized_dfs, ignore_index=True)
        
        # Sort by year, ELEMENT (measurement), then ID (station)
        print("Sorting by year, measurement, then station...")
        df_sorted = df_combined.sort_values(['year', 'ELEMENT', 'ID'])
        
        # Verify final column structure
        final_cols = list(df_sorted.columns)
        print(f"Final DataFrame columns: {len(final_cols)} columns")
        if final_cols != expected_columns:
            print(f"⚠️  Warning: Final column structure doesn't match expected!")
            print(f"    Expected: {expected_columns[:10]}...")
            print(f"    Got: {final_cols[:10]}...")
        else:
            print(f"✓ Final column structure verified: {len(final_cols)} columns")
        
        # Display final info
        display_dataframe_info(df_sorted)
        
        # Save final result
        final_output = os.path.join(data_dir, "weather_combined_sorted.parquet")
        save_wide_dataframe(df_sorted, final_output)
        
        # Report concatenation time
        end_time = time.time()
        concatenation_time = end_time - start_time
        print(f"\n⏱️  Concatenation completed in {concatenation_time:.1f} seconds ({concatenation_time/60:.1f} minutes)")
        
        return final_output
        
    except Exception as e:
        end_time = time.time()
        concatenation_time = end_time - start_time
        print(f"Error concatenating files: {e}")
        print(f"⏱️  Failed after {concatenation_time:.1f} seconds ({concatenation_time/60:.1f} minutes)")
        return None


def main():
    """Main function to process multiple years of weather data."""
    parser = argparse.ArgumentParser(description='Process multiple years of weather data')
    parser.add_argument('--start_year', type=int, default=2020, help='Start year (default: 2020)')
    parser.add_argument('--end_year', type=int, default=2022, help='End year (default: 2022)')
    parser.add_argument('--data_dir', type=str, default='data', help='Data directory (default: data)')
    parser.add_argument('--n_workers', type=int, default=20, help='Number of Dask workers (default: 20)')
    parser.add_argument('--memory_per_worker', type=str, default='4GB', help='Memory per worker (default: 4GB)')
    
    args = parser.parse_args()
    
    print("Weather Data Multi-Year Processor")
    print("=" * 40)
    print(f"Processing years: {args.start_year} to {args.end_year}")
    print(f"Data directory: {args.data_dir}")
    print(f"Dask cluster: {args.n_workers} workers, {args.memory_per_worker} per worker")
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    overall_start_time = time.time()
    
    # Setup Dask cluster using cluster_utils
    print(f"\n{'='*50}")
    print("Setting up Dask cluster")
    print(f"{'='*50}")
    
    cluster, client, cleanup_summary = setup_dask_cluster(
        n_workers=args.n_workers, 
        memory_per_worker=args.memory_per_worker
    )
    
    # Report cleanup summary if any existing clusters were closed
    if cleanup_summary and (cleanup_summary.get('clients_closed', 0) > 0 or cleanup_summary.get('clusters_closed', 0) > 0):
        print(f"✓ Cleaned up {cleanup_summary.get('clients_closed', 0)} existing clients and {cleanup_summary.get('clusters_closed', 0)} existing clusters")
    
    # Setup data directory
    data_dir = setup_data_directory()
    
    try:
        # Process each year
        processed_files = []
        for year in range(args.start_year, args.end_year + 1):
            output_file = process_single_year(year, data_dir)
            processed_files.append(output_file)
        
        # Concatenate and sort all files
        final_file = concatenate_and_sort_files(processed_files, data_dir)
        
    finally:
        # Clean up cluster using cluster_utils
        close_dask_cluster(cluster, client)
    
    # Summary
    overall_end_time = time.time()
    total_time = overall_end_time - overall_start_time
    
    print(f"\n{'='*50}")
    print("PROCESSING COMPLETE")
    print(f"{'='*50}")
    print(f"Processed years: {args.start_year} to {args.end_year}")
    print(f"Individual files saved in: {data_dir}")
    if final_file:
        print(f"Final concatenated file: {final_file}")
    print(f"Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"⏱️  Total processing time: {total_time:.1f} seconds ({total_time/60:.1f} minutes)")
    
    # Calculate average time per year
    years_processed = args.end_year - args.start_year + 1
    if years_processed > 0:
        avg_time_per_year = total_time / years_processed
        print(f"⏱️  Average time per year: {avg_time_per_year:.1f} seconds ({avg_time_per_year/60:.1f} minutes)")


if __name__ == "__main__":
    main()

