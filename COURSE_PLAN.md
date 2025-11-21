# Course Plan 2 — 10-Week Schedule Skeleton

## Format Summary
- Duration: 10 weeks
- Sessions: Three classes per week (Monday, Wednesday, Friday)
- Labs/Assignments: total of 4
- - Quiz once a week
- Deliverables & Assessments: TBD
- notebooks, python code, test code
- Prompt for plan, plan, code
---

### Week 1 — Introduction and Setup
- **Class (Mon)**: Course overview, prediction vs. explanation, tooling expectations, weekly quiz cadence
- **Class (Wed)**: Team formation (roles: cluster controller, report creator, repo organizer, statistician, comms lead), repo hygiene, concise reporting patter
- **Class (Fri)**: AWS orientation (EC2, S3, IAM basics), launching cost-controlled instances, GitHub workflow primer
- **Deliverables / Notes**: _TBD (HW defined by instructor)_

### Week 2 — Memory Hierarchy, HDFS, Parquet
- **Class (Mon)**: Memory hierarchy, cache vs. disk vs. network latency, implications for distributed jobs
- **Class (Wed)**: History of large-scale storage (HDFS evolution, object stores), Parquet layout, compression/encoding options
- **Class (Fri)**: MapReduce patterns, lazy computation planning, translating conceptual execution plans into Dask
- **Deliverables / Notes**: _TBD (HW defined by instructor)_

### Week 3 — Dask
- **Class (Mon)**: Cursor + AI-supported coding workflow, Dask APIs tour, navigating documentation efficiently
- **Class (Wed)**: Dask theory—graphs, schedulers, persistence, partitioning strategies, debugging lazy execution
- **Class (Fri)**: Hands-on lab with weather and taxi data; profiling `compute()`, `persist()`, and diagnostics dashboard
- **Deliverables / Notes**: _TBD (HW defined by instructor)_

### Week 4 — Data Ingestion, Data Cleaning and Basic Statistical Analysis, Visualization on maps
- **Class (Mon)**: CSV ingestion pipelines, schema enforcement, writing tidy Parquet datasets
- **Class (Wed)**: Data quality metrics, covariance/correlation tracking at scale, partition-aware statistics; geospatial visualization with Folium and vector tiles
- **Class (Fri)**: Pivoting/repartitioning scenarios, rare-category pruning, NaN remediation strategies; meteorological mapping (xarray + cartopy + interactive maps)
- **Deliverables / Notes**: _TBD (HW defined by instructor)_

### Week 5 — PCA I: Theory
- **Class (Mon)**: Linear algebra refresher, singular value decomposition intuition, Sanjoy's slides walkthrough
- **Class (Wed)**: Eigenvalue decomposition, principal components derivation, variance explained concepts
- **Class (Fri)**: Mathematical foundations, geometric interpretation, theoretical properties of PCA
- **Deliverables / Notes**: _TBD (HW defined by instructor)_

### Week 6 — PCA II: applications
- **Class (Mon)**: Applying PCA to temperature anomalies (TAVG), interpreting components
- **Class (Wed)**: Reconstruction error analysis, dimensionality selection heuristics
- **Class (Fri)**: Communicating findings, practical considerations, case studies
- **Deliverables / Notes**: _TBD (HW defined by instructor)_

### Week 7 — Splines
- **Class (Mon)**: Basis functions, smoothing penalties, interpreting spline terms
- **Class (Wed)**: Spline fitting techniques, knot selection, degrees of freedom
- **Class (Fri)**: Tensor-product splines, regularization tuning, practical applications
- **Deliverables / Notes**: _TBD (HW defined by instructor)_

### Week 8 — GAMs
- **Class (Mon)**: Introduction to Generalized Additive Models, additive structure, link functions
- **Class (Wed)**: Hands-on with pyGAM; comparing splines vs. tree-based fits on weather signals
- **Class (Fri)**: Multivariate GAM case studies (climate + mobility), factor terms, shape constraints; model diagnostics (QQ plots, residual structure, deviance)
- **Deliverables / Notes**: _TBD (HW defined by instructor)_

### Week 9 — Boosting: theory
- **Class (Mon)**: Gradient boosting fundamentals, bias-variance review, connection to additive models
- **Class (Wed)**: Boosting algorithms (AdaBoost, gradient boosting), loss functions, regularization
- **Class (Fri)**: Theoretical properties, convergence analysis, ensemble methods theory
- **Deliverables / Notes**: _TBD (HW defined by instructor)_

### Week 10 — Boosting: XGBoost
- **Class (Mon)**: XGBoost/LightGBM with Dask, handling categorical/temporal features, hyperparameter sweeps
- **Class (Wed)**: Model monitoring, feature importance narratives, integrating boosted models into pipelines
- **Class (Fri)**: Advanced XGBoost techniques, distributed training, production deployment considerations
- **Deliverables / Notes**: _TBD (HW defined by instructor)_


---

_Use this skeleton to flesh out weekly themes, lecture focus, labs, and assessments as you iterate._
