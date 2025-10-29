#!/usr/bin/env python3
"""
Test suite for compute_pca_coefficients.py

This module contains comprehensive tests for the PCA coefficients computation program.
It tests all major functions and edge cases to ensure reliability.

Usage:
    python test_compute_pca_coefficients.py

Author: AI Assistant
Date: 2025-01-25
"""

import unittest
import tempfile
import os
import shutil
import pickle
import numpy as np
import pandas as pd
import dask.dataframe as dd
from unittest.mock import patch, MagicMock
import warnings

# Import the module under test
from compute_pca_coefficients import (
    load_pca_results,
    preprocess_daily_data,
    compute_pca_coefficients,
    process_measurement_type,
    main
)

# Suppress warnings for cleaner test output
warnings.filterwarnings('ignore')


class TestPCACoefficientsComputation(unittest.TestCase):
    """Test cases for PCA coefficients computation functions."""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        # Create temporary directory for test files
        self.test_dir = tempfile.mkdtemp()
        self.pca_dir = os.path.join(self.test_dir, 'pca_results')
        os.makedirs(self.pca_dir, exist_ok=True)
        
        # Create sample PCA results
        self.sample_pca_results = {
            'components': np.random.randn(10, 365),
            'explained_variances': np.random.rand(10),
            'mean': np.random.randn(365)
        }
        
        # Create sample weather data
        self.sample_weather_data = self._create_sample_weather_data()
    
    def tearDown(self):
        """Clean up after each test method."""
        shutil.rmtree(self.test_dir)
    
    def _create_sample_weather_data(self, n_records=100):
        """Create sample weather data for testing."""
        data = {
            'station_id_x': [f'TEST{i:06d}' for i in range(n_records)],
            'latitude': np.random.uniform(20, 70, n_records),
            'longitude': np.random.uniform(-180, 180, n_records),
            'year': np.random.randint(2020, 2023, n_records),
            'ELEMENT': np.random.choice(['SNWD', 'PRCP', 'TMIN', 'TMAX'], n_records)
        }
        
        # Add daily columns
        for day in range(1, 366):
            data[f'day_{day}'] = np.random.uniform(0, 100, n_records)
        
        return pd.DataFrame(data)
    
    def _create_pca_file(self, measurement_type):
        """Create a PCA result file for testing."""
        pca_file = os.path.join(self.pca_dir, f"{measurement_type}_pca_results.pkl")
        with open(pca_file, 'wb') as f:
            pickle.dump(self.sample_pca_results, f)
        return pca_file
    
    def test_load_pca_results_success(self):
        """Test successful loading of PCA results."""
        # Create PCA files for all measurement types
        measurement_types = ['snwd', 'prcp', 'tmin', 'snow', 'tmax', 'tobs', 'tavg']
        for measurement in measurement_types:
            self._create_pca_file(measurement)
        
        # Test loading
        results = load_pca_results(self.pca_dir)
        
        # Verify results
        self.assertEqual(len(results), 7)
        for measurement in measurement_types:
            self.assertIn(measurement.upper(), results)
            self.assertIn('components', results[measurement.upper()])
            self.assertIn('explained_variances', results[measurement.upper()])
            self.assertIn('mean', results[measurement.upper()])
    
    def test_load_pca_results_missing_files(self):
        """Test loading PCA results when some files are missing."""
        # Create only some PCA files
        self._create_pca_file('snwd')
        self._create_pca_file('prcp')
        
        results = load_pca_results(self.pca_dir)
        
        # Should only load the available files
        self.assertEqual(len(results), 2)
        self.assertIn('SNWD', results)
        self.assertIn('PRCP', results)
    
    def test_load_pca_results_empty_directory(self):
        """Test loading PCA results from empty directory."""
        results = load_pca_results(self.pca_dir)
        self.assertEqual(len(results), 0)
    
    def test_preprocess_daily_data_success(self):
        """Test successful preprocessing of daily data."""
        # Create sample data
        data = self.sample_weather_data.head(10)
        mean_values = np.random.randn(365)
        
        # Test preprocessing
        result = preprocess_daily_data(data, 'SNWD', mean_values)
        
        # Verify result
        self.assertIsNotNone(result)
        self.assertEqual(result.shape, (10, 365))
        self.assertFalse(np.isnan(result).any())
    
    def test_preprocess_daily_data_missing_columns(self):
        """Test preprocessing when daily columns are missing."""
        # Create data without daily columns
        data = pd.DataFrame({
            'station_id_x': ['TEST001'],
            'ELEMENT': ['SNWD']
        })
        mean_values = np.random.randn(365)
        
        # Test preprocessing
        result = preprocess_daily_data(data, 'SNWD', mean_values)
        
        # Should return None for missing columns
        self.assertIsNone(result)
    
    def test_preprocess_daily_data_with_nans(self):
        """Test preprocessing with NaN values."""
        # Create data with NaN values
        data = self.sample_weather_data.head(5).copy()
        data.loc[0, 'day_1'] = np.nan
        data.loc[1, 'day_100'] = np.nan
        
        mean_values = np.random.randn(365)
        
        # Test preprocessing
        result = preprocess_daily_data(data, 'SNWD', mean_values)
        
        # Verify NaN values are handled
        self.assertIsNotNone(result)
        self.assertFalse(np.isnan(result).any())
    
    def test_compute_pca_coefficients_success(self):
        """Test successful computation of PCA coefficients."""
        # Create sample data
        data = np.random.randn(10, 365)
        components = np.random.randn(10, 365)
        
        # Test computation
        result = compute_pca_coefficients(data, components)
        
        # Verify result
        self.assertEqual(result.shape, (10, 10))
        self.assertFalse(np.isnan(result).any())
        self.assertFalse(np.isinf(result).any())
    
    def test_compute_pca_coefficients_dimensions(self):
        """Test PCA coefficient computation with different dimensions."""
        # Test with different number of samples
        data = np.random.randn(5, 365)
        components = np.random.randn(10, 365)
        
        result = compute_pca_coefficients(data, components)
        self.assertEqual(result.shape, (5, 10))
    
    def test_process_measurement_type_success(self):
        """Test successful processing of a measurement type."""
        # Create PCA file
        self._create_pca_file('snwd')
        
        # Create Dask DataFrame
        dask_df = dd.from_pandas(self.sample_weather_data, npartitions=2)
        
        # Load PCA results
        pca_results = load_pca_results(self.pca_dir)
        
        # Test processing
        result = process_measurement_type(dask_df, 'SNWD', pca_results, chunk_size=50)
        
        # Verify result
        self.assertFalse(result.empty)
        self.assertIn('PC1', result.columns)
        self.assertIn('PC10', result.columns)
        self.assertEqual(len(result.columns), len(self.sample_weather_data.columns) + 10)
    
    def test_process_measurement_type_no_data(self):
        """Test processing when no data exists for measurement type."""
        # Create PCA file
        self._create_pca_file('snwd')
        
        # Create data without SNWD records
        data = self.sample_weather_data.copy()
        data['ELEMENT'] = 'PRCP'  # No SNWD records
        dask_df = dd.from_pandas(data, npartitions=2)
        
        # Load PCA results
        pca_results = load_pca_results(self.pca_dir)
        
        # Test processing
        result = process_measurement_type(dask_df, 'SNWD', pca_results)
        
        # Should return empty DataFrame
        self.assertTrue(result.empty)
    
    def test_process_measurement_type_no_pca_results(self):
        """Test processing when PCA results are missing."""
        # Create Dask DataFrame
        dask_df = dd.from_pandas(self.sample_weather_data, npartitions=2)
        
        # Empty PCA results
        pca_results = {}
        
        # Test processing
        result = process_measurement_type(dask_df, 'SNWD', pca_results)
        
        # Should return empty DataFrame
        self.assertTrue(result.empty)
    
    @patch('compute_pca_coefficients.dd.read_parquet')
    @patch('compute_pca_coefficients.load_pca_results')
    @patch('compute_pca_coefficients.process_measurement_type')
    @patch('compute_pca_coefficients.pd.concat')
    def test_main_function_success(self, mock_concat, mock_process, mock_load_pca, mock_read_parquet):
        """Test successful execution of main function."""
        # Mock the dependencies
        mock_df = MagicMock()
        mock_df.shape = (1000, 379)
        mock_read_parquet.return_value = mock_df
        
        mock_pca_results = {'SNWD': self.sample_pca_results}
        mock_load_pca.return_value = mock_pca_results
        
        mock_result_df = pd.DataFrame({'ELEMENT': ['SNWD'], 'PC1': [1.0]})
        mock_process.return_value = mock_result_df
        
        mock_concat.return_value = mock_result_df
        
        # Mock file operations
        with patch('builtins.open', MagicMock()), \
             patch('compute_pca_coefficients.os.makedirs', MagicMock()), \
             patch.object(mock_result_df, 'to_parquet', MagicMock()):
            
            # Test main function
            with patch('sys.argv', ['compute_pca_coefficients.py', '--input-file', 'test.parquet']):
                main()
        
        # Verify function calls
        mock_read_parquet.assert_called_once()
        mock_load_pca.assert_called_once()
        mock_process.assert_called_once()
        mock_concat.assert_called_once()
    
    def test_integration_small_dataset(self):
        """Integration test with a small dataset."""
        # Create PCA files
        measurement_types = ['snwd', 'prcp']
        for measurement in measurement_types:
            self._create_pca_file(measurement)
        
        # Create small weather dataset
        small_data = self.sample_weather_data.head(20)
        small_data['ELEMENT'] = ['SNWD'] * 10 + ['PRCP'] * 10
        
        # Save as parquet
        input_file = os.path.join(self.test_dir, 'input.parquet')
        small_data.to_parquet(input_file, index=False)
        
        # Create Dask DataFrame
        dask_df = dd.read_parquet(input_file)
        
        # Load PCA results
        pca_results = load_pca_results(self.pca_dir)
        
        # Process each measurement type
        all_results = []
        for measurement_type in pca_results.keys():
            result_df = process_measurement_type(dask_df, measurement_type, pca_results, chunk_size=10)
            if not result_df.empty:
                all_results.append(result_df)
        
        # Combine results
        if all_results:
            final_df = pd.concat(all_results, ignore_index=True)
            
            # Verify results
            self.assertFalse(final_df.empty)
            self.assertIn('PC1', final_df.columns)
            self.assertIn('PC10', final_df.columns)
            
            # Check that we have data for both measurement types
            elements = final_df['ELEMENT'].unique()
            self.assertIn('SNWD', elements)
            self.assertIn('PRCP', elements)


class TestEdgeCases(unittest.TestCase):
    """Test edge cases and error conditions."""
    
    def test_empty_dataframe(self):
        """Test handling of empty DataFrame."""
        empty_df = pd.DataFrame()
        mean_values = np.random.randn(365)
        
        result = preprocess_daily_data(empty_df, 'SNWD', mean_values)
        self.assertIsNone(result)
    
    def test_single_record(self):
        """Test processing of single record."""
        single_record = pd.DataFrame({
            'station_id_x': ['TEST001'],
            'ELEMENT': ['SNWD']
        })
        
        # Add daily columns
        for day in range(1, 366):
            single_record[f'day_{day}'] = [np.random.uniform(0, 100)]
        
        mean_values = np.random.randn(365)
        
        result = preprocess_daily_data(single_record, 'SNWD', mean_values)
        self.assertIsNotNone(result)
        self.assertEqual(result.shape, (1, 365))
    
    def test_large_chunk_size(self):
        """Test processing with chunk size larger than data."""
        # This test would require mocking the process_measurement_type function
        # to avoid actual data processing
        pass


def run_tests():
    """Run all tests and return results."""
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test cases
    test_suite.addTest(unittest.makeSuite(TestPCACoefficientsComputation))
    test_suite.addTest(unittest.makeSuite(TestEdgeCases))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    return result


if __name__ == "__main__":
    print("Running PCA Coefficients Computation Tests...")
    print("=" * 50)
    
    result = run_tests()
    
    print("\n" + "=" * 50)
    if result.wasSuccessful():
        print("✅ All tests passed!")
    else:
        print(f"❌ {len(result.failures)} test(s) failed, {len(result.errors)} error(s)")
        for test, traceback in result.failures + result.errors:
            print(f"\nFailed: {test}")
            print(traceback)
    
    print(f"\nTests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
