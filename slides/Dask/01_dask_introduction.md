# Introduction to Dask

**Title**: Introduction to Dask  
**Subtitle**: Scalable Analytics in Python  
**Author**: CSE255 - Scalable Data Analysis

---

## Slide 1: Title Page

---

## Slide 2: The Big Data Problem

- **Memory limits**: "What happens when data > RAM?"
- Traditional tools (NumPy, Pandas) fail with large datasets
- Need for parallel and distributed computing
- **Graphics**: Diagram showing data size vs memory capacity

**Visual Concept**: 
- Left side: Small data (fits in RAM) → Pandas/NumPy work fine
- Right side: Large data (exceeds RAM) → Need Dask/Spark

---

## Slide 3: What is Dask?

- Parallel computing library for Python
- Scales from laptop to cluster
- Familiar APIs (NumPy-like, Pandas-like)
- **Graphics**: Dask logo

![Dask Logo](https://docs.dask.org/en/latest/_images/dask_horizontal.svg)

---

## Slide 4: Dask's Place in the Ecosystem

**Tool Comparison:**

| Tool | Scale | Language | Use Case |
|------|-------|----------|----------|
| NumPy/Pandas | Single machine, in-memory | Python | Small-medium data |
| Dask | Single machine or cluster, larger-than-memory | Python | Large data, familiar APIs |
| Spark | Cluster | JVM (Scala/Java/Python) | Very large data, enterprise |

- **Graphics**: Ecosystem diagram showing tool positioning

**Visual Concept**: 
- NumPy/Pandas: Small box (single machine)
- Dask: Medium box (single machine or cluster)
- Spark: Large box (cluster)

---

## Slide 5: Why Dask?

- **Familiar APIs**: Works like pandas and NumPy
- **Pure Python**: No JVM required
- **Flexible**: Lazy evaluation enables optimization
- **Scalable**: From laptop to cluster
- **Graphics**: Comparison table

**Key Advantages:**
- If you know pandas → you know Dask DataFrames
- If you know NumPy → you know Dask Arrays
- No need to learn new syntax

---

## Slide 6: Core Concept: Lazy Evaluation

- Build computation graph first
- Execute only when needed (`.compute()`)
- Enables optimization by scheduler
- **Graphics**: Simple task graph visualization

**Example:**
```python
df = dd.read_csv('data/*.csv')  # No data loaded yet
result = df.groupby('col').sum()  # Still no data loaded
final = result.compute()  # NOW data is loaded and processed
```

**Visual Concept**: 
- Step 1: Build graph (lightweight)
- Step 2: Optimize graph
- Step 3: Execute (heavy computation)

---

## Slide 7: Task Graphs

- Dask builds graphs of operations
- **Nodes** = tasks (individual operations)
- **Edges** = dependencies (data flow)
- Scheduler optimizes execution order
- **Graphics**: Example task graph diagram

**Visual Concept:**
```
read_file1 → process1 ─┐
read_file2 → process2 ──→ combine → write
read_file3 → process3 ─┘
```

---

## Slide 8: Dask Collections Overview

**Four Main Collections:**

1. **DataFrame**: Many pandas DataFrames
   - Tabular data, pandas-like API
   
2. **Array**: Many NumPy arrays
   - N-dimensional arrays, NumPy-like API
   
3. **Bag**: Many Python objects
   - Unstructured data, functional operations
   
4. **Delayed**: Arbitrary Python functions
   - Custom workflows, general parallelization

- **Graphics**: Visual representation of each collection type

**Visual Concept**: 
- DataFrame: Table icon with multiple partitions
- Array: Grid icon with blocks
- Bag: Container icon with items
- Delayed: Function icon with graph

---

## Slide 9: Dask DataFrame = Many Pandas DataFrames

- One Dask DataFrame = collection of pandas DataFrames
- Partitioned along index
- Operations applied to each partition in parallel
- **Graphics**: Diagram showing partitioned DataFrame structure

![Dask DataFrame Structure](https://docs.dask.org/en/stable/_images/dask-dataframe.svg)

**Key Points:**
- Each partition is a real pandas DataFrame
- Partitions can be on different machines
- Operations happen in parallel across partitions

---

## Slide 10: When to Use Dask

**Use Dask when:**
- Data larger than memory (or close to it)
- Need parallel processing
- Want familiar pandas/NumPy APIs
- Need to scale beyond single machine

- **Graphics**: Decision flowchart

**Decision Tree:**
1. Does data fit in memory? → No → Use Dask
2. Need parallel processing? → Yes → Use Dask
3. Want pandas-like API? → Yes → Use Dask DataFrame

---

## Slide 11: When NOT to Use Dask

**Don't use Dask when:**
- Small datasets (use pandas/NumPy directly)
- Simple operations (overhead not worth it)
- Real-time processing (use streaming tools)
- Data fits comfortably in memory

- **Graphics**: Comparison scenarios

**Rule of Thumb:**
- If you have 5-10x RAM compared to dataset size → pandas is fine
- If dataset approaches or exceeds RAM → consider Dask

---

## Slide 12: Dask vs Alternatives

**vs Pandas:**
- Pandas: Single machine, in-memory
- Dask: Single machine or cluster, larger-than-memory, parallel

**vs Spark:**
- Spark: JVM-based, cluster-focused, enterprise
- Dask: Python-native, flexible, easier to learn

**vs NumPy:**
- NumPy: Single machine, in-memory arrays
- Dask: Single machine or cluster, larger arrays, distributed

- **Graphics**: Feature comparison table

---

## Slide 13: Installation and Setup

**Basic Installation:**
```bash
pip install dask
```

**Complete Installation (recommended):**
```bash
pip install dask[complete]
```

**For Distributed Computing:**
```bash
pip install dask[distributed]
```

**Graphics**: Installation command examples

**What's Included:**
- `dask[complete]`: All optional dependencies
- `dask[distributed]`: Distributed scheduler
- `dask[dataframe]`: DataFrame-specific dependencies

---

## Slide 14: Basic Example

```python
import dask.dataframe as dd

# Read data (lazy - no data loaded yet)
df = dd.read_csv('data/*.csv')

# Build computation (still lazy)
result = df.groupby('column').sum()

# Actually execute
result.compute()  # NOW data is loaded and processed
```

**What Happens:**
1. `read_csv()`: Creates task graph for reading files
2. `groupby().sum()`: Adds grouping tasks to graph
3. `compute()`: Executes all tasks in parallel

- **Graphics**: Code visualization showing lazy vs eager

---

## Slide 15: Summary

**Key Takeaways:**
- Dask = parallel computing for Python
- Familiar APIs (pandas, NumPy)
- Lazy evaluation for optimization
- Scales from laptop to cluster

**Next Steps:**
- Learn Dask DataFrames (most common use case)
- Understand delayed and futures
- Explore distributed computing

- **Graphics**: Key concepts diagram

**Core Concepts:**
- Lazy evaluation
- Task graphs
- Partitioned collections
- Familiar APIs

