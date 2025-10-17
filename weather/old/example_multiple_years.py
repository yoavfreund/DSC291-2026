#!/usr/bin/env python3
"""
Example usage of the multi-year weather data processor.

This script demonstrates how to use the process_multiple_years.py script
with different configurations.
"""

import subprocess
import sys
import os


def run_example():
    """Run an example with a small year range."""
    print("Weather Data Multi-Year Processor Example")
    print("=" * 45)
    
    # Example 1: Process just 2020
    print("\nExample 1: Processing year 2020 only")
    print("-" * 40)
    
    cmd = [
        sys.executable, 
        "process_multiple_years.py",
        "--start_year", "2020",
        "--end_year", "2020"
    ]
    
    print(f"Running: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        print("STDOUT:")
        print(result.stdout)
        if result.stderr:
            print("STDERR:")
            print(result.stderr)
        print(f"Return code: {result.returncode}")
    except subprocess.TimeoutExpired:
        print("Command timed out after 5 minutes")
    except Exception as e:
        print(f"Error running command: {e}")
    
    # Check what files were created
    print("\nFiles created in 'data' directory:")
    if os.path.exists("data"):
        for file in os.listdir("data"):
            print(f"  - {file}")
    else:
        print("  No 'data' directory found")


def show_usage_examples():
    """Show different usage examples."""
    print("\nUsage Examples:")
    print("=" * 20)
    print()
    
    examples = [
        {
            "description": "Process single year (2020) with default cluster",
            "command": "python process_multiple_years.py --start_year 2020 --end_year 2020"
        },
        {
            "description": "Process multiple years (2020-2022)",
            "command": "python process_multiple_years.py --start_year 2020 --end_year 2022"
        },
        {
            "description": "Process with custom cluster (16 workers, 8GB each)",
            "command": "python process_multiple_years.py --start_year 2020 --end_year 2021 --n_workers 16 --memory_per_worker 8GB"
        },
        {
            "description": "Process with custom data directory",
            "command": "python process_multiple_years.py --start_year 2020 --end_year 2021 --data_dir my_data"
        },
        {
            "description": "Process longer range (2020-2025) with smaller cluster",
            "command": "python process_multiple_years.py --start_year 2020 --end_year 2025 --n_workers 10 --memory_per_worker 2GB"
        }
    ]
    
    for i, example in enumerate(examples, 1):
        print(f"{i}. {example['description']}")
        print(f"   {example['command']}")
        print()


if __name__ == "__main__":
    show_usage_examples()
    
    # Ask user if they want to run the example
    response = input("Do you want to run the example (process year 2020)? (y/n): ")
    if response.lower() in ['y', 'yes']:
        run_example()
    else:
        print("Example skipped. You can run the script manually using the commands above.")
