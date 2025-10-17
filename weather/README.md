# Weather Data Processing Pipeline

This directory contains tools and notebooks for processing NOAA GHCN weather data using Dask for distributed computing. The pipeline transforms weather data from long format to wide format and provides utilities for concatenating and analyzing large weather datasets.

## 📁 Directory Structure

```
weather/
├── README.md                           # This file
├── data/                              # Processed weather data (parquet files)
├── old/                               # Legacy files and documentation
├── *.py                               # Python scripts
├── *.ipynb                            # Jupyter notebooks
└── *.log                              # Processing logs
```

## 🚀 Quick Start

### Prerequisites

```bash
pip install dask[complete] s3fs pandas numpy pyarrow
```

### Basic Usage

1. **Process weather data for multiple years:**
   ```bash
   python process_multiple_years.py --start_year 2020 --end_year 2022
   ```

2. **Concatenate existing parquet files:**
   ```bash
   python concatenate_weather_data.py --data_dir data --start_year 1950 --end_year 1954
   ```

3. **Explore data interactively:**
   ```bash
   jupyter notebook core_loader.ipynb
   ```

## 📋 Files Overview

### Core Python Scripts

#### `process_multiple_years.py`
**Main processing script for multi-year weather data transformation**

- **Purpose**: Downloads and processes weather data from NOAA GHCN S3 bucket
- **Features**: 
  - Transforms long format to wide format
  - Processes multiple years in parallel
  - Uses distributed Dask cluster
  - Saves individual year files and combined dataset
- **Usage**:
  ```bash
  python process_multiple_years.py --start_year 2020 --end_year 2022 --n_workers 20 --memory_per_worker 4GB
  ```

#### `concatenate_weather_data.py`
**Utility script for concatenating existing parquet files**

- **Purpose**: Combines multiple year parquet files into a single dataset
- **Features**:
  - Batch processing for large datasets
  - Error handling for corrupted files
  - Progress reporting
- **Usage**:
  ```bash
  python concatenate_weather_data.py --data_dir data --start_year 1950 --end_year 2025
  ```

#### `weather_transformation.py`
**Core transformation functions**

- **Purpose**: Contains reusable functions for data transformation
- **Key Functions**:
  - `transform_long_to_wide()`: Converts long format to wide format
  - `display_dataframe_info()`: Shows dataframe statistics
  - `save_wide_dataframe()`: Saves data to parquet files
- **Usage**: Imported by other scripts and notebooks

#### `cluster_utils.py`
**Dask cluster management utilities**

- **Purpose**: Manages Dask distributed clusters
- **Features**:
  - Automatic cluster setup and cleanup
  - Memory and worker configuration
  - Dashboard access
- **Usage**: Imported by processing scripts

### Jupyter Notebooks

#### `core_loader.ipynb`
**Single-year weather data processing**

- **Purpose**: Demonstrates processing weather data for a single year (2020)
- **Features**:
  - S3 data loading
  - Long-to-wide transformation
  - Dask cluster management
- **Use Case**: Learning and testing single-year processing

#### `noaa_ghcn_s3_exploration.ipynb`
**Data exploration and analysis**

- **Purpose**: Explores NOAA GHCN S3 dataset structure and content
- **Features**:
  - S3 bucket exploration
  - Data schema analysis
  - Visualization examples
- **Use Case**: Understanding data structure before processing

#### `concatenate_1950_1954.ipynb`
**Concatenation example notebook**

- **Purpose**: Demonstrates concatenating multiple year files
- **Features**:
  - File discovery and loading
  - Data concatenation
  - Result verification
- **Use Case**: Learning concatenation workflow

## 📊 Data Format

### Input Format (Long)
```
ID          DATE      ELEMENT    DATA_VALUE
USC00026481 20200101  TMAX       239
USC00026481 20200101  TMIN       156
USC00026481 20200101  PRCP       0
```

### Output Format (Wide)
```
ID          year  ELEMENT  day_1  day_2  ...  day_365
USC00026481 2020  TMAX     239    245    ...  156
USC00026481 2020  TMIN     156    162    ...  89
USC00026481 2020  PRCP     0      0      ...  0
```

## 🔧 Configuration

### Dask Cluster Settings

Default configuration:
- **Workers**: 20
- **Memory per worker**: 4GB
- **Total memory**: 80GB
- **Dashboard**: http://127.0.0.1:8787/status

### Data Processing Settings

- **Missing values**: 999999.0 (instead of NaN)
- **Aggregation**: Mean values for multiple observations
- **Date range**: 1-365 days per year
- **Measurements**: TOBS, TMAX, TMIN, PRCP, SNOW, SNWD

## 📈 Performance

### Typical Processing Times

| Years | Files | Processing Time | Memory Usage |
|-------|-------|----------------|--------------|
| 1 year | 6 files | 2-5 minutes | ~4GB |
| 5 years | 30 files | 10-15 minutes | ~8GB |
| 76 years | 456 files | 30-60 minutes | ~16GB |

### Optimization Tips

1. **Use appropriate cluster size** for your data volume
2. **Process in batches** for very large datasets
3. **Monitor memory usage** via Dask dashboard
4. **Use SSD storage** for faster I/O

## 🐛 Troubleshooting

### Common Issues

#### 1. Memory Errors
```
MemoryError: Unable to allocate array
```
**Solution**: Reduce cluster size or process fewer years at once

#### 2. Empty Parquet Files
```
ValueError: No files satisfy the parquet_file_extension criteria
```
**Solution**: Check if parquet files exist and are not corrupted

#### 3. S3 Connection Issues
```
ConnectionError: Failed to connect to S3
```
**Solution**: Check internet connection and S3 bucket accessibility

### Debug Tools

- **Dask Dashboard**: Monitor cluster performance
- **Log files**: Check `process_multiple_years.log` for detailed logs
- **Column validation**: Use `debug_columns.py` for schema issues

## 📚 Examples

### Example 1: Process Recent Data
```bash
# Process 2020-2022 weather data
python process_multiple_years.py --start_year 2020 --end_year 2022 --n_workers 16 --memory_per_worker 8GB
```

### Example 2: Concatenate Historical Data
```bash
# Combine 1950s data
python concatenate_weather_data.py --data_dir data --start_year 1950 --end_year 1959
```

### Example 3: Custom Output
```bash
# Save with custom filename
python concatenate_weather_data.py --data_dir data --start_year 2020 --end_year 2022 --output_name my_weather_data.parquet
```

## 📖 Documentation

### Additional Resources

- **Legacy Documentation**: See `old/README_multiple_years.md` for detailed processing documentation
- **Data Schema**: See `old/BY_YEAR_PARQUET_SUMMARY.md` for NOAA GHCN data structure
- **Examples**: Check `old/` directory for additional example scripts

### Data Sources

- **NOAA GHCN**: Global Historical Climatology Network
- **S3 Bucket**: `s3://noaa-ghcn-pds/parquet/by_year/`
- **Documentation**: https://noaa-ghcn-pds.s3.amazonaws.com/readme.txt

## 🤝 Contributing

### Adding New Features

1. **New transformation functions**: Add to `weather_transformation.py`
2. **New processing scripts**: Follow existing patterns in `process_multiple_years.py`
3. **New notebooks**: Use `core_loader.ipynb` as a template

### Code Style

- Follow PEP 8 guidelines
- Add docstrings to all functions
- Include type hints where appropriate
- Test with small datasets before large processing

## 📄 License

This project is part of the CSE255 course materials. Please refer to your course guidelines for usage and distribution policies.

---

**Last Updated**: October 2025  
**Maintainer**: CSE255 Weather Data Processing Team
