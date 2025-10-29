# Weather Data PCA Analysis Script

This script computes mean and PCA analysis for weather measurements from parquet files.

## Dependencies

Required Python packages:
- dask
- numpy
- pandas
- matplotlib
- tqdm

Install with: `pip install dask numpy pandas matplotlib tqdm`

## Usage

### Basic Usage
```bash
python weather_pca_analysis.py
```

### Advanced Usage
```bash
# Specify custom input file and output directory
python weather_pca_analysis.py --input ../../../weather_data/weather.parquet --output results/

# Analyze specific measurements with more components
python weather_pca_analysis.py --measurements TAVG SNWD --n_components 15

# Analyze only northern hemisphere data
python weather_pca_analysis.py --hemisphere northern --verbose

# Set minimum stations requirement
python weather_pca_analysis.py --min_stations 200
```

## Command Line Options

- `--input, -i`: Input parquet file path (default: ../../../weather_data/joined_stations_weather.parquet)
- `--output, -o`: Output directory for pickle files (default: pca_results)
- `--n_components, -n`: Number of principal components to compute (default: 10)
- `--hemisphere, -hem`: Hemisphere to analyze (northern/southern/both, default: both)
- `--measurements, -m`: Specific measurements to analyze (e.g., TAVG SNWD)
- `--min_stations`: Minimum number of stations required (default: 100)
- `--verbose, -v`: Enable verbose output

## Output

The script generates:
- Individual pickle files for each measurement (e.g., `tavg_pca_results.pkl`)
- Summary report (`analysis_summary.txt`)
- Progress logging to console

## Example Output Structure

```
pca_results/
├── tavg_pca_results.pkl
├── snwd_pca_results.pkl
├── prcp_pca_results.pkl
└── analysis_summary.txt
```

Each pickle file contains:
- `mean`: Mean values for each day of year
- `components`: Principal components
- `explained_variances`: Variance explained by each component
- `explained_variance_ratios`: Proportion of variance explained
- `measurement`: Name of the measurement type
- `data_shape`: Original data dimensions
