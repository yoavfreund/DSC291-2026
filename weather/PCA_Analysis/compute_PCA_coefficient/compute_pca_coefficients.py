#!/usr/bin/env python3
"""
PCA Coefficients Computation Program

This program computes PCA coefficients for each row in the weather data,
using pre-computed PCA components for each measurement type.

Usage:
    python compute_pca_coefficients.py [--input-file PATH] [--output-file PATH] [--chunk-size N]

Author: AI Assistant
Date: 2025-01-25
"""

import argparse
import os
import pickle
import logging
from typing import Dict, Tuple, List
import numpy as np
import pandas as pd
import dask.dataframe as dd
from tqdm import tqdm
import warnings

# Suppress warnings for cleaner output
warnings.filterwarnings('ignore')

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('pca_coefficients.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def load_pca_results(pca_dir: str = "../weather_info/pca_results/") -> Dict[str, Dict]:
    """
    Load all PCA results from pickle files.
    
    Args:
        pca_dir: Directory containing PCA result files
        
    Returns:
        Dictionary mapping measurement types to PCA results
    """
    logger.info("Loading PCA results...")
    
    measurement_types = ['snwd', 'prcp', 'tmin', 'snow', 'tmax', 'tobs', 'tavg']
    pca_results = {}
    
    for measurement in measurement_types:
        pca_file = os.path.join(pca_dir, f"{measurement}_pca_results.pkl")
        
        if not os.path.exists(pca_file):
            logger.warning(f"PCA file not found: {pca_file}")
            continue
            
        try:
            with open(pca_file, 'rb') as f:
                results = pickle.load(f)
                pca_results[measurement.upper()] = results
                logger.info(f"Loaded PCA results for {measurement.upper()}: "
                           f"components {results['components'].shape}, "
                           f"variances {results['explained_variances'].shape}")
        except Exception as e:
            logger.error(f"Error loading {pca_file}: {e}")
            continue
    
    logger.info(f"Successfully loaded PCA results for {len(pca_results)} measurement types")
    return pca_results


def preprocess_daily_data(data: pd.DataFrame, measurement_type: str, 
                         mean_values: np.ndarray) -> np.ndarray:
    """
    Preprocess daily data for PCA coefficient computation.
    
    Args:
        data: DataFrame with daily columns (day_1 to day_365)
        measurement_type: Type of measurement (e.g., 'SNWD')
        mean_values: Pre-computed mean values for this measurement type
        
    Returns:
        Preprocessed data array (n_samples, 365)
    """
    # Extract daily columns
    daily_cols = [f'day_{i}' for i in range(1, 366)]
    
    if not all(col in data.columns for col in daily_cols):
        logger.error(f"Missing daily columns for {measurement_type}")
        return None
    
    # Get daily data
    daily_data = data[daily_cols].values
    
    # Handle missing values (replace NaN with 0, which is common for weather data)
    daily_data = np.nan_to_num(daily_data, nan=0.0)
    
    # Normalize by subtracting mean
    normalized_data = daily_data - mean_values
    
    return normalized_data


def compute_pca_coefficients(data: np.ndarray, components: np.ndarray) -> np.ndarray:
    """
    Compute PCA coefficients by projecting data onto principal components.
    
    Args:
        data: Normalized data array (n_samples, 365)
        components: PCA components (10, 365)
        
    Returns:
        PCA coefficients (n_samples, 10)
    """
    # Project data onto principal components
    # Formula: coefficients = data @ components.T
    coefficients = data @ components.T
    
    return coefficients


def process_measurement_type(df: dd.DataFrame, measurement_type: str, 
                           pca_results: Dict, chunk_size: int = 10000) -> pd.DataFrame:
    """
    Process one measurement type and compute PCA coefficients.
    
    Args:
        df: Dask DataFrame with weather data
        measurement_type: Type of measurement (e.g., 'SNWD')
        pca_results: Dictionary containing PCA results
        chunk_size: Size of chunks for processing
        
    Returns:
        DataFrame with original metadata + PCA coefficients
    """
    logger.info(f"Processing {measurement_type}...")
    
    if measurement_type not in pca_results:
        logger.warning(f"No PCA results found for {measurement_type}")
        return pd.DataFrame()
    
    # Filter data for this measurement type
    measurement_data = df[df['ELEMENT'] == measurement_type]
    
    if len(measurement_data) == 0:
        logger.warning(f"No data found for {measurement_type}")
        return pd.DataFrame()
    
    # Get PCA components and mean
    components = pca_results[measurement_type]['components']  # (10, 365)
    mean_values = pca_results[measurement_type]['mean']  # (365,)
    
    logger.info(f"Processing {len(measurement_data)} records for {measurement_type}")
    
    # Process in chunks to manage memory
    results = []
    
    # Compute the data to work with pandas
    measurement_data = measurement_data.compute()
    
    # Process in chunks
    for i in tqdm(range(0, len(measurement_data), chunk_size), 
                  desc=f"Processing {measurement_type}"):
        chunk = measurement_data.iloc[i:i+chunk_size]
        
        # Preprocess daily data
        daily_data = preprocess_daily_data(chunk, measurement_type, mean_values)
        
        if daily_data is None:
            continue
        
        # Compute PCA coefficients
        coefficients = compute_pca_coefficients(daily_data, components)
        
        # Create result DataFrame
        result_chunk = chunk.copy()
        
        # Add PCA coefficient columns
        for j in range(10):
            result_chunk[f'PC{j+1}'] = coefficients[:, j]
        
        results.append(result_chunk)
    
    if not results:
        logger.warning(f"No results generated for {measurement_type}")
        return pd.DataFrame()
    
    # Combine all chunks
    result_df = pd.concat(results, ignore_index=True)
    
    logger.info(f"Generated {len(result_df)} records with PCA coefficients for {measurement_type}")
    return result_df


def main():
    """Main function to orchestrate PCA coefficient computation."""
    parser = argparse.ArgumentParser(description='Compute PCA coefficients for weather data')
    parser.add_argument('--input-file', '-i', 
                       default='../../../weather_data/stations_weather_with_dist2coast.parquet',
                       help='Input parquet file path')
    parser.add_argument('--output-file', '-o',
                       default='../../../weather_data/pca_coefficients.parquet',
                       help='Output parquet file path')
    parser.add_argument('--chunk-size', '-c', type=int, default=10000,
                       help='Chunk size for processing')
    parser.add_argument('--pca-dir', '-p',
                       default='../weather_info/pca_results/',
                       help='Directory containing PCA result files')
    
    args = parser.parse_args()
    
    logger.info("Starting PCA coefficients computation...")
    logger.info(f"Input file: {args.input_file}")
    logger.info(f"Output file: {args.output_file}")
    logger.info(f"Chunk size: {args.chunk_size}")
    
    try:
        # Step 1: Load weather data
        logger.info("Loading weather data...")
        df = dd.read_parquet(args.input_file)
        logger.info(f"Loaded weather data: {df.shape}")
        
        # Step 2: Load PCA results
        pca_results = load_pca_results(args.pca_dir)
        
        if not pca_results:
            logger.error("No PCA results loaded. Exiting.")
            return
        
        # Step 3: Process each measurement type
        all_results = []
        
        for measurement_type in pca_results.keys():
            result_df = process_measurement_type(df, measurement_type, pca_results, args.chunk_size)
            
            if not result_df.empty:
                all_results.append(result_df)
        
        if not all_results:
            logger.error("No results generated. Exiting.")
            return
        
        # Step 4: Combine all results
        logger.info("Combining all results...")
        final_df = pd.concat(all_results, ignore_index=True)
        
        # Step 5: Save results
        logger.info(f"Saving results to {args.output_file}...")
        
        # Ensure output directory exists
        output_dir = os.path.dirname(args.output_file)
        if output_dir:  # Only create directory if path is not empty
            os.makedirs(output_dir, exist_ok=True)
        
        # Save as parquet
        final_df.to_parquet(args.output_file, index=False)
        
        logger.info(f"Successfully saved {len(final_df)} records to {args.output_file}")
        logger.info(f"Output columns: {list(final_df.columns)}")
        
        # Print summary statistics
        logger.info("\nSummary Statistics:")
        for measurement_type in pca_results.keys():
            count = len(final_df[final_df['ELEMENT'] == measurement_type])
            logger.info(f"  {measurement_type}: {count} records")
        
        logger.info("PCA coefficients computation completed successfully!")
        
    except Exception as e:
        logger.error(f"Error during computation: {e}")
        raise


if __name__ == "__main__":
    main()
