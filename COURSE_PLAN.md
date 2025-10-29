## Course description
A project-based introduction to modern, scalable data analytics. Students use AWS and S3 (with Vacoreum cost management), Cursor IDE with AI-assisted development, Dask, and the Python data/ML stack to transform large, real-world public datasets into actionable insights. Teams of eight select a dataset, engineer Parquet dataframes with robust testing, analyze and visualize at scale (including geospatial via ipyleaflet), and answer domain questions using PCA, regression, GAMs, K-means clustering, decision trees, and XGBoost with appropriate statistical inference and hypothesis testing. Final presentations showcase complete data science pipelines from raw data to reproducible insights.

## Prerequisites
* Strong experience with Unix shell, Python, NumPy, Pandas, GitHub, and SSH
* A laptop with Cursor installed (student licence ok)
* Basic statistics: expectation, variance, covariance, correlation
* Basic linear algebra: vectors, norms, orthogonality, orthonormal bases, change of basis

## Project-based Course Plan: Scalable Data Analysis with Dask

- **Format**: 10 weeks; 3 × 45‑minute lectures; one 30‑minute Zoom meeting weekly (alternating TA/Instructor)
- **Teams**: 8 students/team; each team selects a public dataset (weather dataset reserved for instructor demos only)
- **Grading**: 80% project, 20% homework (4 HWs × 5% each)
- **Focus**: AWS/S3 (with Vacoreum cost management), Parquet-centric data engineering, Dask (DataFrame-centric, lazy evaluation, execution graphs), visualization (incl. ipyleaflet), PCA, regression/GAMs, K-means/Decision Trees/XGBoost, hypothesis-driven modeling with p-values, final report and presentation

## Infrastructure and Baseline

- **Stack**: AWS EC2 + S3; Python 3.10+
  - Core: `dask[complete]`, `distributed`, `pandas`, `pyarrow`, `s3fs`, `bokeh`, `matplotlib`, `plotly`
  - Numerics/ML: `dask-ml`, `scikit-learn`, `xarray`, `numba`
  - Inference/Stats: `statsmodels`, `pygam`
  - Visualization maps: `ipyleaflet`
- **Environment**: `environment.yml` committed in each team repo; Parquet is the canonical storage format; S3 URIs for data access
- **Cost Management**: Vacoreum integrated with AWS for budgets, alerts, and reporting
- **Instructor Demo Dataset**: Weather dataset for live demonstrations.

## Weekly Schedule, Labs, and Deliverables

### Week 1 — Kickoff, AWS/S3, Vacoreum, Team Formation
- Lecture: Course scope, evaluation, example questions; AWS accounts, IAM basics, S3 organization; dataset selection criteria (prefer ≥10 GB, public, stable access)
- Deliverables:
  - Project Proposal (1–2 pages): dataset, access plan, initial questions, risks
  - Repo initialized with `environment.yml`, `README`, roles, and tagging policy
  - Vacoreum screenshot: linked account, active budget, alert policy
- HW1 (5%): AWS/S3 setup validation + simple data fetch to S3; cost hygiene checklist; Vacoreum alert test

### Week 2 — Cursor, Notebooks vs Python Files, Testing, Prompt Engineering
- Lecture: Productive workflows in Cursor; pairing with AI responsibly; repo layout for data science (`src/` package + `notebooks/`); when to use notebooks vs modules; testing strategies (`pytest`, data-contract tests, lightweight fixtures); prompt engineering for code, refactors, and reviews; reproducible runs and guardrails
- Deliverables:
  - Repo skeleton with clear module boundaries; `pytest` green locally
  - One refactored notebook paired with a module; minimal documentation on when to use each
  - Prompt snippets (short templates) the team will use in Cursor for common tasks
  - Runnable pipeline (`make` or `python -m`); partition plan documented (keys, expected sizes)
  - Cost visibility: Vacoreum cost trend and storage footprint; table of cost per 1M rows ingested
- HW2 (5%): Convert messy CSV/JSON to Parquet with validation; justify partitioning and compression choices

### Week 3 — Data Ingestion and Parquet Modeling
- Lecture: Raw→bronze→silver modeling; schema discovery; dtypes, timezones; Parquet/Arrow fundamentals; partitioning strategy

### Week 4 — Dask Fundamentals: DataFrame, Lazy Evaluation, Task Graphs
- Lecture: Dask collections, lazy semantics, when to `persist`; Dask dashboard; shuffles vs `set_index`, divisions, categoricals
- Deliverables:
  - Exploratory analysis at scale: joins/groupbys with performance notes (before/after)
  - Partitioning rationale tied to query patterns
  - Cost notes: cluster size vs runtime vs incremental $ (Vacoreum export)
- HW3 (5%): Refactor a Pandas pipeline to Dask; report speed/memory/cost differences

### Week 5 — Visualization at Scale; Geospatial with ipyleaflet
- Lecture: Sampling vs aggregation; tiles/overlays; scalable EDA patterns; map-based summaries
- Deliverables:
  - Reproducible EDA report (figures + narrative) with at least one map-based insight using `ipyleaflet`
  - Demonstrate caching/aggregation to reduce repeated compute and spend

### Week 6 — PCA and Dimensionality Reduction at Scale
- Lecture: Dask Array; chunking; PCA/SVD; reconstruction error and interpretation
- Deliverables:
  - PCA analysis notebook: explained variance and reconstruction error; chunking trade-offs
  - Optional: Compare concepts with instructor’s weather PCA demo (no reuse of dataset)

### Week 7 — Regression and GAMs
- Lecture: Modeling pipeline design; linear/logistic regression; GAMs for nonlinear effects; regularization; p-values and assumptions
- Deliverables:
  - Modeling baseline with documented feature pipeline; diagnostics (residuals, partial dependence, overfit checks)

### Week 8 — K-means, Decision Trees, XGBoost
- Lecture: Unsupervised clustering with K-means; tree-based models (decision trees, random forests); gradient boosting with XGBoost; distributed training with Dask-ML; feature importance and interpretability
- Deliverables:
  - K-means clustering analysis with elbow method and silhouette scores
  - Decision tree and XGBoost models with cross-validation; feature importance analysis; performance comparison
  - Optional: Time permitting, ensemble models combining tree-based and linear approaches

### Week 9 — Hypothesis Testing, Scaling, Tuning, and Report Preparation
- Lecture: Predictive vs causal framing; hypothesis testing; multiple comparisons; robustness checks; dashboard optimization; performance tuning; retries, checkpoints, idempotence; narrative structure for data science reports
- Deliverables:
  - Questions→Model mapping (1–2 pages): targets, metrics, tests, evaluation protocol
  - Performance report: baseline vs tuned (runtime + $) with dashboard screenshots and Vacoreum graphs
  - Draft report (6–10 pages): methods, data, experiments, results, limitations, references
  - Slide deck draft with figures and demo plan
  - Cost section with Vacoreum graphs: spend by service, daily trend, cost per result/figure
  - CI passing: sample-size smoke job, lint, and a 5–10 minute nightly test
- HW4 (5%): Given a scenario, specify hypotheses, appropriate models, and p-value strategy with pitfalls

### Week 10 — Project Presentations
- Presentations: 12–15 minutes/team + Q&A; live demo optional
- Final deliverable submission deadline: All project artifacts due before presentations

## Grading

- **Project (80%)**
  - Milestones (Weeks 2–9): 35%
    - Data engineering quality (schema, Parquet layout, idempotence, validation)
    - Dask proficiency (partitioning, lazy evaluation, dashboard-informed tuning)
    - Visualization quality (scalable summaries, correct use of `ipyleaflet` if applicable)
    - Modeling rigor (PCA interpretation, regression/GAMs, K-means/trees/XGBoost, diagnostics, p-values with correct controls)
  - Final Report: 25% — clarity, methodology, reproducibility, limitations, governance
  - Final Presentation: 15% — storytelling, correctness, insight, Q&A
  - Engineering/Reproducibility Artifacts: 5% — CI, runbook, environment, deterministic runs, cost hygiene (Vacoreum evidence)
- **Homework (20%)**: 4 HWs × 5%
  - HW1: AWS/S3 setup, cost hygiene, Vacoreum alert
  - HW2: CSV/JSON → Parquet modeling with validation
  - HW3: Pandas → Dask refactor with performance/cost analysis
  - HW4: Hypotheses and p-value strategy for a domain question

## Dataset Selection Guidelines

- Public, stable access; permissible licensing
- Prefer ≥10 GB uncompressed or complex multi-file sources
- Clear potential for geospatial or temporal aggregation
- Examples: NYC TLC trips, OpenAQ air quality, OpenStreetMap extracts, NOAA water data, GDELT, Yelp, Common Crawl subsets
- Not allowed: instructor’s weather dataset

## Team Structure and Process

- Suggested roles: data engineer, infra/DevOps, visualization lead, modeling lead, QA/validation, PM/documentation, research/reading, rotating backup
- Add Cost & Governance Lead: owns Vacoreum dashboards, tagging compliance, weekly cost digests, budget adherence
- Weekly stand-up with progress notes and next-week plan; GitHub Projects for task tracking; PR reviews required


## Reproducibility and Artifacts

- All code runnable via `make` or a single `python -m` entrypoint with a clear `README`
- Provide `environment.yml`, sample data fetch script, and seeded randomness for ML
- Results must be reproducible on a fresh environment and with different cluster sizes

