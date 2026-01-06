# Dask Delayed and Futures

**Title**: Dask Delayed and Futures  
**Subtitle**: Parallelizing Arbitrary Python Code  
**Author**: CSE255 - Scalable Data Analysis

---

## Slide 1: Title Page

---

## Slide 2: The Problem

**Not All Code is Array/DataFrame Operations:**
- Custom functions and workflows
- File processing pipelines
- API calls and web scraping
- Complex data transformations
- Machine learning preprocessing

**Need to Parallelize:**
- For loops with independent iterations
- Batch processing jobs
- Independent function calls

- **Graphics**: Problem scenario diagram

**Visual Concept:**
- Sequential processing: [Task1] → [Task2] → [Task3] (slow)
- Parallel processing: [Task1, Task2, Task3] simultaneously (fast)

---

## Slide 3: Two Approaches

**Delayed:**
- Lazy execution
- Builds computation graph first
- Executes when `.compute()` called
- Good for complex dependencies

**Futures:**
- Eager execution
- Executes immediately
- Non-blocking
- Good for simple parallelism

- **Graphics**: Comparison diagram

**Key Difference:**
- Delayed: Plan first, execute later
- Futures: Execute immediately

---

## Slide 4: What is dask.delayed?

**The `@delayed` Decorator:**
- Wraps functions to make them lazy
- Builds computation graph
- Executes when `.compute()` called
- Enables parallelization

**Basic Concept:**
```python
from dask import delayed

@delayed
def my_function(x):
    return x * 2

result = my_function(5)  # Returns Delayed object
final = result.compute()  # Actually executes
```

- **Graphics**: Delayed workflow diagram

**Visual Concept:**
- Function call → Delayed object (lightweight)
- Compute → Actual execution (heavy)

---

## Slide 5: Basic Delayed Example

```python
from dask import delayed

@delayed
def inc(x):
    return x + 1

# Returns Delayed object (no execution yet)
result = inc(1)
print(result)  # <Delayed 'inc-...'>

# Actually executes
final = result.compute()
print(final)  # 2
```

**Key Points:**
- Simple function decoration
- Returns Delayed object immediately
- Execution happens at `.compute()`

- **Graphics**: Code execution flow

**Timeline:**
1. `@delayed` decorates function
2. Function call returns Delayed object
3. `.compute()` triggers execution

---

## Slide 6: Delayed: Multiple Functions

```python
@delayed
def add(x, y):
    return x + y

# Create delayed computations
x = inc(1)  # Delayed
y = inc(2)  # Delayed
z = add(x, y)  # Delayed, depends on x and y

# Execute all at once
z.compute()  # Executes inc(1), inc(2), then add(3, 4)
```

**Key Features:**
- Builds dependency graph
- Dependencies executed first
- Parallel execution when possible

- **Graphics**: Task graph visualization

**Visual Concept:**
```
    inc(1) ──┐
            ├──→ add(3, 4) → result
    inc(2) ──┘
```

---

## Slide 7: Visualizing Task Graphs

```python
# Visualize the computation graph
z.visualize()
```

**What You See:**
- Nodes = tasks (functions to execute)
- Edges = dependencies (data flow)
- Helps understand execution plan

- **Graphics**: Example task graph output

**Benefits:**
- See computation structure
- Understand dependencies
- Debug complex workflows
- Optimize execution order

---

## Slide 8: Delayed: For Loops

**Parallelizing Loops:**
```python
@delayed
def process_file(filename):
    data = read_file(filename)
    return transform(data)

# Create list of delayed tasks
results = [process_file(f) for f in files]

# Execute all in parallel
final = dask.compute(*results)
```

**Key Advantage:**
- Loop iterations run in parallel
- Much faster than sequential loop
- Automatic dependency handling

- **Graphics**: Loop parallelization diagram

**Visual Concept:**
```
Sequential: file1 → file2 → file3 (slow)
Parallel:   file1, file2, file3 simultaneously (fast)
```

---

## Slide 9: Real-World Pattern: Read-Transform-Write

```python
@delayed
def process_file(filename):
    # Read
    data = read_file(filename)
    
    # Transform
    processed = transform(data)
    
    # Write
    output_path = f"results/{filename}"
    write_file(processed, output_path)
    
    return output_path

# Process all files in parallel
files = ['file1.csv', 'file2.csv', 'file3.csv']
tasks = [process_file(f) for f in files]
dask.compute(*tasks)
```

**Common Workflow:**
- Read data from files
- Apply transformations
- Write results
- All in parallel

- **Graphics**: Pipeline diagram

**Visual Concept:**
```
file1.csv → [Read] → [Transform] → [Write] → result1
file2.csv → [Read] → [Transform] → [Write] → result2
file3.csv → [Read] → [Transform] → [Write] → result3
(All in parallel)
```

---

## Slide 10: What are Futures?

**Futures:**
- Eager, non-blocking execution
- Returns immediately with Future object
- Computation happens in background
- Can check status anytime

**Key Difference from Delayed:**
- Delayed: Lazy (wait for compute)
- Futures: Eager (start immediately)

- **Graphics**: Futures timeline diagram

**Visual Concept:**
```
Time 0: Submit task → Get Future (pending)
Time 1: Task executing (in background)
Time 2: Task done → Future (finished)
```

---

## Slide 11: Futures: Basic Example

```python
from dask.distributed import Client

# Create client
client = Client()

# Submit task (returns immediately)
future = client.submit(inc, 1)  # Returns Future object

# Check status
print(future.status)  # 'pending' or 'finished'

# Get result (blocks until done)
result = future.result()  # Waits if not done
```

**Key Features:**
- Immediate submission
- Non-blocking
- Status tracking
- Result retrieval

- **Graphics**: Execution timeline

**Timeline:**
- `submit()`: Returns immediately
- Task executes in background
- `result()`: Blocks until done

---

## Slide 12: Futures: Status Tracking

```python
# Check status
future.status  # 'pending', 'finished', 'error'

# Check if done
if future.done():
    result = future.result()

# Get result (blocks if not done)
result = future.result()
```

**Status States:**
- **pending**: Task queued, not started
- **finished**: Task completed successfully
- **error**: Task failed

- **Graphics**: Status state diagram

**Use Cases:**
- Monitor progress
- Handle errors
- Collect results as they complete

---

## Slide 13: Futures: Map Pattern

```python
# Apply function to sequence
file_list = ['file1.csv', 'file2.csv', 'file3.csv']
futures = client.map(process_file, file_list)

# Collect results
results = client.gather(futures)
```

**Map vs Submit:**
- `submit()`: Single function call
- `map()`: Apply to sequence
- Both return Futures

- **Graphics**: Map operation diagram

**Visual Concept:**
```
file_list: [f1, f2, f3]
    ↓ map(process_file)
futures: [Future1, Future2, Future3]
    ↓ gather
results: [result1, result2, result3]
```

---

## Slide 14: Delayed vs Futures: Lazy vs Eager

**Delayed:**
- Build graph first
- Execute later (on `.compute()`)
- Scheduler can optimize
- Good for complex dependencies

**Futures:**
- Execute immediately
- No graph building
- Start as soon as submitted
- Good for simple parallelism

- **Graphics**: Side-by-side comparison

**Timeline Comparison:**
- Delayed: Build graph → Optimize → Execute
- Futures: Submit → Execute immediately

---

## Slide 15: Delayed vs Futures: When to Use

**Use Delayed when:**
- Complex dependencies
- Want graph optimization
- Need to see computation structure
- Building complex workflows

**Use Futures when:**
- Simple parallelism
- Need immediate feedback
- Real-time monitoring
- Independent tasks

- **Graphics**: Decision tree

**Decision Flow:**
1. Complex dependencies? → Delayed
2. Need immediate execution? → Futures
3. Want optimization? → Delayed
4. Simple parallelism? → Futures

---

## Slide 16: Futures: Real-Time Monitoring

```python
# Submit multiple tasks
futures = [client.submit(process, f) for f in files]

# Monitor as they complete
for future in futures:
    if future.done():
        try:
            result = future.result()
            print(f"Completed: {result}")
        except Exception as e:
            print(f"Error: {e}")
```

**Benefits:**
- See progress in real-time
- Handle results as they complete
- Identify failures early

- **Graphics**: Monitoring dashboard concept

**Use Cases:**
- Long-running tasks
- Progress reporting
- Early error detection

---

## Slide 17: Combining Delayed and Futures

```python
@delayed
def complex_task(data):
    # Can submit futures inside delayed
    futures = [client.submit(process, chunk) 
               for chunk in data]
    return client.gather(futures)

# Use delayed for outer structure
result = complex_task(large_data)
final = result.compute()
```

**Hybrid Approach:**
- Delayed for overall structure
- Futures for inner parallelism
- Best of both worlds

- **Graphics**: Combined workflow

**Visual Concept:**
- Outer: Delayed graph (optimized)
- Inner: Futures (immediate execution)

---

## Slide 18: Error Handling: Delayed

```python
@delayed
def risky_function(x):
    if x < 0:
        raise ValueError("Negative not allowed")
    return x * 2

try:
    result = risky_function(-1).compute()
except ValueError as e:
    print(f"Error: {e}")
```

**Error Behavior:**
- Errors raised at compute time
- Can catch exceptions normally
- Graph execution stops on error

- **Graphics**: Error flow diagram

**Best Practice:**
- Validate inputs early
- Use try/except around compute
- Check for None results

---

## Slide 19: Error Handling: Futures

```python
# Submit risky task
future = client.submit(risky_function, arg)

# Check for errors
try:
    result = future.result()
except Exception as e:
    print(f"Error: {e}")
    # Handle error appropriately
```

**Error Behavior:**
- Errors available immediately
- Can check `future.status == 'error'`
- Non-blocking error checking

- **Graphics**: Error handling comparison

**Advantages:**
- Immediate error detection
- Don't wait for all tasks
- Better for monitoring

---

## Slide 20: Best Practices: Delayed

**Use Delayed for:**
- Complex workflows with dependencies
- When you want graph optimization
- Building reusable computation pipelines
- Debugging computation structure

**Tips:**
- Leverage graph optimization
- Batch operations when possible
- Use `.visualize()` to understand structure
- Keep functions pure (no side effects)

- **Graphics**: Best practices checklist

**Key Principles:**
- Build clear dependency graphs
- Minimize data movement
- Use persist for repeated computations

---

## Slide 21: Best Practices: Futures

**Use Futures for:**
- Simple parallelism
- Independent tasks
- Real-time monitoring needs
- When immediate execution is important

**Tips:**
- Monitor progress regularly
- Handle errors promptly
- Use gather() for collecting results
- Don't create too many futures at once

- **Graphics**: Best practices checklist

**Key Principles:**
- Submit tasks in batches
- Monitor status regularly
- Clean up completed futures
- Handle errors gracefully

---

## Slide 22: Summary

**Key Takeaways:**
- **Delayed**: Lazy, graph-based, optimized
- **Futures**: Eager, immediate, simple
- Choose based on use case
- Both enable parallel execution

**When to Use What:**
- Complex workflows → Delayed
- Simple parallelism → Futures
- Need optimization → Delayed
- Need monitoring → Futures

- **Graphics**: Key concepts diagram

**Next Steps:**
- Practice with real examples
- Learn distributed computing
- Explore performance optimization

