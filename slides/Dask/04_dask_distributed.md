# Distributed Dask

**Title**: Distributed Dask  
**Subtitle**: Scaling Across Machines  
**Author**: CSE255 - Scalable Data Analysis

---

## Slide 1: Title Page

---

## Slide 2: Schedulers Overview

**Three Types of Schedulers:**

1. **Threaded**: Single machine, shared memory
   - Uses threads (lightweight)
   - Good for I/O-bound tasks
   - Limited by Python GIL

2. **Processes**: Single machine, separate memory
   - Uses processes (heavier)
   - Good for CPU-bound tasks
   - Bypasses Python GIL

3. **Distributed**: Multiple machines, network
   - Uses network communication
   - Scales to clusters
   - Best for large-scale computing

- **Graphics**: Scheduler comparison diagram

**Visual Concept:**
- Threaded: Single box with threads
- Processes: Single box with processes
- Distributed: Multiple boxes connected

---

## Slide 3: Why Distributed?

**When Single Machine Isn't Enough:**
- Need more memory (data > single machine RAM)
- Need more CPU cores
- Need to scale to cluster
- Want fault tolerance

**Benefits:**
- Scale beyond single machine limits
- Utilize multiple machines
- Handle larger datasets
- Better resource utilization

- **Graphics**: Scaling diagram

**Visual Concept:**
- Single machine: Limited resources
- Distributed: Combined resources from multiple machines

---

## Slide 4: Client-Worker Architecture

**Three Components:**

1. **Client**: 
   - Submits tasks
   - Your Python session
   - Coordinates computation

2. **Workers**: 
   - Execute tasks
   - Hold data in memory
   - Report status to scheduler

3. **Scheduler**: 
   - Coordinates execution
   - Assigns tasks to workers
   - Manages dependencies

- **Graphics**: Architecture diagram

**Visual Concept:**
```
Client (your code)
    ↓
Scheduler (coordinates)
    ↓
Workers (execute tasks)
```

---

## Slide 5: Creating a Client

```python
from dask.distributed import Client

# Local cluster (single machine)
client = Client(n_workers=4)

# Remote cluster (multiple machines)
client = Client('tcp://scheduler-address:8786')
```

**Local vs Remote:**
- **Local**: All on one machine (good for testing)
- **Remote**: Across multiple machines (production)

- **Graphics**: Client setup diagram

**Common Setup:**
- Development: Local client
- Production: Remote cluster (EC2 instances)

---

## Slide 6: Client Configuration

```python
client = Client(
    n_workers=4,              # Number of worker processes
    threads_per_worker=2,     # Threads per worker
    memory_limit='8GB'        # Memory per worker
)
```

**Configuration Options:**
- `n_workers`: Number of worker processes
- `threads_per_worker`: Threads per worker
- `memory_limit`: Memory limit per worker
- `processes`: Use processes vs threads

- **Graphics**: Configuration options

**Resource Planning:**
- Balance workers vs threads
- Consider available memory
- Match to your workload

---

## Slide 7: Workers and Cores

**Worker Structure:**
- Each worker = separate process
- Workers have cores (threads)
- Balance workers vs cores per worker

**Example:**
- 8 CPU cores available
- Option 1: 4 workers × 2 threads = 8 threads
- Option 2: 8 workers × 1 thread = 8 threads

- **Graphics**: Worker/core diagram

**Visual Concept:**
```
Machine with 8 cores:
├── Worker 1 (2 threads)
├── Worker 2 (2 threads)
├── Worker 3 (2 threads)
└── Worker 4 (2 threads)
```

---

## Slide 8: The Dashboard

**Real-Time Monitoring:**
- Task stream visualization
- Worker status
- Memory usage
- Performance metrics

**Access:**
- URL shown when creating Client
- Usually: `http://localhost:8787/status`
- Opens in browser

- **Graphics**: Dashboard screenshot/description

**Key Views:**
- Task Stream: See tasks executing
- Worker Memory: Memory usage per worker
- Progress: Overall computation progress

---

## Slide 9: Dashboard: Task Stream

**What You See:**
- Tasks executing over time
- Worker utilization
- Bottlenecks and idle time
- Task dependencies

**Use Cases:**
- Identify performance bottlenecks
- See if workers are busy
- Understand computation flow
- Debug slow operations

- **Graphics**: Task stream visualization

**Visual Concept:**
- Timeline showing tasks
- Color-coded by worker
- Gaps show idle time

---

## Slide 10: Dashboard: Worker Memory

**Memory Monitoring:**
- Memory usage per worker
- Identify memory pressure
- Optimize partition sizes
- Prevent out-of-memory errors

**What to Look For:**
- Workers near memory limit
- Uneven memory distribution
- Memory leaks

- **Graphics**: Memory usage chart

**Visual Concept:**
- Bar chart per worker
- Shows current memory usage
- Red zone = near limit

---

## Slide 11: Performance Monitoring

```python
# Get performance info
client.profile()      # Detailed profiling
client.nthreads()     # Total threads
client.ncores()       # Total cores
client.scheduler_info # Scheduler details
```

**Monitoring Tools:**
- Client methods for info
- Dashboard for visualization
- Logs for debugging

- **Graphics**: Monitoring metrics

**Key Metrics:**
- Worker count
- Memory usage
- Task completion rate
- Network traffic

---

## Slide 12: Persist vs Compute

```python
# Compute: execute and return result
result = df.sum().compute()
# Result is a pandas Series (small)
# DataFrame is discarded

# Persist: execute and keep in memory
df_persisted = df.persist()
# DataFrame stays in memory
# Can reuse without recomputation
```

**When to Use:**
- **Compute**: One-time results, final output
- **Persist**: Intermediate results, reused data

- **Graphics**: Persist vs compute diagram

**Visual Concept:**
- Compute: Execute → Return → Discard
- Persist: Execute → Keep in memory → Reuse

---

## Slide 13: Memory Management

**Key Principles:**
- Each worker has memory limit
- Partitions should fit in worker memory
- Monitor memory usage
- Use persist strategically

**Best Practices:**
- Right-size partitions (100MB-1GB)
- Monitor dashboard
- Use persist for repeated computations
- Clear persisted data when done

- **Graphics**: Memory distribution diagram

**Visual Concept:**
```
Worker 1: [Partition 1, Partition 2] (4GB used / 8GB limit)
Worker 2: [Partition 3, Partition 4] (3GB used / 8GB limit)
Worker 3: [Partition 5] (2GB used / 8GB limit)
```

---

## Slide 14: Performance Optimization: Partitioning

**Partitioning Strategy:**
- Right-size partitions
- Align with worker memory
- Consider data locality
- Balance partition count

**Guidelines:**
- 100MB-1GB per partition
- Match to worker memory
- More partitions = more parallelism (but more overhead)
- Fewer partitions = less overhead (but less parallelism)

- **Graphics**: Partitioning strategies

**Example:**
- 10GB dataset, 4 workers with 4GB each
- Good: 10-20 partitions of 500MB-1GB each
- Bad: 1000 partitions of 10MB each (too much overhead)

---

## Slide 15: Performance Optimization: Caching

```python
# Cache intermediate results
df_filtered = df[df['value'] > 100].persist()

# Reuse cached data
result1 = df_filtered.groupby('cat').sum()
result2 = df_filtered.groupby('cat').mean()
result3 = df_filtered.groupby('cat').count()
```

**Benefits:**
- Avoid recomputation
- Faster subsequent operations
- Uses more memory

- **Graphics**: Caching benefit diagram

**Visual Concept:**
- Without persist: Filter → Groupby → Filter → Groupby (recomputes filter)
- With persist: Filter → Persist → Groupby → Groupby (reuses filtered data)

---

## Slide 16: Debugging: Task Failures

**When Tasks Fail:**
1. Check dashboard for errors
2. Review task status
3. Check worker logs
4. Look for error messages

**Common Issues:**
- Out of memory errors
- Network connectivity
- Data format issues
- Worker crashes

- **Graphics**: Debugging workflow

**Debugging Steps:**
1. Check dashboard error view
2. Review task tracebacks
3. Check worker logs
4. Verify data format
5. Test with smaller data

---

## Slide 17: Debugging: Slow Performance

**Identifying Bottlenecks:**
- Check task stream for idle workers
- Verify data locality (minimize network transfer)
- Check network bandwidth
- Look for straggler tasks

**Common Causes:**
- Data shuffling (network transfer)
- Uneven partition sizes
- Worker overload
- Network latency

- **Graphics**: Performance debugging checklist

**Optimization Strategies:**
- Co-locate data and computation
- Balance partition sizes
- Increase workers if CPU-bound
- Increase memory if memory-bound

---

## Slide 18: Scaling Considerations

**Scaling Strategies:**
- Add more workers (horizontal scaling)
- Increase worker memory (vertical scaling)
- Optimize data partitioning
- Consider data locality

**Trade-offs:**
- More workers = more parallelism but more overhead
- Larger workers = more memory but fewer workers
- Network transfer can be bottleneck

- **Graphics**: Scaling strategies

**Visual Concept:**
- Start: 2 workers
- Scale up: 4 workers, 8 workers, 16 workers
- Each step adds capacity

---

## Slide 19: Connecting to EC2 Cluster

```python
# On EC2 instance
from dask.distributed import Client

# Connect to scheduler
client = Client('tcp://scheduler-ip:8786')

# Or create local cluster on instance
client = Client(n_workers=4)
```

**EC2 Setup:**
- Scheduler on one EC2 instance
- Workers on other EC2 instances
- Client can be anywhere (laptop, EC2, etc.)

- **Graphics**: EC2 cluster diagram

**Visual Concept:**
```
EC2 Instance 1: Scheduler
EC2 Instance 2: Worker 1
EC2 Instance 3: Worker 2
EC2 Instance 4: Worker 3
Your Laptop: Client (submits tasks)
```

---

## Slide 20: Best Practices

**Resource Management:**
- Right-size partitions
- Use persist strategically
- Monitor memory usage
- Clean up when done

**Performance:**
- Monitor dashboard regularly
- Optimize data partitioning
- Minimize data shuffling
- Use appropriate number of workers

**Reliability:**
- Handle errors gracefully
- Use try/except blocks
- Check task status
- Log important operations

- **Graphics**: Best practices summary

---

## Slide 21: Summary

**Key Takeaways:**
- Distributed enables scaling beyond single machine
- Client coordinates workers via scheduler
- Dashboard provides real-time monitoring
- Optimize for your specific workload

**Next Steps:**
- Practice with local cluster
- Explore dashboard features
- Optimize your workflows
- Scale to EC2 cluster

- **Graphics**: Key takeaways

**Core Concepts:**
- Client-Worker-Scheduler architecture
- Persist vs compute
- Memory management
- Performance optimization

