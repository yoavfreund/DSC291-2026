# Plan: NYC Taxicab 2015 Data from S3 - Parquet Notebook

## Objective
Create an educational notebook that demonstrates reading NYC taxicab 2015 data from S3 (in Parquet format) using Dask and performing simple data manipulations. This notebook will teach:
- Reading Parquet files from S3 with Dask
- Basic data exploration and inspection
- Simple data transformations and aggregations
- Working with large datasets that don't fit in memory

**Style**: Educational, with clear explanations. Code cells should be concise and demonstrate key concepts. Markdown cells provide context and learning objectives.

## Notebook Structure
**File**: `dask-tutorial/06_parquet_s3_taxi.ipynb`

### Section 1: Introduction and Setup (3 cells)
- **Cell 1 (Markdown)**: Title and objectives
  - Introduction to NYC taxicab data
  - Why use Parquet format
  - Why use S3 for large datasets
  - Learning objectives: S3 access, Parquet reading, basic manipulations
  
- **Cell 2 (Code)**: Import libraries and setup
  ```python
  import dask.dataframe as dd
  import pandas as pd
  import numpy as np
  from dask.distributed import Client
  
  # Optional: Start a client for better performance
  client = Client()
  client
  ```

- **Cell 3 (Markdown)**: Data source information
  - S3 bucket: `s3://dask-data/nyc-taxi/nyc-2015.parquet/`
  - Data format: Parquet (columnar, compressed)
  - Public access (no credentials needed)
  - Year: 2015

### Section 2: Reading Data from S3 (3-4 cells)
- **Cell 4 (Markdown)**: Reading Parquet from S3
  - Explain `dd.read_parquet()` with S3 paths
  - Lazy loading concept
  - Storage options for public S3 buckets
  
- **Cell 5 (Code)**: Load data from S3
  ```python
  # Read NYC taxi 2015 data from S3
  df = dd.read_parquet(
      "s3://dask-data/nyc-taxi/nyc-2015.parquet/part.*.parquet",
      storage_options={"anon": True}  # Anonymous access for public bucket
  )
  
  print(f"Data loaded (lazy): {df}")
  print(f"Number of partitions: {df.npartitions}")
  ```

- **Cell 6 (Code)**: Inspect data structure (without computing full dataset)
  ```python
  # Get basic info without loading all data
  print("Columns:", list(df.columns))
  print("Data types:")
  print(df.dtypes)
  print("\nFirst few rows:")
  df.head()
  ```

- **Cell 7 (Code)**: Check data size
  ```python
  # Get approximate size (this requires some computation)
  print(f"Approximate number of rows: {len(df):,}")
  print(f"Memory usage estimate: {df.memory_usage(deep=True).sum().compute() / 1024**3:.2f} GB")
  ```

### Section 3: Basic Data Exploration (4-5 cells)
- **Cell 8 (Markdown)**: Data exploration overview
  - Understanding the dataset structure
  - Key columns in taxi data
  - Lazy vs eager operations
  
- **Cell 9 (Code)**: Sample data inspection
  ```python
  # Look at a sample of the data
  sample = df.head(10)
  print("Sample data:")
  print(sample)
  
  # Check for common taxi columns
  expected_cols = ['passenger_count', 'trip_distance', 'fare_amount', 
                   'tip_amount', 'total_amount', 'pickup_datetime', 
                   'dropoff_datetime']
  available = [col for col in expected_cols if col in df.columns]
  print(f"\nAvailable columns: {available}")
  ```

- **Cell 10 (Code)**: Basic statistics (lazy computation)
  ```python
  # Compute basic statistics for numerical columns
  # This is still lazy until .compute() is called
  numerical_cols = df.select_dtypes(include=[np.number]).columns
  print("Numerical columns:", list(numerical_cols))
  
  # Compute descriptive statistics
  stats = df[numerical_cols].describe().compute()
  print("\nDescriptive Statistics:")
  print(stats)
  ```

- **Cell 11 (Code)**: Check for missing values
  ```python
  # Count missing values per column
  missing = df.isnull().sum().compute()
  print("Missing values per column:")
  print(missing[missing > 0])
  print(f"\nTotal missing values: {missing.sum():,}")
  ```

### Section 4: Simple Data Manipulations (5-6 cells)
- **Cell 12 (Markdown)**: Data manipulation overview
  - Filtering data
  - Creating new columns
  - Grouping and aggregations
  - All operations are lazy until `.compute()`

- **Cell 13 (Code)**: Filter data
  ```python
  # Filter for trips with passengers
  df_with_passengers = df[df['passenger_count'] > 0]
  
  # Filter for trips with tips
  df_with_tips = df[df['tip_amount'] > 0]
  
  print(f"Trips with passengers: {len(df_with_passengers):,}")
  print(f"Trips with tips: {len(df_with_tips):,}")
  ```

- **Cell 14 (Code)**: Create derived columns
  ```python
  # Calculate tip percentage
  df = df.assign(
      tip_percentage=(df['tip_amount'] / df['fare_amount'] * 100).fillna(0),
      has_tip=(df['tip_amount'] > 0)
  )
  
  # Show new columns
  print("New columns added:")
  print(df[['tip_percentage', 'has_tip']].head())
  ```

- **Cell 15 (Code)**: Simple aggregations
  ```python
  # Average tip amount by passenger count
  avg_tip_by_passengers = df.groupby('passenger_count')['tip_amount'].mean().compute()
  print("Average tip amount by passenger count:")
  print(avg_tip_by_passengers)
  ```

- **Cell 16 (Code)**: More complex aggregation
  ```python
  # Summary statistics by passenger count
  summary = df.groupby('passenger_count').agg({
      'fare_amount': ['mean', 'std', 'count'],
      'tip_amount': ['mean', 'sum'],
      'trip_distance': 'mean'
  }).compute()
  
  print("Summary statistics by passenger count:")
  print(summary)
  ```

- **Cell 17 (Code)**: Visualize computation graph
  ```python
  # Show the computation graph for a complex operation
  result = df.groupby('passenger_count')['tip_amount'].mean()
  result.visualize()
  ```

### Section 5: Working with Partitions (3-4 cells)
- **Cell 18 (Markdown)**: Understanding partitions
  - What are partitions in Dask
  - How data is split across partitions
  - Repartitioning for better performance

- **Cell 19 (Code)**: Inspect partitions
  ```python
  print(f"Number of partitions: {df.npartitions}")
  print(f"Partition sizes (approximate):")
  
  # Get size of each partition
  partition_sizes = df.map_partitions(len).compute()
  print(partition_sizes.head(10))
  print(f"\nAverage partition size: {partition_sizes.mean():.0f} rows")
  ```

- **Cell 20 (Code)**: Repartition if needed
  ```python
  # Repartition to optimize for downstream operations
  # This is useful if partitions are too small or too large
  df_repartitioned = df.repartition(npartitions=10)
  print(f"Original partitions: {df.npartitions}")
  print(f"Repartitioned: {df_repartitioned.npartitions}")
  ```

### Section 6: Performance Considerations (2-3 cells)
- **Cell 21 (Markdown)**: Performance tips
  - When to use `.persist()` for repeated operations
  - Column selection to reduce memory
  - Filtering early in the pipeline

- **Cell 22 (Code)**: Optimize with column selection
  ```python
  # Select only needed columns to reduce memory usage
  df_subset = df[['passenger_count', 'fare_amount', 'tip_amount', 'trip_distance']]
  
  # This uses less memory than the full dataframe
  print("Reduced columns for analysis")
  print(f"Original columns: {len(df.columns)}")
  print(f"Selected columns: {len(df_subset.columns)}")
  ```

- **Cell 23 (Code)**: Persist for repeated operations
  ```python
  # If you'll use the filtered data multiple times, persist it
  df_filtered = df[df['fare_amount'] > 0].persist()
  
  # Now multiple operations on df_filtered will be faster
  mean_fare = df_filtered['fare_amount'].mean().compute()
  median_fare = df_filtered['fare_amount'].median().compute()
  
  print(f"Mean fare: ${mean_fare:.2f}")
  print(f"Median fare: ${median_fare:.2f}")
  ```

### Section 7: Summary and Next Steps (2 cells)
- **Cell 24 (Markdown)**: Key takeaways
  - Reading Parquet from S3 with Dask
  - Lazy evaluation and when to compute
  - Basic data manipulations on large datasets
  - Performance optimization techniques

- **Cell 25 (Markdown)**: Next steps and exercises
  - Try reading different years
  - Combine multiple years
  - More complex aggregations
  - Time-based analysis (if datetime columns available)
  - Export results to local Parquet files

## Key Concepts to Emphasize

1. **S3 Access**
   - Public buckets with `storage_options={"anon": True}`
   - S3 path patterns with wildcards
   - No need to download data locally

2. **Parquet Format**
   - Columnar storage (efficient for analytics)
   - Compression benefits
   - Schema preservation

3. **Lazy Evaluation**
   - Operations build a computation graph
   - `.compute()` triggers actual execution
   - Can optimize before execution

4. **Partitions**
   - Data split across partitions
   - Parallel processing
   - Repartitioning for optimization

5. **Memory Efficiency**
   - Work with datasets larger than memory
   - Column selection
   - Early filtering
   - Persist for repeated use

## Dependencies
- `dask[dataframe]` - for DataFrame operations
- `s3fs` - for S3 access (usually included with dask)
- `pyarrow` or `fastparquet` - for Parquet reading
- `dask.distributed` - for Client (optional but recommended)

## Data Source
- **S3 Path**: `s3://dask-data/nyc-taxi/nyc-2015.parquet/part.*.parquet`
- **Format**: Parquet
- **Access**: Public (anonymous)
- **Size**: Large enough to demonstrate out-of-core processing

## Testing Criteria
- All cells execute without errors
- Clear progression: setup → read → explore → manipulate
- Demonstrates lazy evaluation concepts
- Shows performance considerations
- Code is educational and well-commented
- Visualizations render correctly (if included)
- Execution time reasonable for educational purposes

## Implementation Notes

- Keep examples focused and educational
- Show both lazy operations and when to compute
- Include performance tips throughout
- Use realistic but manageable operations
- Add comments explaining key concepts
- Consider adding a simple visualization (histogram or bar chart)
- Make sure S3 access works (test with public bucket)
- Handle potential network/access issues gracefully

## Potential Challenges

1. **S3 Access**: May need to verify public bucket access
2. **Network Speed**: S3 reads can be slow; consider mentioning this
3. **Data Size**: Ensure operations complete in reasonable time
4. **Column Names**: Verify actual column names in the dataset
5. **Memory**: Some operations might still require significant memory

## Alternative Data Sources (if primary fails)

- Other public S3 datasets
- Local Parquet files (as fallback)
- Generate synthetic data for demonstration

---
**Status**: [✅] Draft | [ ] Approved | [ ] In Progress | [ ] Complete
**Last Updated**: 2024-12-19

