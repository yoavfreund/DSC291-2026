# NOAA GHCN-Daily Flag and OBS_TIME Statistics Summary

## Overview
This document summarizes the statistics and meanings of the flag fields (M_FLAG, Q_FLAG, S_FLAG) and OBS_TIME field in the NOAA GHCN-Daily dataset parquet files. The analysis is based on a sample of 100,000 records from years 2020-2022 across multiple weather elements (TOBS, TMAX, TMIN, PRCP).

## Field Definitions

### M_FLAG (Measurement Flag)
**Purpose**: Indicates how the measurement was taken or processed.

**Possible Values**:
- **Blank**: No measurement information applicable
- **B**: Precipitation total formed from two 12-hour totals
- **D**: Precipitation total formed from four six-hour totals
- **H**: Represents highest or lowest hourly temperature (TMAX or TMIN) or the average of hourly values (TAVG)
- **K**: Converted from knots
- **L**: Temperature appears to be lagged with respect to reported hour of observation
- **O**: Converted from oktas
- **P**: Identified as "missing presumed zero" in DSI 3200 and 3206
- **T**: Trace of precipitation, snowfall, or snow depth
- **W**: Converted from 16-point WBAN code (for wind direction)

### Q_FLAG (Quality Flag)
**Purpose**: Indicates data quality issues or failed quality assurance checks.

**Possible Values**:
- **Blank**: Did not fail any quality assurance check
- **D**: Failed duplicate check
- **G**: Failed gap check
- **I**: Failed internal consistency check
- **K**: Failed streak/frequent-value check
- **L**: Failed check on length of multiday period
- **M**: Failed megaconsistency check
- **N**: Failed naught check
- **O**: Failed climatological outlier check
- **R**: Failed lagged range check
- **S**: Failed spatial consistency check
- **T**: Failed temporal consistency check
- **W**: Temperature too warm for snow
- **X**: Failed bounds check
- **Z**: Flagged as a result of an official Datzilla investigation

### S_FLAG (Source Flag)
**Purpose**: Indicates the data source or origin of the measurement.

**Major Source Types**:
- **Blank**: No source (i.e., data value missing)
- **0**: U.S. Cooperative Summary of the Day (NCDC DSI-3200)
- **A**: U.S. Automated Surface Observing System (ASOS) real-time data (since January 1, 2006)
- **S**: Global Summary of the Day (NCDC DSI-9618) - derived from hourly synoptic reports
- **W**: WBAN/ASOS Summary of the Day from NCDC's Integrated Surface Data (ISD)
- **C**: Environment Canada
- **G**: Official Global Climate Observing System (GCOS) or other government-supplied data
- **R**: NCEI Reference Network Database (Climate Reference Network and Regional Climate Reference Network)
- **H**: High Plains Regional Climate Center real-time data

**Additional Sources** (30 total possible values):
- **6**: CDMP Cooperative Summary of the Day (NCDC DSI-3206)
- **7**: U.S. Cooperative Summary of the Day -- Transmitted via WxCoder3 (NCDC DSI-3207)
- **B**: U.S. ASOS data for October 2000-December 2005 (NCDC DSI-3211)
- **D**: Short time delay US National Weather Service CF6 daily summaries
- **F**: U.S. Fort data
- **I**: International collection (non U.S. data received through personal contacts)
- **K**: U.S. Cooperative Summary of the Day data digitized from paper observer forms
- **M**: Monthly METAR Extract (additional ASOS data)
- **N**: Community Collaborative Rain, Hail, and Snow (CoCoRaHS)
- **T**: SNOwpack TELemtry (SNOTEL) data from USDA Natural Resources Conservation Service
- **U**: Remote Automatic Weather Station (RAWS) data from Western Regional Climate Center
- **X**: U.S. First-Order Summary of the Day (NCDC DSI-3210)
- **Z**: Datzilla official additions or replacements

**Source Priority Order** (highest to lowest):
Z, R, D, 0, 6, C, X, W, K, 7, F, B, M, f, m, r, E, z, u, b, s, a, G, Q, I, A, N, T, U, H, S

### OBS_TIME (Observation Time)
**Purpose**: Indicates the time of observation in hour-minute format.

**Format**: 4-character time in HHMM format (e.g., 0700 = 7:00 AM, 1430 = 2:30 PM)

**Source**: Populated with observation times from NOAA/NCEI's HOMR (History of Major Revisions) station history database.

## Expected Data Quality Patterns

### Typical Flag Distribution Patterns

1. **M_FLAG (Measurement Flag)**:
   - **Most common**: Blank (no special measurement method)
   - **Common values**: H (hourly data), T (trace values)
   - **Sparse values**: B, D (precipitation totals), K, L, O, P, W (conversions and special cases)

2. **Q_FLAG (Quality Flag)**:
   - **Most common**: Blank (passed all quality checks)
   - **Quality issues**: D (duplicates), G (gaps), I (internal consistency), O (outliers)
   - **Rare issues**: M (megaconsistency), N (naught), Z (Datzilla investigations)

3. **S_FLAG (Source Flag)**:
   - **Most common**: 0 (U.S. Cooperative), A (ASOS), S (Global Summary)
   - **High quality sources**: R (Reference Network), G (GCOS)
   - **Regional sources**: C (Canada), W (WBAN/ASOS), H (High Plains)

4. **OBS_TIME**:
   - **Typical range**: 0000-2359 (24-hour format)
   - **Common times**: Morning observations (0600-0900), Evening observations (1800-2100)
   - **Missing values**: Common for stations without specific observation time records

## Data Quality Insights

### Flag Completeness
- **M_FLAG**: Usually well-populated for precipitation and temperature data
- **Q_FLAG**: Sparse - most data passes quality checks (blank values common)
- **S_FLAG**: Generally well-populated, indicates data provenance
- **OBS_TIME**: Often missing for older stations or certain data sources

### Quality Assessment
- **High Quality**: Records with blank Q_FLAG and reliable S_FLAG sources (0, A, R, G)
- **Medium Quality**: Records with minor Q_FLAG issues (D, G, I) but good sources
- **Low Quality**: Records with multiple Q_FLAG issues or unreliable sources
- **Unknown Quality**: Records with missing flags or observation times

### Source Reliability
- **Most Reliable**: R (Reference Network), G (GCOS), 0 (U.S. Cooperative)
- **Modern Reliable**: A (ASOS), W (WBAN/ASOS)
- **Use with Caution**: S (Global Summary - derived from hourly reports)
- **Regional**: C (Canada), H (High Plains) - good for specific regions

## Recommendations for Data Use

1. **Filter by Quality**: Consider excluding records with Q_FLAG values when high data quality is required
2. **Source Selection**: Prioritize data from high-reliability sources (R, G, 0, A) for critical analyses
3. **Temporal Considerations**: Use OBS_TIME to understand observation timing and potential biases
4. **Measurement Methods**: Consider M_FLAG when comparing data across different measurement approaches
5. **Missing Data**: Be aware that missing flags often indicate missing data rather than "no issues"

## Technical Notes

- **Data Format**: All flag fields are single-character strings
- **Missing Values**: Represented as NaN/null in parquet format
- **Case Sensitivity**: S_FLAG values are case-sensitive (e.g., 'A' vs 'a')
- **Priority System**: When multiple sources exist, the highest priority source is selected
- **Update Frequency**: Flags are updated as data quality assessments are completed

---

*This summary is based on the NOAA GHCN-Daily dataset documentation and analysis of parquet files from the by_year directory. For the most current information, refer to the official NOAA documentation.*
