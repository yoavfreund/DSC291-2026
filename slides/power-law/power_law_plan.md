---
name: Power-law slides with log-log plots
overview: Create a Beamer slide deck in slides/power-law/ explaining power-law distributions, how to infer the power-law exponent from log-log plots, with visual examples including noisy data.
todos:
  - id: "1"
    content: Create slides/power-law/ directory and power_law.tex with Beamer preamble (Madrid theme, pgfplots, tikz)
    status: pending
  - id: "2"
    content: Add title page and introduction slides (What is power-law, formula, properties)
    status: pending
  - id: "3"
    content: Add log-log plot explanation slides (why log-log, rank-order method, inferring exponent)
    status: pending
  - id: "4"
    content: Create pgfplots figure for clean power-law example (Pareto, α=2.0, with fitted line)
    status: pending
  - id: "5"
    content: Create pgfplots figure for power-law vs normal comparison (side-by-side)
    status: pending
  - id: "6"
    content: Create pgfplots figure for noisy power-law (low noise) with fitted line
    status: pending
  - id: "7"
    content: Create pgfplots figure for noisy power-law (high noise) with fitted line
    status: pending
  - id: "8"
    content: Add slides on detecting power-laws in noisy data (R², visual inspection, thresholds)
    status: pending
  - id: "9"
    content: Add real-world example slide (city sizes/Zipf) and recap slide
    status: pending
  - id: "10"
    content: Compile and verify all figures render correctly, fix any pgfplots warnings
    status: pending
isProject: false
---

# Power-Law Slides Plan

## Overview

Create a Beamer presentation in `slides/power-law/power_law.tex` explaining power-law distributions, log-log plots, and how to infer the power-law exponent, with visual examples including noise.

## Structure and Content

### Slide 1: Title Page

- Title: "Power-Law Distributions"
- Subtitle: "Detecting and measuring power-law exponents from log-log plots"
- Author: CSE255 - Scalable Data Analysis
- Date: \today

### Slide 2: What is a Power-Law?

- Definition: P(x) ∝ x^(-α) where α is the power-law exponent
- Key properties:
  - Many small values, few very large values
  - "Long tail" distribution
  - Common in nature: city sizes, word frequencies, network degrees, earthquake magnitudes
- Visual: Simple schematic showing many small values vs few large values

### Slide 3: Power-Law Formula and Properties

- Mathematical form: P(x) = C · x^(-α) for x ≥ x_min
- α > 0 is the power-law exponent (typically 1 < α < 3)
- Lower α = heavier tail (more extreme values)
- Higher α = lighter tail (more concentrated)
- Visual: Two curves with different α values (e.g., α=1.5 vs α=2.5) on linear scale

### Slide 4: Why Log-Log Plots?

- Problem: Power-laws span many orders of magnitude
- Solution: Take logarithm of both axes
- Key insight: log(P(x)) = log(C) - α·log(x)
- This is a straight line: y = intercept - α·x
- Visual: Side-by-side comparison: linear scale (hard to see) vs log-log scale (straight line)

### Slide 5: Log-Log Rank-Order Plots

- Method: Sort data from largest to smallest
- X-axis: log(rank) where rank = 1, 2, 3, ...
- Y-axis: log(value) for each ranked value
- If power-law: points form a straight line
- The slope = -α (negative of the power-law exponent)
- Visual: Example log-log rank plot with fitted line showing slope

### Slide 6: Example 1: Clean Power-Law (Pareto Distribution)

- Generate Pareto data: α = 2.0
- Plot on log-log rank-order plot
- Fit line and measure slope
- Show: slope ≈ -2.0, so α ≈ 2.0
- Visual: pgfplots figure with:
  - Blue dots: data points
  - Red dashed line: fitted line with slope annotation
  - Axis labels: log(rank) vs log(value)

### Slide 7: Inferring the Exponent

- Step 1: Create log-log rank-order plot
- Step 2: Fit a line (linear regression on log scale)
- Step 3: Extract slope m
- Step 4: Power-law exponent α = -m
- Formula: log(value) = intercept + m·log(rank), so α = -m
- Visual: Diagram showing the process: data → log-log plot → fit line → extract slope → α

### Slide 8: Example 2: Power-Law vs Normal Distribution

- Compare power-law (Pareto) vs normal distribution
- Both on log-log rank-order plots
- Power-law: straight line
- Normal: curved (not a power-law)
- Visual: Two side-by-side plots showing the difference

### Slide 9: Power-Law with Noise (Introduction)

- Real data is noisy
- Noise can obscure the power-law pattern
- Still possible to detect and measure if noise is not too large
- Visual: Clean power-law vs noisy power-law (preview)

### Slide 10: Example 3: Noisy Power-Law (Low Noise)

- Add small Gaussian noise to power-law data
- Plot on log-log rank-order plot
- Points scatter around the line but pattern is still visible
- Fit line and measure slope
- Show: α can still be estimated reasonably well
- Visual: pgfplots with:
  - Scattered blue dots around a line
  - Red dashed fitted line
  - Annotation: "α ≈ 2.0 (despite noise)"

### Slide 11: Example 4: Noisy Power-Law (High Noise)

- Add larger Gaussian noise to power-law data
- Plot on log-log rank-order plot
- Points scatter more widely
- Still possible to fit, but less accurate
- Visual: pgfplots with more scattered points, fitted line with wider confidence interval or error bars

### Slide 12: Detecting Power-Laws in Noisy Data

- Visual inspection: Do points roughly follow a line?
- Statistical test: R² of linear fit on log scale
- Threshold: R² > 0.9 suggests power-law (adjust based on noise level)
- Caution: Noise can create false positives
- Visual: Three examples: clear power-law (high R²), marginal (medium R²), not power-law (low R²)

### Slide 13: Real-World Example: City Sizes

- City population data often follows power-law (Zipf's law)
- Rank cities by population
- Plot on log-log scale
- Typically α ≈ 1.0 (Zipf's law)
- Visual: Schematic or stylized plot showing city size distribution

### Slide 14: Recap

- Power-law: P(x) ∝ x^(-α)
- Log-log rank-order plots reveal power-laws as straight lines
- Slope of line = -α (power-law exponent)
- Noise makes detection harder but still possible
- Common in many natural and social phenomena

## Technical Implementation

### LaTeX Setup

- Use Beamer with Madrid theme (consistent with other slides)
- Packages: `pgfplots`, `tikz`, `amsmath`, `xcolor`
- Define custom colors for data points, fitted lines, etc.
- Use `pgfplotsset{compat=1.17}`

### Figures

All figures will be generated using pgfplots within the LaTeX file (no external images):

1. **Clean Power-Law Plot**: 
   - Generate data points using pgfplots math functions or sampled coordinates
   - Use `\addplot` with log-log axis
   - Add fitted line using `\addplot` with calculated slope

2. **Noisy Power-Law Plots**:
   - Use `scatter` plot style with random noise added to coordinates
   - Can use `\pgfmathsetseed` for reproducibility
   - Add noise using `\pgfmathparse` with random functions

3. **Comparison Plots**:
   - Use `groupplots` or side-by-side `tikzpicture` environments
   - Consistent axis styling and colors

### Key Formulas in Slides

- P(x) = C · x^(-α)
- log(P(x)) = log(C) - α·log(x)
- α = -slope (from log-log plot)

### Color Scheme

- Data points: blue
- Fitted lines: red (dashed)
- Clean examples: solid colors
- Noisy examples: slightly transparent or different marker styles

## File Structure

- Create directory: `slides/power-law/`
- Main file: `slides/power-law/power_law.tex`
- Follow naming convention consistent with other slide decks

## References

- Content inspired by `weather/Basic_Analysis/3.powerlaw_loglog_explained.ipynb`
- Mathematical foundation: Power-law distributions, Pareto distribution
- Visual style: Match existing slide decks (Madrid theme, pgfplots for figures)
