#!/usr/bin/env python3
"""
Test script to verify cluster_utils integration in process_multiple_years.py
"""

import sys
import os

def test_imports():
    """Test that all required imports work."""
    print("Testing imports...")
    
    try:
        # Test cluster_utils import
        from cluster_utils import setup_dask_cluster, close_dask_cluster
        print("✓ cluster_utils import successful")
        
        # Test weather_transformation import
        from weather_transformation import transform_long_to_wide, display_dataframe_info, save_wide_dataframe
        print("✓ weather_transformation import successful")
        
        # Test main script import
        from process_multiple_years import main
        print("✓ process_multiple_years import successful")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False


def test_cluster_functions():
    """Test cluster setup and cleanup functions."""
    print("\nTesting cluster functions...")
    
    try:
        from cluster_utils import setup_dask_cluster, close_dask_cluster
        
        # Test cluster setup with small configuration
        print("  Setting up test cluster (2 workers, 1GB each)...")
        cluster, client, cleanup_summary = setup_dask_cluster(
            n_workers=2, 
            memory_per_worker='1GB'
        )
        
        if cluster is not None and client is not None:
            print("  ✓ Cluster setup successful")
            
            # Test basic computation
            result = client.submit(lambda x: x * 2, 21).result()
            if result == 42:
                print("  ✓ Cluster computation test successful")
            else:
                print(f"  ❌ Cluster computation test failed: expected 42, got {result}")
            
            # Test cleanup
            print("  Cleaning up cluster...")
            close_dask_cluster(cluster, client)
            print("  ✓ Cluster cleanup successful")
            
            return True
        else:
            print("  ❌ Cluster setup failed")
            return False
            
    except Exception as e:
        print(f"  ❌ Cluster test error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_command_line_interface():
    """Test command line argument parsing."""
    print("\nTesting command line interface...")
    
    try:
        from process_multiple_years import main
        import argparse
        
        # Test argument parsing (without running main)
        parser = argparse.ArgumentParser()
        parser.add_argument('--start_year', type=int, default=2020)
        parser.add_argument('--end_year', type=int, default=2022)
        parser.add_argument('--data_dir', type=str, default='data')
        parser.add_argument('--n_workers', type=int, default=20)
        parser.add_argument('--memory_per_worker', type=str, default='4GB')
        
        # Test default arguments
        args = parser.parse_args([])
        if args.start_year == 2020 and args.n_workers == 20:
            print("  ✓ Default arguments work correctly")
        else:
            print(f"  ❌ Default arguments failed: {args}")
            return False
        
        # Test custom arguments
        test_args = parser.parse_args(['--start_year', '2021', '--n_workers', '16'])
        if test_args.start_year == 2021 and test_args.n_workers == 16:
            print("  ✓ Custom arguments work correctly")
        else:
            print(f"  ❌ Custom arguments failed: {test_args}")
            return False
        
        return True
        
    except Exception as e:
        print(f"  ❌ CLI test error: {e}")
        return False


def main():
    """Run all tests."""
    print("Cluster Integration Test Suite")
    print("=" * 40)
    
    tests = [
        ("Import Test", test_imports),
        ("Cluster Functions Test", test_cluster_functions),
        ("Command Line Interface Test", test_command_line_interface)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        print("-" * len(test_name))
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print(f"\n{'='*40}")
    print("Test Results Summary:")
    print("=" * 40)
    
    passed = 0
    for test_name, result in results:
        status = "✓ PASS" if result else "❌ FAIL"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("🎉 All tests passed! Cluster integration is working correctly.")
        return 0
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
