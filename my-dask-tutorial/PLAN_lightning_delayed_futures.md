# Plan: Lightning Notebook for dask.delayed and dask Futures

## Objective
Create a concise, quick-to-complete notebook that demonstrates the essential capabilities of both `dask.delayed` and `dask.futures`, highlighting their key differences and when to use each.

**Style**: Lightning-fast introduction. Code cells minimal and focused. Markdown cells brief but clear. Aim for ~15-20 minutes total execution time.

## Notebook Structure
**File**: `dask-tutorial/03b_lightning_delayed_futures.ipynb`

### Section 1: Introduction (2 cells)
- **Cell 1 (Markdown)**: Title, brief overview
  - What are delayed and futures?
  - Key difference: lazy (delayed) vs eager (futures)
  - When to use each: delayed for graph-building workflows, futures for immediate execution
  
- **Cell 2 (Code)**: Setup
  ```python
  from dask.distributed import Client
  from time import sleep
  import dask
  
  client = Client(n_workers=2)  # Small cluster for demo
  ```

### Section 2: dask.delayed Basics (4-5 cells)
- **Cell 3 (Markdown)**: Introduction to delayed
  - Lazy evaluation: builds a graph, doesn't execute until `.compute()`
  - Perfect for: for-loops, workflows with dependencies
  
- **Cell 4 (Code)**: Simple sequential example (baseline)
  ```python
  def process(x):
      sleep(0.5)
      return x * 2
  
  %%time
  results = [process(i) for i in range(4)]
  ```

- **Cell 5 (Code)**: Parallelize with delayed
  ```python
  @dask.delayed
  def process(x):
      sleep(0.5)
      return x * 2
  
  %%time
  delayed_results = [process(i) for i in range(4)]
  final = dask.compute(*delayed_results)  # or dask.compute(delayed_results)
  ```

- **Cell 6 (Code)**: Visualize the graph
  ```python
  # Show task graph
  delayed_results[0].visualize()  # or create a sum/composite operation
  ```

### Section 3: dask.delayed with Dependencies (3-4 cells)
- **Cell 7 (Markdown)**: Handling dependencies
  - Dask automatically handles dependencies in the graph
  - Example: process data, then aggregate
  
- **Cell 8 (Code)**: Dependent operations
  ```python
  @dask.delayed
  def load(filename):
      sleep(0.3)
      return f"data_{filename}"
  
  @dask.delayed
  def process(data):
      sleep(0.5)
      return data.upper()
  
  @dask.delayed
  def aggregate(results):
      sleep(0.2)
      return len(results)
  
  # Build graph with dependencies
  files = ['a', 'b', 'c']
  loaded = [load(f) for f in files]
  processed = [process(d) for d in loaded]
  result = aggregate(processed)
  
  result.visualize()
  result.compute()
  ```

### Section 4: Futures Basics (4-5 cells)
- **Cell 9 (Markdown)**: Introduction to futures
  - Eager execution: starts immediately when submitted
  - Non-blocking: returns immediately with a Future object
  - Perfect for: interactive work, real-time monitoring, streaming
  
- **Cell 10 (Code)**: Submit tasks with futures
  ```python
  def process(x):
      sleep(0.5)
      return x * 2
  
  # Submit immediately - returns Future objects
  futures = [client.submit(process, i) for i in range(4)]
  print(futures)  # Shows pending futures
  
  # Check status
  [f.status for f in futures]
  ```

- **Cell 11 (Code)**: Get results (blocking and non-blocking)
  ```python
  # Blocking: wait for result
  result = futures[0].result()
  
  # Non-blocking: check if done
  futures[0].done()
  
  # Get all results (blocks until all complete)
  results = [f.result() for f in futures]
  ```

- **Cell 12 (Code)**: Real-time monitoring
  ```python
  # Submit and monitor
  future = client.submit(process, 10)
  
  # Do other work while it runs
  print("Future status:", future.status)
  print("Future done:", future.done())
  
  # Get result when ready
  result = future.result()
  ```

### Section 5: Key Differences and When to Use (2-3 cells)
- **Cell 13 (Markdown)**: Comparison table
  - **delayed**: Lazy, graph-based, batch workflows, better for complex dependencies
  - **futures**: Eager, immediate execution, interactive, better for real-time monitoring
  
- **Cell 14 (Code)**: Side-by-side comparison
  ```python
  # Same task with delayed
  @dask.delayed
  def task(x):
      sleep(0.5)
      return x * 2
  
  delayed_work = [task(i) for i in range(4)]
  # Nothing executed yet - just graph built
  
  # Same task with futures
  future_work = [client.submit(task, i) for i in range(4)]
  # Already executing!
  
  # Compare execution
  %time dask.compute(*delayed_work)
  %time [f.result() for f in future_work]
  ```

- **Cell 15 (Markdown)**: Decision guide
  - Use **delayed** when:
    - You have a clear workflow/graph structure
    - You want to optimize the entire computation graph
    - You're processing batches of data
  - Use **futures** when:
    - You need immediate feedback
    - You're doing interactive/exploratory work
    - You want to monitor progress in real-time
    - You're submitting tasks dynamically based on results

### Section 6: Quick Exercise (2 cells)
- **Cell 16 (Markdown)**: Exercise prompt
  - Convert a simple for-loop workflow to use both delayed and futures
  - Compare execution times and code style
  
- **Cell 17 (Code)**: Exercise solution (commented out or in separate cell)
  ```python
  # Exercise: Process a list of numbers
  # 1. Square each number
  # 2. Sum the results
  # Try with both delayed and futures
  ```

### Section 7: Summary (1 cell)
- **Cell 18 (Markdown)**: Key takeaways
  - Delayed: lazy, graph-based, batch processing
  - Futures: eager, immediate, interactive
  - Both powerful for parallelizing arbitrary Python code
  - Choose based on your workflow needs

## Key Concepts to Emphasize

1. **Lazy vs Eager**
   - Delayed builds a graph, executes on `.compute()`
   - Futures execute immediately on `.submit()`

2. **Graph Visualization**
   - Show how delayed creates a visual task graph
   - Futures don't have a single graph (they're independent)

3. **Dependency Handling**
   - Delayed automatically handles dependencies
   - Futures require manual coordination (or use `client.map`)

4. **Use Cases**
   - Delayed: batch processing, complex workflows
   - Futures: interactive work, real-time monitoring

## Dependencies
- `dask[distributed]` - for Client and futures
- Existing dask-tutorial setup (Client, workers)
- No external data files needed (use synthetic examples)

## Testing Criteria
- All cells execute without errors
- Clear progression: delayed → futures → comparison
- Code is minimal and focused
- Execution time stays under 2-3 minutes total
- Visualizations render correctly
- Key differences are clearly demonstrated

## Implementation Notes

- Keep examples simple and self-contained
- Use `sleep()` to simulate work and make parallelism visible
- Show timing differences clearly
- Include at least one visualization (delayed graph)
- Make the comparison section particularly clear
- Aim for ~15-20 total cells (including markdown)

---
**Status**: [✅] Draft | [ ] Approved | [ ] In Progress | [ ] Complete
**Last Updated**: 2024-12-19

