"""
Dask Cluster Management Utilities

This module provides functions to clean up existing Dask clusters
and create new ones with proper configuration.
"""

import subprocess
import os
import time
import gc
from dask.distributed import Client, LocalCluster


def cleanup_existing_clusters():
    """
    Clean up any existing Dask clusters using multiple methods:
    1. Close current client connections
    2. Close orphaned LocalCluster instances in memory
    3. Force kill processes on common Dask ports
    
    Returns:
        dict: Summary of cleanup actions performed
    """
    cleanup_summary = {
        'clients_closed': 0,
        'clusters_closed': 0,
        'processes_killed': 0
    }
    
    print("Checking for existing Dask clusters...")
    
    # Method 1: Close current client
    try:
        existing_client = Client.current()
        if existing_client:
            print(f"Found existing cluster with {len(existing_client.ncores())} workers")
            print("Closing existing cluster...")
            existing_client.close()
            cleanup_summary['clients_closed'] = 1
            print("✓ Existing cluster closed")
    except Exception:
        print("No current client found")

    # Method 2: Close any LocalCluster instances in memory
    try:
        closed_clusters = 0
        for obj in gc.get_objects():
            if isinstance(obj, LocalCluster):
                print(f"Found orphaned LocalCluster, closing...")
                obj.close()
                closed_clusters += 1
        cleanup_summary['clusters_closed'] = closed_clusters
        if closed_clusters > 0:
            print(f"✓ Closed {closed_clusters} orphaned clusters")
    except Exception:
        pass

    # Method 3: Force close any processes on Dask ports
    def kill_process_on_port(port):
        """Kill processes running on a specific port"""
        try:
            result = subprocess.run(['lsof', '-ti', f':{port}'], 
                                  capture_output=True, text=True)
            if result.stdout.strip():
                pids = result.stdout.strip().split('\n')
                for pid in pids:
                    if pid:
                        os.kill(int(pid), 9)  # SIGKILL
                        print(f"✓ Killed process {pid} on port {port}")
                        cleanup_summary['processes_killed'] += 1
        except Exception:
            pass

    # Kill processes on common Dask ports
    for port in [8787, 8788, 8789, 8790, 8791]:
        kill_process_on_port(port)

    # Wait a moment for cleanup
    time.sleep(2)
    
    print("All existing clusters closed.")
    return cleanup_summary


def create_dask_cluster(n_workers=20, memory_per_worker='4GB', 
                       dashboard_port=8790, worker_port=8791):
    """
    Create a new Dask cluster with specified configuration.
    
    Args:
        n_workers (int): Number of worker processes
        memory_per_worker (str): Memory limit per worker (e.g., '4GB')
        dashboard_port (int): Port for the main dashboard
        worker_port (int): Port for worker dashboard
        
    Returns:
        tuple: (cluster, client) objects
    """
    print(f"Setting up new cluster with {n_workers} workers...")
    
    cluster = LocalCluster(
        n_workers=n_workers,
        threads_per_worker=1,   # 1 thread per worker (1 CPU per worker)
        memory_limit=memory_per_worker,
        processes=True,         # Use separate processes for workers
        dashboard_address=f':{dashboard_port}',
        silence_logs=False,     # Show worker logs
        worker_dashboard_address=f':{worker_port}'
    )

    # Connect client to cluster
    client = Client(cluster)
    print(f"✓ Dask cluster created with {len(cluster.workers)} workers")
    print(f"✓ Dashboard available at: {client.dashboard_link}")
    print(f"✓ Total workers: {len(client.ncores())}")
    print(f"✓ Cores per worker: {client.ncores()}")
    # Extract numeric value from memory_per_worker string (e.g., '4GB' -> 4)
    memory_gb = int(memory_per_worker.replace('GB', '').replace('MB', ''))
    if 'MB' in memory_per_worker:
        memory_gb = memory_gb / 1024
    print(f"✓ Total memory available: {len(client.ncores()) * memory_gb:.1f} GB")

    # Verify cluster is working
    import dask.array as da
    test_array = da.random.random((100, 100), chunks=(10, 10))
    test_result = test_array.sum().compute()
    print(f"✓ Cluster test computation successful: {test_result:.2f}")

    return cluster, client


def setup_dask_cluster(n_workers=20, memory_per_worker='4GB', 
                      dashboard_port=8790, worker_port=8791):
    """
    Complete setup: cleanup existing clusters and create new one.
    
    Args:
        n_workers (int): Number of worker processes
        memory_per_worker (str): Memory limit per worker
        dashboard_port (int): Port for main dashboard
        worker_port (int): Port for worker dashboard
        
    Returns:
        tuple: (cluster, client) objects
    """
    # Cleanup first
    cleanup_summary = cleanup_existing_clusters()
    
    # Create new cluster
    cluster, client = create_dask_cluster(
        n_workers=n_workers,
        memory_per_worker=memory_per_worker,
        dashboard_port=dashboard_port,
        worker_port=worker_port
    )
    
    return cluster, client, cleanup_summary


def close_dask_cluster(cluster, client):
    """
    Properly close a Dask cluster and client.
    
    Args:
        cluster: LocalCluster object
        client: Client object
    """
    print("Closing Dask cluster...")
    client.close()
    cluster.close()
    print("✓ Cluster closed successfully")
