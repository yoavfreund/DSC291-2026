# NOAA GHCN by_year Parquet Dataset Summary

## File Organization

The `by_year` parquet dataset is organized in a **hierarchical partitioned structure**:

```
s3://noaa-ghcn-pds/parquet/by_year/
├── YEAR=1750/
│   ├── ELEMENT=PRCP/
│   │   ├── *.snappy.parquet
│   │   └── ...
│   ├── ELEMENT=TMAX/
│   ├── ELEMENT=TMIN/
│   └── ...
├── YEAR=1751/
├── ...
└── YEAR=2025/
```

### Partitioning Scheme

1. **Primary partition: YEAR**
   - Data spans from **1750 to 2025** (264 years total)
   - Each year has its own subdirectory: `YEAR=XXXX/`

2. **Secondary partition: ELEMENT**
   - Within each year, data is further partitioned by weather element type
   - Common elements include: TMAX, TMIN, PRCP, SNOW, SNWD, TAVG, and 60+ others
   - Each element has its own subdirectory: `ELEMENT=XXXX/`

3. **Parquet Files**
   - Multiple `.snappy.parquet` files within each YEAR/ELEMENT directory
   - Files use Snappy compression
   - Typical file size: ~1.6 MB compressed
   - Each file contains ~500,000 rows

## Schema and Fields

### Column Structure (7 columns)

| Column Name | Data Type | Description | Null % | Example Values |
|-------------|-----------|-------------|--------|----------------|
| **ID** | String | 11-character station identification code | 0% | USC00026481, ASN00018192 |
| **DATE** | String | 8-character date in YYYYMMDD format | 0% | 20200101 |
| **DATA_VALUE** | Int64 | Measurement value (units depend on ELEMENT) | 0% | 239 (for TMAX = 23.9°C) |
| **M_FLAG** | String | Measurement Flag (1 char) | 90% | H (see flags below) |
| **Q_FLAG** | String | Quality Flag (1 char) | 99.8% | I, S, O (see flags below) |
| **S_FLAG** | String | Source Flag (1 char) | 0% | 7, S, E, a (see flags below) |
| **OBS_TIME** | String | Observation time in HHMM format | 62% | 0700, 0800, 2400 |

### Sample Data

```
ID              DATE      DATA_VALUE  M_FLAG  Q_FLAG  S_FLAG  OBS_TIME
ASN00018192    20200101       239     None    None      a       None
ASN00018195    20200101       318     None    None      a       None
USR0000OTOK    20200114        56     None    None      7       0700
```

## Weather Elements (ELEMENT codes)

### Core Elements (Most Common)

| Code | Description | Units |
|------|-------------|-------|
| **PRCP** | Precipitation | tenths of mm |
| **SNOW** | Snowfall | mm |
| **SNWD** | Snow depth | mm |
| **TMAX** | Maximum temperature | tenths of degrees C |
| **TMIN** | Minimum temperature | tenths of degrees C |
| **TAVG** | Average temperature | tenths of degrees C |
| **TOBS** | Temperature at observation time | tenths of degrees C |

### Additional Elements (60+ available)

- **AWND** - Average daily wind speed (tenths of m/s)
- **AWDR** - Average daily wind direction (degrees)
- **EVAP** - Evaporation (tenths of mm)
- **RHAV** - Average relative humidity (percent)
- **TSUN** - Total sunshine (minutes)
- **WDF2/WDF5** - Direction of fastest 2-minute/5-minute wind
- **WSF2/WSF5** - Fastest 2-minute/5-minute wind speed
- **WT01-WT18** - Weather types (fog, thunder, hail, etc.)
- And 50+ more specialized measurements

## Flags

### M_FLAG (Measurement Flag)
- Indicates special measurement conditions
- Common values: H (missing data estimated)

### Q_FLAG (Quality Flag)
- Indicates quality issues with the data
- Common values:
  - I - Failed internal consistency check
  - S - Failed spatial consistency check
  - O - Failed outlier check
  - Z - Flagged as suspect by source

### S_FLAG (Source Flag)
- Indicates data source
- Common values:
  - 7 - US Cooperative Summary of the Day
  - S - SNOTEL
  - E - European Climate Assessment
  - a - Australian data
  - Many others for different data providers

## Data Characteristics

### Typical File Contents
- **Rows per file**: ~500,000 observations
- **Unique stations per file**: ~13,000+
- **Date range per file**: Usually 1-2 months worth of daily data
- **Memory usage**: ~138 MB uncompressed per file
- **Compression**: Snappy (~1.6 MB compressed)

### Data Sparsity
- M_FLAG: 90% null (flags only when needed)
- Q_FLAG: 99.8% null (quality issues are rare)
- OBS_TIME: 62% null (not all observations include time)

## Usage Notes

1. **Partitioning Benefits**:
   - Efficient queries by year and/or element type
   - Can read only specific years/elements needed
   - Supports parallel processing with Dask

2. **Unit Conversions**:
   - Temperature: divide by 10 to get °C (e.g., 239 → 23.9°C)
   - Precipitation: divide by 10 to get mm
   - Pressure: divide by 10 to get hPa

3. **Date Handling**:
   - DATE is stored as string in YYYYMMDD format
   - Convert to datetime: `pd.to_datetime(df['DATE'], format='%Y%m%d')`

4. **Station Information**:
   - Station metadata available in `ghcnd-stations.txt`
   - Contains lat/lon, elevation, name for each station ID

## Access Information

- **S3 Bucket**: s3://noaa-ghcn-pds/parquet/by_year/
- **Access**: Public, no credentials required
- **AWS CLI**: Use `--no-sign-request` flag
- **Dask Example**:
  ```python
  import dask.dataframe as dd
  
  # Read all TMAX data for 2020
  df = dd.read_parquet(
      's3://noaa-ghcn-pds/parquet/by_year/YEAR=2020/ELEMENT=TMAX/',
      storage_options={'anon': True}
  )
  ```

## Total Dataset Size

- **Years**: 264 (1750-2025)
- **Elements**: 70+ unique weather elements
- **Partitions**: ~18,000+ year/element combinations
- **Total files**: Hundreds of thousands of parquet files
- **Estimated total records**: Billions of observations

## Documentation References

- Main README: https://noaa-ghcn-pds.s3.amazonaws.com/readme.txt
- by_year README: https://noaa-ghcn-pds.s3.amazonaws.com/readme-by_year.txt
- Stations list: https://noaa-ghcn-pds.s3.amazonaws.com/ghcnd-stations.txt

