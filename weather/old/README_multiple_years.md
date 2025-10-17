# Multi-Year Weather Data Processor

This script processes weather data for multiple years, transforming each year from long to wide format and then concatenating all results into a single sorted dataset.

## Features

- **Multi-year processing**: Process any range of years
- **Individual year files**: Each year is saved as a separate parquet file
- **Automatic concatenation**: All years are combined into one sorted file
- **Sorted output**: Results are sorted by year, measurement type, then station ID
- **Missing value handling**: Uses 999999.0 to indicate missing data
- **Distributed Dask processing**: Parallel processing with configurable cluster
- **Performance monitoring**: Detailed timing reports for each step
- **Memory efficient**: Handles large datasets with lazy evaluation

## Files

- `process_multiple_years.py`: Main processing script
- `example_multiple_years.py`: Example usage script
- `weather_transformation.py`: Core transformation functions (required)
- `cluster_utils.py`: Dask cluster management utilities (required)

## Usage

### Basic Usage

```bash
# Process single year with default cluster (20 workers, 4GB each)
python process_multiple_years.py --start_year 2020 --end_year 2020

# Process multiple years
python process_multiple_years.py --start_year 2020 --end_year 2022

# Process with custom cluster configuration
python process_multiple_years.py --start_year 2020 --end_year 2022 --n_workers 16 --memory_per_worker 8GB

# Process with custom data directory
python process_multiple_years.py --start_year 2020 --end_year 2021 --data_dir my_data
```

### Command Line Arguments

- `--start_year`: First year to process (default: 2020)
- `--end_year`: Last year to process (default: 2022)
- `--data_dir`: Directory to save output files (default: data)
- `--n_workers`: Number of Dask workers (default: 20)
- `--memory_per_worker`: Memory per worker, e.g., '4GB', '8GB' (default: 4GB)

### Example Output Structure

```
data/
├── weather_2020_wide.parquet    # Individual year files
├── weather_2021_wide.parquet
├── weather_2022_wide.parquet
└── weather_combined_sorted.parquet  # Final concatenated file
```

## Output Format

Each parquet file contains weather data in wide format with columns:

- `ID`: Station identifier (string)
- `year`: Year (integer)
- `ELEMENT`: Measurement type (TOBS, TMAX, TMIN, PRCP, SNOW, SNWD)
- `day_1`, `day_2`, ..., `day_365`: Daily values for each day of the year

Missing values are represented as `999999.0` instead of NaN.

## Processing Steps

1. **Data Loading**: Load weather data from S3 for each year
2. **Transformation**: Convert from long to wide format using Dask
3. **Individual Saving**: Save each year as a separate parquet file
4. **Concatenation**: Combine all years into a single dataset
5. **Sorting**: Sort by year, measurement type, then station ID
6. **Final Save**: Save the complete sorted dataset

## Dask Cluster Configuration

The script uses `cluster_utils.py` to automatically set up a distributed Dask cluster for parallel processing:

- **Default Configuration**: 20 workers, 4GB memory per worker (80GB total)
- **Process-based workers**: Each worker runs in a separate process for true parallelism
- **Dashboard**: Real-time monitoring available at the dashboard URL
- **Automatic cleanup**: Cluster is properly closed after processing
- **Existing cluster cleanup**: Automatically closes any existing clusters before starting new ones

### Cluster Monitoring

When the script starts, you'll see:
```
==================================================
Setting up Dask cluster
==================================================
Checking for existing Dask clusters...
No current client found
All existing clusters closed.
Setting up new cluster with 20 workers...
✓ Dask cluster created with 20 workers
✓ Dashboard available at: http://127.0.0.1:8787/status
✓ Total workers: 20
✓ Cores per worker: 1
✓ Total memory available: 80.0 GB
✓ Cluster test computation successful: 84.00
✓ Cleaned up 0 existing clients and 0 existing clusters
```

## Performance Notes

- **Parallel processing**: Uses distributed Dask cluster for faster computation
- **Memory efficient**: Each worker has dedicated memory allocation
- **Lazy evaluation**: Operations are optimized and executed in parallel
- **Independent processing**: Each year is processed independently
- **Processing time**: Depends on data availability, year range, and cluster size

## Error Handling

- Continues processing even if some years have no data
- Logs warnings for inaccessible data sources
- Returns meaningful error messages for debugging
- **Column structure validation**: Ensures consistent column names during concatenation
- **Automatic column standardization**: Fixes column mismatches between different years
- **Detailed debugging**: Shows missing/extra columns when issues occur

## Requirements

- Python 3.7+
- Dask
- Pandas
- S3FS
- NumPy
- cluster_utils.py (included in project)

## Example Workflow

```python
# 1. Process years 2020-2022
python process_multiple_years.py --start_year 2020 --end_year 2022

# 2. Check results
ls data/
# Output: weather_2020_wide.parquet, weather_2021_wide.parquet, 
#         weather_2022_wide.parquet, weather_combined_sorted.parquet

# 3. Load final result
import dask.dataframe as dd
df = dd.read_parquet('data/weather_combined_sorted.parquet')
print(df.head())
```

## Troubleshooting

### Common Issues

- **No data found**: Some years may not have data available on S3
- **Memory issues**: Reduce the year range or use a smaller subset
- **Timeout errors**: Increase timeout or process fewer years at once
- **Permission errors**: Ensure write permissions for the data directory

### Column Structure Issues

If you encounter column name errors during concatenation:

1. **Check column structure**:
   ```bash
   python debug_columns.py
   ```

2. **Expected column structure**:
   - ID, year, ELEMENT, day_1, day_2, ..., day_365 (368 columns total)
   - All parquet files should have identical column structure

3. **Automatic fixes**: The script now automatically:
   - Detects column mismatches
   - Standardizes column structure
   - Reports detailed column differences
   - Ensures consistent concatenation

### Debug Tools

- `debug_columns.py`: Check column structure of existing parquet files
- Enhanced logging: Detailed column mismatch reporting
- Column verification: Final structure validation after concatenation
