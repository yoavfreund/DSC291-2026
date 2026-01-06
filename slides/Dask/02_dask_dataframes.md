# Dask DataFrames

**Title**: Dask DataFrames  
**Subtitle**: Parallel Pandas for Large Datasets  
**Author**: CSE255 - Scalable Data Analysis

---

## Slide 1: Title Page

---

## Slide 2: DataFrame Architecture

- One Dask DataFrame = many pandas DataFrames
- Partitioned along index
- Each partition is a pandas DataFrame
- Operations applied to each partition in parallel

**Graphics**: Partitioned DataFrame diagram

![Dask DataFrame Structure](https://docs.dask.org/en/stable/_images/dask-dataframe.svg)

**Key Insight:**
- Think of Dask DataFrame as a "meta-DataFrame"
- Contains references to many pandas DataFrames
- Each partition can be on different machines

---

## Slide 3: Blocked Parallel Strategy

**How It Works:**
1. Data split into blocks (partitions)
2. Operations applied to each block independently
3. Results combined to form final answer

**Example:**
- 1TB dataset → 10 partitions of 100GB each
- Each partition processed in parallel
- Results merged at the end

- **Graphics**: Diagram showing block operations

**Visual Concept:**
```
Large Dataset
    ↓
[Partition 1] [Partition 2] [Partition 3] [Partition 4]
    ↓              ↓              ↓              ↓
[Process 1]   [Process 2]   [Process 3]   [Process 4]
    ↓              ↓              ↓              ↓
    └──────────────┴──────────────┴──────────────┘
                    ↓
              Combined Result
```

---

## Slide 4: Creating DataFrames: From Files

```python
import dask.dataframe as dd

# Read CSV files
df = dd.read_csv('data/*.csv')

# Read Parquet files
df = dd.read_parquet('s3://bucket/data/*.parquet')
```

**Key Features:**
- Supports glob patterns (`*`, `?`, `[...]`)
- Automatic schema inference
- Lazy loading (no data read until `.compute()`)

- **Graphics**: File reading visualization

**What Happens:**
- Dask scans file paths
- Infers schema from first file
- Creates task graph for reading
- Data not loaded until needed

---

## Slide 5: Creating DataFrames: From Pandas

```python
import pandas as pd
import dask.dataframe as dd

# Create pandas DataFrame
pandas_df = pd.DataFrame({
    'col1': range(1000),
    'col2': range(1000, 2000)
})

# Convert to Dask DataFrame
dask_df = dd.from_pandas(pandas_df, npartitions=4)
```

**Key Points:**
- Convert existing pandas DataFrames
- Specify number of partitions
- Useful for testing or small-to-medium data

- **Graphics**: Conversion diagram

**Partitioning:**
- `npartitions=4` splits data into 4 partitions
- Each partition is a pandas DataFrame
- Index determines how data is split

---

## Slide 6: Lazy Evaluation in Action

**What "Lazy" Means:**
- `dd.read_csv()` doesn't load data
- Just creates task graph
- `.compute()` triggers actual loading

**Example:**
```python
df = dd.read_csv('data/*.csv')  # Instant (no data loaded)
print(df)  # Shows metadata only
result = df.sum()  # Still no data loaded
final = result.compute()  # NOW data is loaded
```

- **Graphics**: Before/after compute visualization

**Visual Concept:**
- Before compute: Lightweight graph structure
- After compute: Actual data in memory
- Scheduler optimizes execution order

---

## Slide 7: Basic Operations: Inspection

```python
df.head()      # Triggers computation (loads first partition)
df.tail()      # Triggers computation (loads last partition)
df.describe()  # Triggers computation (loads all partitions)
df.dtypes      # No computation needed (metadata)
df.columns     # No computation needed (metadata)
```

**Key Distinction:**
- **Metadata operations**: No computation (fast)
- **Data operations**: Trigger computation (slower)

- **Graphics**: Operation classification

**When Computation Happens:**
- `.head()`, `.tail()`: Loads partial data
- `.describe()`, `len()`: Loads all data
- `.dtypes`, `.columns`: No data loading

---

## Slide 8: Filtering and Selection

```python
# Filter rows
filtered = df[df['column'] > 100]

# Select columns
selected = df[['col1', 'col2']]

# Combined
result = df[df['value'] > 50][['col1', 'col2']]
```

**How It Works:**
- Works exactly like pandas
- Applied to each partition independently
- Filtering reduces data size early

- **Graphics**: Filtering operation diagram

**Visual Concept:**
```
Partition 1: [row1, row2, row3, row4, row5]
    ↓ filter(column > 100)
Partition 1: [row2, row4]  (filtered)
```

---

## Slide 9: GroupBy Operations

```python
# Group by category
grouped = df.groupby('category')

# Aggregate
result = grouped['value'].sum()
result.compute()

# Multiple aggregations
result = grouped.agg({
    'value': ['sum', 'mean', 'count']
})
```

**Key Features:**
- Distributed groupby
- Handles shuffles efficiently
- Works like pandas groupby

- **Graphics**: GroupBy visualization across partitions

**Visual Concept:**
```
Partition 1: [A: 1, B: 2, A: 3]
Partition 2: [B: 4, A: 5, C: 6]
    ↓ groupby
A: [1, 3, 5] → sum = 9
B: [2, 4] → sum = 6
C: [6] → sum = 6
```

---

## Slide 10: Aggregations

```python
# Column-wise aggregations
df.sum()
df.mean()
df.count()
df.max()
df.min()

# Row-wise aggregations
df.sum(axis=1)
```

**How It Works:**
- Applied per partition, then combined
- Efficient for large datasets
- Same API as pandas

- **Graphics**: Aggregation flow diagram

**Example:**
```
Partition 1: sum = 100
Partition 2: sum = 200
Partition 3: sum = 150
    ↓ combine
Total sum = 450
```

---

## Slide 11: Joins and Merges

```python
# Merge two DataFrames
result = dd.merge(df1, df2, on='key')

# Left join
result = dd.merge(df1, df2, on='key', how='left')

# Multiple keys
result = dd.merge(df1, df2, on=['key1', 'key2'])
```

**Key Features:**
- Handles large joins efficiently
- Partition-aware (optimizes data movement)
- Same API as pandas merge

- **Graphics**: Join operation diagram

**Performance:**
- Dask optimizes join strategy
- Minimizes data shuffling
- Can handle joins larger than memory

---

## Slide 12: Reading from S3

```python
# Read Parquet from S3
df = dd.read_parquet('s3://bucket/data/*.parquet')

# Read CSV from S3
df = dd.read_csv('s3://bucket/data/*.csv')
```

**Key Features:**
- Direct S3 access (no download needed)
- Uses IAM roles (no credentials needed on EC2)
- Works with partitioned data

- **Graphics**: S3 connection diagram

**Setup Required:**
- IAM role attached to EC2 instance
- Bucket permissions configured
- That's it! No credentials in code

---

## Slide 13: Reading Parquet Files

**Why Parquet?**
- **Columnar format**: Read only needed columns
- **Efficient compression**: 3-10x smaller than CSV
- **Schema preservation**: Data types stored with data
- **Cross-platform**: Works with many tools

- **Graphics**: Parquet structure diagram

**Visual Concept:**
```
Parquet File:
├── Column 1: [val1, val2, val3, ...]
├── Column 2: [val1, val2, val3, ...]
└── Column 3: [val1, val2, val3, ...]

Only read columns you need!
```

---

## Slide 14: Writing Results

```python
# Write to Parquet
df.to_parquet('s3://bucket/output/')

# Write to CSV
df.to_csv('s3://bucket/output/*.csv')

# With options
df.to_parquet(
    's3://bucket/output/',
    compression='snappy',
    write_index=False
)
```

**Key Features:**
- Writes partitioned files
- One file per partition
- Maintains partitioning structure

- **Graphics**: Writing process diagram

**Output Structure:**
```
output/
├── part.0.parquet
├── part.1.parquet
├── part.2.parquet
└── part.3.parquet
```

---

## Slide 15: Index Management

**Index Determines Partitioning:**
- Index values determine which partition data goes to
- Setting index can be expensive operation

```python
# Set index (may trigger shuffle)
df = df.set_index('date')

# Repartition
df = df.repartition(npartitions=8)

# Reset index
df = df.reset_index()
```

- **Graphics**: Index partitioning diagram

**Best Practice:**
- Set index during read if possible
- Avoid setting index on large datasets unnecessarily

---

## Slide 16: When Operations Trigger Computation

**Explicit Triggers:**
- `.compute()` - explicit trigger
- `len(df)` - triggers computation
- `df.head()` - triggers partial computation

**Lazy Operations:**
- Most operations are lazy
- Build task graph only
- No data loaded until compute

- **Graphics**: Trigger points diagram

**Example:**
```python
df = dd.read_csv('data/*.csv')  # Lazy
filtered = df[df['col'] > 100]  # Lazy
grouped = filtered.groupby('cat')  # Lazy
result = grouped.sum()  # Lazy
final = result.compute()  # TRIGGERS computation
```

---

## Slide 17: Memory Management

**Key Principles:**
- Each partition fits in memory
- Operations stream through partitions
- `.persist()` caches in memory

**Example:**
```python
# Stream through partitions (low memory)
result = df.groupby('cat').sum().compute()

# Cache in memory (higher memory, faster)
df_persisted = df.persist()
result1 = df_persisted.groupby('cat').sum()
result2 = df_persisted.groupby('cat').mean()
```

- **Graphics**: Memory usage diagram

**Memory Strategy:**
- Default: Stream (low memory)
- Use persist: When reusing data (higher memory)

---

## Slide 18: Performance Tips: Partition Size

**Partition Size Guidelines:**
- **Too small**: Overhead dominates (many small tasks)
- **Too large**: Memory issues (partition doesn't fit)
- **Rule of thumb**: 100MB-1GB per partition

**Adjusting Partitions:**
```python
# Repartition to different size
df = df.repartition(npartitions=8)  # Fewer, larger partitions
df = df.repartition(npartitions=32)  # More, smaller partitions
```

- **Graphics**: Performance curve

**Visual Concept:**
- X-axis: Partition size
- Y-axis: Performance
- Sweet spot in middle (100MB-1GB)

---

## Slide 19: Performance Tips: Operations

**Optimization Strategies:**
1. **Filter early**: Reduces data size
   ```python
   # Good: Filter first
   df[df['value'] > 100].groupby('cat').sum()
   
   # Bad: Groupby first
   df.groupby('cat').sum()[result > 100]
   ```

2. **Use appropriate dtypes**: Smaller dtypes = less memory
   ```python
   df['id'] = df['id'].astype('int32')  # Instead of int64
   ```

3. **Avoid iterating over rows**: Use vectorized operations

- **Graphics**: Optimization checklist

---

## Slide 20: Common Pitfalls: Setting Index

```python
# SLOW: Sets index after loading all data
df = dd.read_parquet('s3://bucket/data/*.parquet')
df = df.set_index('date')  # Expensive shuffle!

# BETTER: Set index during read
df = dd.read_parquet(
    's3://bucket/data/*.parquet',
    index='date'  # Index set during read
)
```

**Why It Matters:**
- Setting index requires data shuffle
- Can be very expensive for large datasets
- Set index during read when possible

- **Graphics**: Performance comparison

---

## Slide 21: Common Pitfalls: Iterating

```python
# BAD: Iterating over partitions
for partition in df.to_delayed():
    process(partition)

# BETTER: Use vectorized operations
df.apply(func, axis=1)

# BEST: Use built-in operations
df.groupby('cat').apply(func)
```

**Key Principle:**
- Avoid Python loops
- Use vectorized operations
- Leverage Dask's parallelization

- **Graphics**: Anti-pattern vs pattern

**Performance Impact:**
- Loops: Sequential, slow
- Vectorized: Parallel, fast

---

## Slide 22: Real-World Example: Flight Data

```python
# Read flight data from S3
df = dd.read_parquet('s3://bucket/flights/*.parquet')

# Filter delayed flights
delayed_flights = df[df['dep_delay'] > 0]

# Group by airline
by_airline = delayed_flights.groupby('carrier').size()

# Compute result
result = by_airline.compute()

# Display
print(result)
```

**Complete Workflow:**
1. Read data (lazy)
2. Filter (lazy)
3. Group and aggregate (lazy)
4. Compute (executes everything)

- **Graphics**: Workflow diagram

**What Happens:**
- All operations build task graph
- Scheduler optimizes execution
- Data processed in parallel
- Results combined

---

## Slide 23: Summary

**Key Takeaways:**
- Dask DataFrame = many pandas DataFrames
- Lazy evaluation for efficiency
- Pandas-like API (familiar)
- Scales to large datasets

**Best Practices:**
- Filter early
- Right-size partitions
- Use persist strategically
- Avoid unnecessary index operations

- **Graphics**: Key takeaways

**Next Steps:**
- Learn delayed and futures
- Explore distributed computing
- Practice with real datasets

