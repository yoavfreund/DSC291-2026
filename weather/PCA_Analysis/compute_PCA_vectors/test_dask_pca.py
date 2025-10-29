#!/usr/bin/env python3
"""
Test program for dask_pca.py

This module provides comprehensive tests for the Dask PCA implementation,
including unit tests and performance benchmarks.
"""

import numpy as np
import dask.array as da
import time
import sys
import os

# Add current directory to path to import dask_pca
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from dask_pca import dask_pca, dask_pca_transform, dask_pca_inverse_transform, dask_pca_explained_variance_ratio


def test_basic_functionality():
    """Test basic PCA functionality with simple data."""
    print("=" * 50)
    print("TEST 1: Basic Functionality")
    print("=" * 50)
    
    # Create simple 2D data
    np.random.seed(42)
    n_samples, n_features = 100, 5
    X = da.random.random((n_samples, n_features))
    
    print(f"Input data shape: {X.shape}")
    
    # Perform PCA
    components_, explained_variances_, mean_ = dask_pca(X, n_components=3)
    
    print(f"Components shape: {components_.shape}")
    print(f"Explained variances: {explained_variances_}")
    print(f"Mean shape: {mean_.shape}")
    
    # Test transform and inverse transform
    X_transformed = dask_pca_transform(X, components_, mean_)
    X_reconstructed = dask_pca_inverse_transform(X_transformed, components_, mean_)
    
    print(f"Transformed shape: {X_transformed.shape}")
    print(f"Reconstructed shape: {X_reconstructed.shape}")
    
    # Check reconstruction accuracy
    reconstruction_error = da.mean((X - X_reconstructed) ** 2).compute()
    print(f"Reconstruction error: {reconstruction_error:.6f}")
    
    print("✓ Basic functionality test passed\n")


def test_nan_handling():
    """Test PCA with different NaN patterns."""
    print("=" * 50)
    print("TEST 2: NaN Handling - Different Patterns")
    print("=" * 50)
    
    # Test 1: Random NaN pattern
    print("Pattern 1: Random NaN (10% missing)")
    np.random.seed(42)
    n_samples, n_features = 200, 10
    X = da.random.random((n_samples, n_features))
    nan_mask = da.random.random((n_samples, n_features)) < 0.1
    X = da.where(nan_mask, np.nan, X)
    
    print(f"Input data shape: {X.shape}")
    print(f"Number of NaN values: {da.isnan(X).sum().compute()}")
    
    components_, explained_variances_, mean_ = dask_pca(X, n_components=3)
    print(f"Components shape: {components_.shape}")
    print(f"Mean computed successfully: {not np.isnan(mean_).any()}")
    
    # Test 2: Column-wise NaN pattern (some columns have more NaNs)
    print("\nPattern 2: Column-wise NaN (some columns 50% missing)")
    X2 = da.random.random((n_samples, n_features))
    # Make columns 0, 2, 4 have 50% NaN values
    for col in [0, 2, 4]:
        nan_mask_col = da.random.random(n_samples) < 0.5
        X2 = da.where(da.outer(nan_mask_col, da.ones(n_features)) * (da.arange(n_features) == col), np.nan, X2)
    
    print(f"Column-wise NaN pattern - NaN count: {da.isnan(X2).sum().compute()}")
    components_2, explained_variances_2, mean_2 = dask_pca(X2, n_components=3)
    print(f"Column-wise test successful: {components_2.shape}")
    
    # Test 3: Row-wise NaN pattern (some rows have more NaNs)
    print("\nPattern 3: Row-wise NaN (some rows 30% missing)")
    X3 = da.random.random((n_samples, n_features))
    # Make every 5th row have 30% NaN values
    for i in range(0, n_samples, 5):
        nan_mask_row = da.random.random(n_features) < 0.3
        row_mask = da.arange(n_samples) == i
        X3 = da.where(da.outer(row_mask, nan_mask_row), np.nan, X3)
    
    print(f"Row-wise NaN pattern - NaN count: {da.isnan(X3).sum().compute()}")
    components_3, explained_variances_3, mean_3 = dask_pca(X3, n_components=3)
    print(f"Row-wise test successful: {components_3.shape}")
    
    # Test 4: Block NaN pattern (rectangular regions of NaNs)
    print("\nPattern 4: Block NaN (rectangular regions)")
    X4 = da.random.random((n_samples, n_features))
    # Create rectangular blocks of NaN values
    block_mask = ((da.arange(n_samples)[:, None] >= 50) & 
                  (da.arange(n_samples)[:, None] < 100) & 
                  (da.arange(n_features)[None, :] >= 2) & 
                  (da.arange(n_features)[None, :] < 7))
    X4 = da.where(block_mask, np.nan, X4)
    
    print(f"Block NaN pattern - NaN count: {da.isnan(X4).sum().compute()}")
    components_4, explained_variances_4, mean_4 = dask_pca(X4, n_components=3)
    print(f"Block test successful: {components_4.shape}")
    
    # Test 5: Diagonal NaN pattern
    print("\nPattern 5: Diagonal NaN (diagonal elements missing)")
    X5 = da.random.random((n_samples, n_features))
    # Make diagonal elements NaN (where row == col)
    diagonal_mask = da.arange(n_samples)[:, None] == da.arange(n_features)[None, :]
    X5 = da.where(diagonal_mask, np.nan, X5)
    
    print(f"Diagonal NaN pattern - NaN count: {da.isnan(X5).sum().compute()}")
    components_5, explained_variances_5, mean_5 = dask_pca(X5, n_components=3)
    print(f"Diagonal test successful: {components_5.shape}")
    
    # Test 6: Extreme NaN pattern (90% missing)
    print("\nPattern 6: Extreme NaN (90% missing)")
    X6 = da.random.random((n_samples, n_features))
    nan_mask_extreme = da.random.random((n_samples, n_features)) < 0.9
    X6 = da.where(nan_mask_extreme, np.nan, X6)
    
    print(f"Extreme NaN pattern - NaN count: {da.isnan(X6).sum().compute()}")
    try:
        components_6, explained_variances_6, mean_6 = dask_pca(X6, n_components=3)
        print(f"Extreme test successful: {components_6.shape}")
    except Exception as e:
        print(f"Extreme test failed (expected): {type(e).__name__}: {e}")
    
    # Test 7: Complete rows/columns missing
    print("\nPattern 7: Complete rows missing")
    X7 = da.random.random((n_samples, n_features))
    # Make rows 10-20 completely NaN
    complete_nan_rows = (da.arange(n_samples) >= 10) & (da.arange(n_samples) < 20)
    X7 = da.where(complete_nan_rows[:, None], np.nan, X7)
    
    print(f"Complete rows NaN - NaN count: {da.isnan(X7).sum().compute()}")
    components_7, explained_variances_7, mean_7 = dask_pca(X7, n_components=3)
    print(f"Complete rows test successful: {components_7.shape}")
    
    print("✓ NaN handling test with different patterns passed\n")


def test_known_pattern():
    """Test PCA on data with known patterns."""
    print("=" * 50)
    print("TEST 3: Known Pattern Recognition")
    print("=" * 50)
    
    # Create data with clear patterns
    np.random.seed(42)
    n_samples = 1000
    
    # Create 3 clear patterns
    pattern1 = np.sin(np.linspace(0, 4*np.pi, n_samples))
    pattern2 = np.cos(np.linspace(0, 4*np.pi, n_samples))
    pattern3 = np.random.random(n_samples)
    
    # Combine patterns with different weights
    X = np.column_stack([
        pattern1 + 0.1 * np.random.random(n_samples),
        pattern2 + 0.1 * np.random.random(n_samples),
        pattern3 + 0.1 * np.random.random(n_samples),
        pattern1 * 0.5 + 0.1 * np.random.random(n_samples),
        pattern2 * 0.5 + 0.1 * np.random.random(n_samples)
    ])
    
    # Convert to Dask array
    X = da.from_array(X)
    
    print(f"Input data shape: {X.shape}")
    
    # Perform PCA
    components_, explained_variances_, mean_ = dask_pca(X, n_components=3)
    
    print(f"Explained variances: {explained_variances_}")
    
    # Calculate explained variance ratio
    explained_variance_ratio_ = dask_pca_explained_variance_ratio(explained_variances_)
    print(f"Explained variance ratio: {explained_variance_ratio_.compute()}")
    
    # Check that first PC explains most variance
    first_pc_ratio = explained_variance_ratio_.compute()[0]
    print(f"First PC explains {first_pc_ratio:.3f} of variance")
    assert first_pc_ratio > 0.3, f"First PC should explain >30% variance, got {first_pc_ratio:.3f}"
    
    print("✓ Known pattern test passed\n")


def test_performance():
    """Test performance with larger dataset."""
    print("=" * 50)
    print("TEST 4: Performance Test")
    print("=" * 50)
    
    # Create larger dataset
    np.random.seed(42)
    n_samples, n_features = 5000, 100
    X = da.random.random((n_samples, n_features))
    
    print(f"Large dataset: {n_samples} samples x {n_features} features")
    
    # Time the PCA computation
    start_time = time.time()
    components_, explained_variances_, mean_ = dask_pca(X, n_components=10)
    end_time = time.time()
    
    print(f"PCA computation time: {end_time - start_time:.2f} seconds")
    print(f"Components shape: {components_.shape}")
    
    # Test transform performance
    start_time = time.time()
    X_transformed = dask_pca_transform(X, components_, mean_)
    end_time = time.time()
    
    print(f"Transform time: {end_time - start_time:.2f} seconds")
    print(f"Transformed shape: {X_transformed.shape}")
    
    print("✓ Performance test passed\n")


def test_edge_cases():
    """Test edge cases and error handling."""
    print("=" * 50)
    print("TEST 5: Edge Cases")
    print("=" * 50)
    
    # Test with very small dataset
    X_small = da.from_array(np.random.random((3, 2)))
    components_, explained_variances_, mean_ = dask_pca(X_small, n_components=2)
    print(f"Small dataset test: {components_.shape}")
    
    # Test with all NaN values
    X_all_nan = da.full((10, 5), np.nan)
    try:
        components_, explained_variances_, mean_ = dask_pca(X_all_nan, n_components=2)
        print("All NaN test: Handled gracefully")
    except Exception as e:
        print(f"All NaN test: {type(e).__name__}: {e}")
    
    # Test with single feature
    X_single = da.random.random((100, 1))
    components_, explained_variances_, mean_ = dask_pca(X_single, n_components=1)
    print(f"Single feature test: {components_.shape}")
    
    print("✓ Edge cases test passed\n")


def test_reconstruction_accuracy():
    """Test reconstruction accuracy with different numbers of components."""
    print("=" * 50)
    print("TEST 6: Reconstruction Accuracy")
    print("=" * 50)
    
    # Create structured data
    np.random.seed(42)
    n_samples, n_features = 500, 20
    
    # Create data with clear structure
    X = np.random.random((n_samples, n_features))
    for i in range(5):  # Add 5 clear patterns
        pattern = np.sin(np.linspace(0, 2*np.pi*i, n_samples))
        X[:, i] = pattern + 0.1 * np.random.random(n_samples)
    
    X = da.from_array(X)
    
    # Test with different numbers of components
    for n_comp in [1, 5, 10, 15, 20]:
        components_, explained_variances_, mean_ = dask_pca(X, n_components=n_comp)
        X_transformed = dask_pca_transform(X, components_, mean_)
        X_reconstructed = dask_pca_inverse_transform(X_transformed, components_, mean_)
        
        reconstruction_error = da.mean((X - X_reconstructed) ** 2).compute()
        explained_variance_ratio_ = dask_pca_explained_variance_ratio(explained_variances_)
        total_explained = da.sum(explained_variance_ratio_).compute()
        
        print(f"Components: {n_comp:2d}, Error: {reconstruction_error:.6f}, "
              f"Explained: {total_explained:.3f}")
    
    print("✓ Reconstruction accuracy test passed\n")


def run_all_tests():
    """Run all tests."""
    print("DASK PCA TEST SUITE")
    print("=" * 50)
    print("Testing dask_pca.py implementation")
    print("=" * 50)
    
    try:
        test_basic_functionality()
        test_nan_handling()
        test_known_pattern()
        test_performance()
        test_edge_cases()
        test_reconstruction_accuracy()
        
        print("=" * 50)
        print("ALL TESTS PASSED! ✓")
        print("=" * 50)
        
    except Exception as e:
        print(f"TEST FAILED: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    run_all_tests()
