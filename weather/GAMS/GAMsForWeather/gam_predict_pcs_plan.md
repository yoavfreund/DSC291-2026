# Plan: GAM Notebook for Predicting Top 3 PCs from Geographic Variables

## Objective
Create a notebook that:
1. **Visualizes** the TAVG PCA structure (mean, top 3 eigenvectors, variance explained)
2. **Predicts** the top three PC coefficients from latitude, distance to ocean, longitude, and elevation using GAMs

---

## Part I: PCA Visualization (Initial Section)

### Cell 1: Title and Introduction (Markdown)
- Title: "GAMs to Predict TAVG PC Coefficients from Geography"
- Brief description:
  - Use PCA of yearly TAVG (temperature) profiles
  - Predict PC1, PC2, PC3 from latitude, distance to coast, longitude, and elevation
  - Start with visualizing the PCA structure

### Cell 2: Imports and Setup (Code)
- Imports: `numpy`, `pandas`, `matplotlib.pyplot`, `dask.dataframe`, `pickle`, `Path`
- pygam: `LinearGAM`, `s`, `l`
- SciPy 2.0+ compatibility patch for `csr_matrix.A` and `csc_matrix.A`
- Paths:
  - `PCA_PATH = weather/weather_info/pca_results/tavg_pca_results.pkl`
  - `DATA_PATH = /home/yfreund/weather_data/stations_weather_with_dist2coast.parquet` (or `per_row_coefficients.parquet`)

### Cell 3: Load PCA Results (Code)
- Load `tavg_pca_results.pkl`
- Extract: `mean` (365,), `components` (10, 365), `explained_variance_ratios`
- Print shapes and top-3 variance ratios

### Cell 4: Plot Mean and Top 3 Eigenvectors (Code)
- **Separate axes** for mean vs PCs:
  - Left y-axis: mean TAVG profile (day 1–365)
  - Right y-axis (twin): PC1, PC2, PC3 eigenvectors
- X-axis: day of year (1–365)
- Reference: `tavg_quickstart.ipynb` (fig with `ax_mean` and `ax_pc = ax_mean.twinx()`)
- Colors: mean in black; PC1 blue, PC2 orange, PC3 green
- Labels: "Mean TAVG", "PC1", "PC2", "PC3"
- Title: "TAVG Mean and Top 3 PCA Eigenvectors"

### Cell 5: Variance Explained Plot (Code)
- Bar chart of **percentage variance explained** per PC (at least top 10)
- X-axis: PC index (PC1, PC2, …, PC10)
- Y-axis: explained variance ratio (%)
- Optional: cumulative line overlay
- Title: "Percentage Variance Explained by Principal Components"

---

## Part II: Data Preparation

### Cell 6: Load TAVG Data and Compute PC Coefficients (Code)
- Load weather data (stations_weather_with_dist2coast or per_row_coefficients)
- Filter `ELEMENT == 'TAVG'`
- Compute PC1, PC2, PC3 for each station-year:
  - `daily_data = (day_1…day_365) - pca_mean`
  - `PCi = daily_data @ components[i-1]`
- Reference: `tavg_pc1_geographic.ipynb` for projection logic

### Cell 7: Aggregate by Station and Join Geography (Code)
- Group by station ID
- Aggregate: `mean(PC1)`, `mean(PC2)`, `mean(PC3)`, `first(latitude)`, `first(longitude)`, `first(elevation)`, `first(dist_to_coast)`
- Handle `dist_to_water_m` if `dist_to_coast` is missing
- Drop rows with missing predictors or invalid elevation (-999.9)
- Result: one row per station with `lat`, `lon`, `elevation`, `dist_to_coast`, `PC1`, `PC2`, `PC3`

### Cell 8: Prepare Predictor Matrix (Code)
- Predictors: `latitude`, `dist_to_coast`, `longitude`, `elevation`
- X: (n_stations, 4)
- Optional subsample (e.g., 50k) if large
- Column order for GAM terms: `s(0)` latitude, `l(1)` dist_to_coast, `l(2)` longitude, `l(3)` elevation

---

## Part III: GAM Modeling

### Cell 9: Fit GAMs for PC1, PC2, PC3 (Code)
- For each response `y in [PC1, PC2, PC3]`:
  - `LinearGAM(s(0, n_splines=20) + l(1) + l(2) + l(3))` — spline on latitude, linear on dist_to_coast, longitude, elevation
  - `.gridsearch(X, y, progress=False)`
- Store three fitted GAM objects
- Print summary for each

### Cell 10: Partial Dependence Plots (Code)
- 3×4 grid: rows = PC1, PC2, PC3; columns = latitude, dist_to_coast, longitude, elevation
- For each GAM and term: `generate_X_grid`, `partial_dependence(..., width=0.95)`
- Plot with confidence bands

### Cell 11: Goodness of Fit (Code)
- For each GAM: R², MAE, RMSE, AIC
- Optional: table summarizing all three models

---

## Part IV: Optional Enhancements

### Optional: Interpret PC1, PC2, PC3
- Short markdown: PC1 ≈ seasonal amplitude; PC2/PC3 capture phase and higher-order patterns
- Link to variance plot for context

---

## Key Files to Reference
- `weather/GAMS/GAMsForWeather/tavg_quickstart.ipynb` — mean+PC plot, GAM setup
- `weather/Folium/tavg_pc1_geographic.ipynb` — PC coefficient computation
- `weather/GAMS/GAMsForWeather/gam_geographic_predictors.ipynb` — GAM structure, SciPy patch
- `weather/weather_info/pca_results/tavg_pca_results.pkl` — PCA mean and components
- `weather/PCA_Analysis/compute_PCA_vectors/dask_pca.py` — `plot_mean_and_pcs` (alternative)

## Data Paths
- PCA: `weather/weather_info/pca_results/tavg_pca_results.pkl` (relative to GAMsForWeather: `../../weather_info/pca_results/tavg_pca_results.pkl`)
- Weather: `/home/yfreund/weather_data/stations_weather_with_dist2coast.parquet` or `per_row_coefficients.parquet`
