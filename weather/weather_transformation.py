"""
Weather Data Transformation Functions

This module contains functions for transforming weather data from long format to wide format
using Dask DataFrames for efficient processing of large datasets.
"""

import dask.dataframe as dd
import numpy as np
from typing import Optional

# Constant for missing values - using maximal possible value to indicate NaN
# This value is unlikely to occur in real weather data
MISSING_VALUE = 999999.0


def transform_long_to_wide(df_long: dd.DataFrame, 
                          aggfunc: str = 'mean',
                          fill_missing_days: bool = True) -> dd.DataFrame:
    """
    Transform weather data from long format to wide format using Dask.
    
    Args:
        df_long: Dask DataFrame in long format with columns:
                - ID: Station identifier
                - DATE: Date in YYYYMMDD format
                - ELEMENT: Measurement type (TOBS, TMAX, TMIN, PRCP, SNOW, SNWD)
                - DATA_VALUE: Measurement value
        aggfunc: Aggregation function for pivot_table ('mean', 'sum', 'count')
        fill_missing_days: Whether to ensure all days 1-365 exist as columns
        
    Returns:
        Dask DataFrame in wide format with columns:
        - ID: Station identifier
        - year: Year
        - ELEMENT: Measurement type
        - day_1, day_2, ..., day_365: Daily values
        
    Note:
        Missing values are filled with MISSING_VALUE (999999.0) instead of NaN
        to provide a clear indicator of missing data.
    """
    
    # Create a copy to avoid modifying the original dataframe
    df_pivot = df_long[['ID', 'DATE', 'ELEMENT', 'DATA_VALUE']].copy()
    
    # Convert date to datetime and extract day of year and year
    df_pivot['date_dt'] = dd.to_datetime(df_pivot['DATE'], format='%Y%m%d')
    df_pivot['day_of_year'] = df_pivot['date_dt'].dt.dayofyear
    df_pivot['year'] = df_pivot['date_dt'].dt.year
    
    # Convert categorical ELEMENT to string to avoid dtype issues
    df_pivot['ELEMENT'] = df_pivot['ELEMENT'].astype(str)
    
    # Create a unique identifier for each group (station-year-measurement)
    df_pivot['group_id'] = (df_pivot['ID'].astype(str) + '_' + 
                           df_pivot['year'].astype(str) + '_' + 
                           df_pivot['ELEMENT'])
    
    # Convert day_of_year to categorical for dask pivot_table
    df_pivot['day_of_year'] = df_pivot['day_of_year'].astype('category')
    # Ensure known categories (required by dask pivot_table)
    df_pivot['day_of_year'] = df_pivot['day_of_year'].cat.as_known()
    
    # Use dask pivot_table with specified aggregation function
    df_wide = df_pivot.pivot_table(
        index='group_id',
        columns='day_of_year', 
        values='DATA_VALUE',
        aggfunc=aggfunc
    )
    
    # Fill missing values with maximal possible value to indicate NaN
    df_wide = df_wide.fillna(MISSING_VALUE)
    
    # Reset index to get group_id as a column
    df_wide = df_wide.reset_index()
    
    # Split the group_id back into separate columns
    df_wide[['ID', 'year', 'ELEMENT']] = df_wide['group_id'].str.split('_', expand=True, n=2)
    # Keep ID as string since weather station IDs are alphanumeric (e.g., 'AGE00147704')
    df_wide['year'] = df_wide['year'].astype(int)
    
    # Drop the temporary group_id column
    df_wide = df_wide.drop('group_id', axis=1)
    
    if fill_missing_days:
        # Ensure all days 1-365 exist as columns
        day_columns = list(range(1, 366))
        existing_day_cols = [col for col in df_wide.columns if isinstance(col, int)]
        missing_day_cols = [day for day in day_columns if day not in existing_day_cols]
        
        # Add missing day columns efficiently using a single assign operation
        if missing_day_cols:
            # Create all missing columns at once to avoid fragmentation
            missing_cols_dict = {str(day): MISSING_VALUE for day in missing_day_cols}
            df_wide = df_wide.assign(**missing_cols_dict)
            # Convert string column names back to integers
            df_wide = df_wide.rename(columns={str(day): day for day in missing_day_cols})
    
        # Reorder columns to have ID, year, ELEMENT first, then days 1-365
        columns_order = ['ID', 'year', 'ELEMENT'] + day_columns
        df_wide = df_wide[columns_order]
    
    # Sort and rename columns to have consistent naming
    day_cols = sorted([col for col in df_wide.columns if isinstance(col, int)])
    df_wide = df_wide[['ID', 'year', 'ELEMENT'] + day_cols]
    df_wide.columns = ['ID', 'year', 'ELEMENT'] + [f'day_{i}' for i in range(1, 366)]
    
    return df_wide


def display_dataframe_info(df_wide: dd.DataFrame) -> None:
    """
    Display information about the wide format dataframe.
    
    Args:
        df_wide: Dask DataFrame in wide format
    """
    # Display shape - handle mixed dask/pandas objects in shape tuple
    shape = df_wide.shape
    if hasattr(shape[0], 'compute') or hasattr(shape[1], 'compute'):
        # Handle mixed dask delayed objects and regular integers
        rows = shape[0].compute() if hasattr(shape[0], 'compute') else shape[0]
        cols = shape[1].compute() if hasattr(shape[1], 'compute') else shape[1]
        print(f"Created wide format: {rows:,} station-year-measurement combinations × {cols} columns")
    else:
        # Regular pandas tuple
        print(f"Created wide format: {shape[0]:,} station-year-measurement combinations × {shape[1]} columns")


def save_wide_dataframe(df_wide: dd.DataFrame, output_file: str) -> None:
    """
    Save the wide format dataframe to a parquet file.
    
    Args:
        df_wide: Dask DataFrame in wide format
        output_file: Path to output parquet file
    """
    # Dask DataFrame doesn't support index parameter in to_parquet
    # The index is automatically handled by dask
    df_wide.to_parquet(output_file)
    print(f"Saved to {output_file}")


# Example usage:
if __name__ == "__main__":
    # This is an example of how to use the functions
    # You would replace this with your actual data loading code
    
    print("Weather Data Transformation Functions")
    print("=====================================")
    print()
    print("Usage example:")
    print("1. Load your long format data into a Dask DataFrame")
    print("2. Call transform_long_to_wide(df_long)")
    print("3. Use display_dataframe_info(df_wide) to see the results")
    print("4. Use save_wide_dataframe(df_wide, 'output.parquet') to save")
    print()
    print("Available functions:")
    print("- transform_long_to_wide(): Main transformation function")
    print("- display_dataframe_info(): Display dataframe information")
    print("- save_wide_dataframe(): Save to parquet file")
