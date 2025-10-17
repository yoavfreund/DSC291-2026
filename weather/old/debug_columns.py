#!/usr/bin/env python3
"""
Debug script to check column structure of parquet files.

This script helps identify column mismatches in the weather data files.
"""

import os
import dask.dataframe as dd
import pandas as pd


def check_parquet_columns(data_dir="data"):
    """Check the column structure of all parquet files in the data directory."""
    
    print("Parquet File Column Structure Checker")
    print("=" * 50)
    
    if not os.path.exists(data_dir):
        print(f"❌ Data directory '{data_dir}' does not exist")
        return
    
    # Find all parquet directories
    parquet_dirs = [d for d in os.listdir(data_dir) if d.endswith('.parquet')]
    
    if not parquet_dirs:
        print(f"❌ No parquet files found in '{data_dir}'")
        return
    
    print(f"Found {len(parquet_dirs)} parquet directories:")
    for d in parquet_dirs:
        print(f"  - {d}")
    
    print("\nChecking column structure...")
    
    # Expected column structure
    expected_columns = ['ID', 'year', 'ELEMENT'] + [f'day_{i}' for i in range(1, 366)]
    expected_count = len(expected_columns)
    
    print(f"Expected columns: {expected_count} total")
    print(f"Expected structure: {expected_columns[:10]}...")
    
    all_structures_match = True
    
    for i, parquet_dir in enumerate(parquet_dirs):
        file_path = os.path.join(data_dir, parquet_dir)
        print(f"\n{i+1}. Checking {parquet_dir}:")
        
        try:
            # Read the parquet file
            df = dd.read_parquet(file_path)
            actual_columns = list(df.columns)
            actual_count = len(actual_columns)
            
            print(f"   Columns: {actual_count}")
            print(f"   Structure: {actual_columns[:10]}...")
            
            # Check if structure matches
            if actual_columns == expected_columns:
                print(f"   ✓ Structure matches expected")
            else:
                print(f"   ❌ Structure mismatch!")
                all_structures_match = False
                
                # Show differences
                missing_cols = set(expected_columns) - set(actual_columns)
                extra_cols = set(actual_columns) - set(expected_columns)
                
                if missing_cols:
                    print(f"   Missing columns ({len(missing_cols)}): {sorted(list(missing_cols))[:10]}...")
                if extra_cols:
                    print(f"   Extra columns ({len(extra_cols)}): {sorted(list(extra_cols))[:10]}...")
                
                # Show column order differences
                if actual_count == expected_count:
                    print(f"   Column order difference detected")
                    for j, (exp, act) in enumerate(zip(expected_columns, actual_columns)):
                        if exp != act:
                            print(f"     Position {j}: expected '{exp}', got '{act}'")
                            break
            
            # Show sample data
            try:
                sample = df.head().compute()
                print(f"   Sample data shape: {sample.shape}")
                print(f"   Sample columns: {list(sample.columns)[:5]}...")
            except Exception as e:
                print(f"   Could not read sample data: {e}")
                
        except Exception as e:
            print(f"   ❌ Error reading file: {e}")
            all_structures_match = False
    
    print(f"\n{'='*50}")
    if all_structures_match:
        print("✓ All parquet files have consistent column structure")
    else:
        print("❌ Column structure inconsistencies found")
        print("\nRecommendations:")
        print("1. Check the weather_transformation.py function for column generation")
        print("2. Ensure all years are processed with the same transformation")
        print("3. Consider re-running the transformation for inconsistent files")


def main():
    """Main function."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Debug parquet file column structure')
    parser.add_argument('--data_dir', type=str, default='data', help='Data directory to check')
    
    args = parser.parse_args()
    check_parquet_columns(args.data_dir)


if __name__ == "__main__":
    main()
