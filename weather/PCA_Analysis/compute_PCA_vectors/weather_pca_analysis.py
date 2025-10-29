#!/usr/bin/env python3
"""
Weather Data PCA Analysis Script

This script reads weather parquet data, computes mean and PCA for each measurement type,
and stores the results in pickle files.

Usage:
    python weather_pca_analysis.py [options]

Example:
    python weather_pca_analysis.py --input ../../weather_data/joined_stations_weather.parquet --output results/ --n_components 10
"""

import argparse
import os
import sys
import pickle
import logging
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import warnings

import dask.dataframe as dd
import dask.array as da
import numpy as np
import pandas as pd
from tqdm import tqdm

# Set up logging first
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Import our custom dask_pca module
sys.path.append(os.path.join(os.path.dirname(__file__), '../Basic_Analysis'))
try:
    from dask_pca import dask_pca
except ImportError as e:
    logger.error(f"Failed to import dask_pca module: {e}")
    logger.error("Please ensure all dependencies are installed (dask, numpy, matplotlib)")
    sys.exit(1)


def setup_argument_parser() -> argparse.ArgumentParser:
    """Set up command line argument parser."""
    parser = argparse.ArgumentParser(
        description="Compute mean and PCA for weather measurements",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python weather_pca_analysis.py
  python weather_pca_analysis.py --input data/weather.parquet --output results/
  python weather_pca_analysis.py --n_components 5 --hemisphere northern
        """
    )
    
    parser.add_argument(
        '--input', '-i',
        type=str,
        default='../../../weather_data/joined_stations_weather.parquet',
        help='Input parquet file path (default: ../../../weather_data/joined_stations_weather.parquet)'
    )
    
    parser.add_argument(
        '--output', '-o',
        type=str,
        default='pca_results',
        help='Output directory for pickle files (default: pca_results)'
    )
    
    parser.add_argument(
        '--n_components', '-n',
        type=int,
        default=10,
        help='Number of principal components to compute (default: 10)'
    )
    
    parser.add_argument(
        '--hemisphere', '-hem',
        type=str,
        choices=['northern', 'southern', 'both'],
        default='both',
        help='Hemisphere to analyze (default: both)'
    )
    
    parser.add_argument(
        '--measurements', '-m',
        type=str,
        nargs='+',
        default=None,
        help='Specific measurements to analyze (e.g., TAVG SNWD). If not specified, analyzes all available.'
    )
    
    parser.add_argument(
        '--min_stations',
        type=int,
        default=100,
        help='Minimum number of stations required for analysis (default: 100)'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose output'
    )
    
    return parser


def load_weather_data(file_path: str) -> dd.DataFrame:
    """Load weather data from parquet file with error handling."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Input file not found: {file_path}")
    
    logger.info(f"Loading weather data from: {file_path}")
    try:
        df = dd.read_parquet(file_path)
        logger.info(f"Successfully loaded data with shape: {df.shape}")
        logger.debug(f"DataFrame type: {type(df)}")
        return df
    except Exception as e:
        logger.error(f"Error loading parquet file: {e}")
        raise


def safe_compute(df):
    """Safely compute a dask DataFrame/Series, return as-is if already computed."""
    logger.debug(f"safe_compute input type: {type(df)}")
    try:
        if hasattr(df, 'compute') and callable(getattr(df, 'compute')):
            logger.debug("Calling .compute() on dask object")
            return df.compute()
        logger.debug("Object already computed, returning as-is")
        return df
    except Exception as e:
        logger.error(f"Error in safe_compute: {e}")
        logger.error(f"Input type: {type(df)}")
        raise


def get_available_measurements(df: dd.DataFrame, requested_measurements: Optional[List[str]] = None) -> List[str]:
    """Get list of available measurement types."""
    if 'ELEMENT' not in df.columns:
        raise ValueError("ELEMENT column not found in data")
    
    # Get unique elements
    elements = safe_compute(df['ELEMENT'].unique())
    available_elements = sorted([elem for elem in elements if pd.notna(elem)])
    
    logger.info(f"Available measurements: {available_elements}")
    
    if requested_measurements:
        # Filter to only requested measurements that are available
        valid_measurements = [m for m in requested_measurements if m in available_elements]
        missing_measurements = [m for m in requested_measurements if m not in available_elements]
        
        if missing_measurements:
            logger.warning(f"Requested measurements not found: {missing_measurements}")
        
        if not valid_measurements:
            raise ValueError("None of the requested measurements are available")
        
        return valid_measurements
    
    return available_elements


def filter_by_hemisphere(df: dd.DataFrame, hemisphere: str) -> dd.DataFrame:
    """Filter data by hemisphere based on latitude."""
    if hemisphere == 'both':
        return df
    
    if 'latitude' not in df.columns:
        logger.warning("Latitude column not found, cannot filter by hemisphere")
        return df
    
    if hemisphere == 'northern':
        filtered_df = df[df['latitude'] >= 0]
    elif hemisphere == 'southern':
        filtered_df = df[df['latitude'] < 0]
    else:
        return df
    
    logger.info(f"Filtered to {hemisphere} hemisphere")
    return filtered_df


def extract_daily_columns(df: dd.DataFrame) -> List[str]:
    """Extract daily column names (day_1 through day_365/366)."""
    all_columns = df.columns.tolist()
    daily_columns = [col for col in all_columns if col.startswith('day_')]
    daily_columns.sort(key=lambda x: int(x.split('_')[1]))
    return daily_columns


def process_measurement_data(df: dd.DataFrame, measurement: str, min_stations: int = 100) -> Optional[np.ndarray]:
    """Process data for a specific measurement type."""
    logger.info(f"Processing measurement: {measurement}")
    
    # Filter for specific measurement
    try:
        filtered_df = df[df['ELEMENT'] == measurement]
        logger.debug(f"Filtered dataframe type: {type(filtered_df)}")
        measurement_df = safe_compute(filtered_df)
    except Exception as e:
        logger.error(f"Error filtering data for {measurement}: {e}")
        return None
    
    if len(measurement_df) == 0:
        logger.warning(f"No data found for measurement: {measurement}")
        return None
    
    # Check minimum stations requirement
    unique_stations = measurement_df['ID'].nunique()
    if unique_stations < min_stations:
        logger.warning(f"Only {unique_stations} stations for {measurement}, skipping (min: {min_stations})")
        return None
    
    logger.info(f"Found {len(measurement_df)} records for {measurement} across {unique_stations} stations")
    
    # Extract daily columns
    daily_columns = extract_daily_columns(measurement_df)
    if not daily_columns:
        logger.warning(f"No daily columns found for {measurement}")
        return None
    
    # Convert to numpy array, handling missing values
    try:
        data_array = measurement_df[daily_columns].values
        
        # Replace any remaining NaN values with 0 (or could use interpolation)
        data_array = np.nan_to_num(data_array, nan=0.0)
    except Exception as e:
        logger.error(f"Error creating data array for {measurement}: {e}")
        return None
    
    logger.info(f"Data array shape: {data_array.shape}")
    return data_array


def compute_pca_analysis(data: np.ndarray, measurement: str, n_components: int) -> Dict:
    """Compute PCA analysis for the data."""
    logger.info(f"Computing PCA for {measurement} with {n_components} components")
    
    # Convert to dask array for processing
    dask_data = da.from_array(data, chunks='auto')
    
    # Compute PCA
    components, explained_variances, mean = dask_pca(dask_data, n_components=n_components)
    
    # Debug: Check what dask_pca returned
    logger.debug(f"dask_pca returned - components: {type(components)}, explained_variances: {type(explained_variances)}, mean: {type(mean)}")
    
    # Compute results (handle both dask arrays and numpy arrays)
    components_computed = safe_compute(components)
    explained_variances_computed = safe_compute(explained_variances)
    mean_computed = safe_compute(mean)
    
    # Calculate explained variance ratios
    total_variance = np.sum(explained_variances_computed)
    explained_variance_ratios = explained_variances_computed / total_variance
    
    results = {
        'measurement': measurement,
        'mean': mean_computed,
        'components': components_computed,
        'explained_variances': explained_variances_computed,
        'explained_variance_ratios': explained_variance_ratios,
        'n_components': n_components,
        'data_shape': data.shape
    }
    
    logger.info(f"PCA completed for {measurement}")
    logger.info(f"Explained variance by top {n_components} components: {np.sum(explained_variance_ratios):.3f}")
    
    return results


def save_results(results: Dict, output_dir: str, measurement: str):
    """Save PCA results to pickle file."""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    filename = f"{measurement.lower()}_pca_results.pkl"
    filepath = output_path / filename
    
    with open(filepath, 'wb') as f:
        pickle.dump(results, f)
    
    logger.info(f"Saved results to: {filepath}")


def generate_summary_report(all_results: List[Dict], output_dir: str):
    """Generate a summary report of all analyses."""
    output_path = Path(output_dir)
    report_path = output_path / "analysis_summary.txt"
    
    with open(report_path, 'w') as f:
        f.write("Weather Data PCA Analysis Summary\n")
        f.write("=" * 40 + "\n\n")
        
        for results in all_results:
            measurement = results['measurement']
            f.write(f"Measurement: {measurement}\n")
            f.write(f"  Data shape: {results['data_shape']}\n")
            f.write(f"  Components computed: {results['n_components']}\n")
            f.write(f"  Total explained variance: {np.sum(results['explained_variance_ratios']):.3f}\n")
            f.write(f"  Top 3 components explain: {np.sum(results['explained_variance_ratios'][:3]):.3f}\n")
            f.write("\n")
    
    logger.info(f"Summary report saved to: {report_path}")


def main():
    """Main function to orchestrate the analysis."""
    parser = setup_argument_parser()
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    logger.info("Starting weather data PCA analysis")
    logger.info(f"Input file: {args.input}")
    logger.info(f"Output directory: {args.output}")
    logger.info(f"Number of components: {args.n_components}")
    logger.info(f"Hemisphere filter: {args.hemisphere}")
    
    try:
        # Load data
        df = load_weather_data(args.input)
        logger.debug(f"Loaded data type: {type(df)}")
        
        # Filter by hemisphere if specified
        df = filter_by_hemisphere(df, args.hemisphere)
        logger.debug(f"After hemisphere filter type: {type(df)}")
        
        # Get available measurements
        measurements = get_available_measurements(df, args.measurements)
        logger.info(f"Will analyze measurements: {measurements}")
        
        # Process each measurement
        all_results = []
        
        for measurement in tqdm(measurements, desc="Processing measurements"):
            try:
                logger.info(f"Starting processing for {measurement}")
                
                # Process data
                data = process_measurement_data(df, measurement, args.min_stations)
                
                if data is None:
                    logger.warning(f"No data available for {measurement}")
                    continue
                
                logger.info(f"Data processed for {measurement}, shape: {data.shape}")
                
                # Compute PCA
                results = compute_pca_analysis(data, measurement, args.n_components)
                
                # Save results
                save_results(results, args.output, measurement)
                all_results.append(results)
                
                logger.info(f"Successfully processed {measurement}")
                
            except Exception as e:
                logger.error(f"Error processing {measurement}: {e}")
                import traceback
                logger.error(f"Traceback: {traceback.format_exc()}")
                continue
        
        # Generate summary report
        if all_results:
            generate_summary_report(all_results, args.output)
            logger.info(f"Analysis completed successfully. Processed {len(all_results)} measurements.")
        else:
            logger.warning("No measurements were successfully processed.")
    
    except Exception as e:
        logger.error(f"Analysis failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
