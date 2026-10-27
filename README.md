# Spatial Patterns and the Rating-Popularity Relationship of Tourist Destinations in Bali

A reproducible geospatial analysis of 1,452 Google Maps tourist destination records in Bali, Indonesia. The project combines data-quality auditing, descriptive statistics, category and regional comparisons, point mapping, Spearman rank correlation, and a conditional global Moran's I analysis.

The rating count (`jumlah_rating`) is treated as a measure of online review engagement, not as visitor volume. The analysis is observational and cross-sectional. It does not estimate tourist arrivals, spending, satisfaction, or causal effects.

## Contents

- [Overview](#overview)
- [Research questions](#research-questions)
- [Dataset](#dataset)
- [Methods](#methods)
- [Key results](#key-results)
- [Figures](#figures)
- [Repository structure](#repository-structure)
- [Reproducing the analysis](#reproducing-the-analysis)
- [Outputs](#outputs)
- [Limitations](#limitations)
- [Data availability and licensing](#data-availability-and-licensing)
- [Citation and license](#citation-and-license)
- [Acknowledgements](#acknowledgements)

## Overview

This repository contains the full analysis pipeline for an exploratory study of tourist destinations in Bali. It was built to support an academic paper and to remain runnable locally and in Google Colab.

The project answers four questions:

1. How are the destination records distributed by category, regency or city, and subdistrict?
2. What is the direction and strength of the association between Google ratings and the number of Google ratings?
3. Do ratings and rating counts show spatial autocorrelation?
4. Are the main findings robust to data-quality exclusions and alternative analytical choices?

The notebook audits the source file before analysis, keeps the raw CSV unchanged, and exports every table and figure used in the report.

## Research questions

- **RQ1, geographic distribution:** How are the tourist destinations represented in the dataset distributed across regencies or city and subdistricts?
- **RQ2, rating-popularity relationship:** What is the direction and strength of the association between Google rating and the number of Google ratings?
- **RQ3, geographic patterns:** Do rating values and rating counts show spatial concentration or spatial autocorrelation?
- **RQ4, robustness:** Do the main findings remain reasonably consistent after data-quality exclusions and alternative analytical choices?

RQ3 is conditional. Spatial inference is reported only after reviewing coordinate validity, coincident locations, sample size, and the spatial weights design.

## Dataset

The analysis uses the supplied file `data/raw/bali_tourist_destination.csv`.

| Item | Value |
|---|---|
| Records | 1,452 |
| Columns | 11 |
| Destination categories | 4 |
| Regencies or city | 9 |
| Subdistricts | 56 |
| Mapping sample, valid Bali coordinates | 1,445 |
| Rating and rating-count sample | 1,437 |

Expected fields:

- `id_tempat`
- `nama_tempat_wisata`
- `kategori`
- `kecamatan`
- `kabupaten_kota`
- `rating`
- `jumlah_rating`
- `latitude`
- `longitude`
- `link_google_maps`
- `link_gambar`

The file does not document its extraction date or full provenance. The analysis therefore makes no temporal claims.

`data/raw/bali_tourist_destination.csv` is the preserved input used by the analysis. The copy at the repository root is the original download and has the same SHA-256 hash:

```text
68f4ae5a8cb5f90ebf5f11c8263a8b33c2a425c85df66c936050e28e9cb4237d
```

### Data audit summary

| Check | Result |
|---|---|
| Exact duplicate rows | 0 |
| Repeated destination IDs | 0 |
| Repeated names, exact matches after the first | 15 |
| Rows in case-insensitive name groups | 34 |
| Rows with rating recorded as zero | 15 |
| Rows with rating count recorded as zero | 15 |
| Unparseable numeric values | 0 |
| Missing coordinates | 0 |
| Coordinates outside the broad Bali bounding box | 7 |
| Rows sharing a coordinate with another record | 24 |
| Rows matching another record on name, coordinates, rating, and count | 4 |
| Missing image links | 4 |

Zero ratings are treated as unrated records, not as literal scores of zero. The seven records outside the broad Bali bounding box are retained in the processed data and excluded only from geographic mapping and spatial analysis. Repeated names and matching records are exported for review and retained in the primary analysis.

## Methods

The workflow follows the stages in `METHODOLOGY.md`:

1. **Data audit.** Read the CSV as text, check the actual schema, report missing values, duplicate rows, repeated IDs, repeated names, and numeric ranges.
2. **Transparent cleaning.** Trim whitespace, convert numeric fields with explicit failure tracking, flag invalid or implausible values, and keep a cleaning log. No source records are dropped from the processed file.
3. **Analysis-specific samples.** Define separate samples for geographic mapping, rating summaries, and the rating-count association. Report denominators for every result.
4. **Descriptive analysis.** Counts by category, regency or city, and subdistrict; rating and rating-count summaries including median and interquartile range; distribution plots and group comparisons.
5. **Rating-popularity association.** Spearman's rank correlation with a percentile bootstrap confidence interval. Pearson correlations are reported only as secondary comparisons.
6. **Geographic description.** Static point maps with a local scale bar and an aspect-corrected longitude and latitude display. Distance-based spatial weights use UTM zone 50S metres, not raw longitude and latitude distances.
7. **Conditional spatial autocorrelation.** Global Moran's I with row-standardised k-nearest-neighbour weights, permutation inference, multiple k settings, a coordinate-level aggregation, and a largest-connected-component sensitivity check.
8. **Robustness checks.** Recompute the rank association under alternative eligibility rules and data-quality exclusions.
9. **Export.** Save analysis-ready data, tables, figures, and a Markdown report.

All randomized procedures use a fixed seed. Dependency versions are recorded in `requirements.txt` and `outputs/tables/environment_versions.csv`.

## Key results

### Rating and rating-count distributions

| Measure | Result |
|---|---|
| Median Google rating | 4.60 |
| Rating interquartile range | 4.40 to 4.80 |
| Mean Google rating | 4.55, SD 0.32 |
| Median number of Google ratings | 112 |
| Rating-count interquartile range | 25 to 477 |
| Maximum number of Google ratings | 101,523 |

The rating distribution is concentrated near the top of the scale. The rating-count distribution is strongly right-skewed, so the median and logarithmic displays are more informative than the mean alone.

### Rating-popularity association

| Analysis | Result |
|---|---|
| Sample | 1,437 records |
| Spearman rho | -0.218 |
| 95% percentile bootstrap CI | -0.274 to -0.166 |
| p-value | 5.49e-17 |
| Pearson correlation, raw count | -0.020 |
| Pearson correlation, log1p count | -0.114 |

The rank association is negative and weak. The near-zero Pearson value and the modest negative Spearman value are not contradictory: Pearson uses the raw count scale, where a few very large counts dominate, while Spearman uses ranks.

This association describes the supplied records. It does not show that ratings cause review engagement, or that review counts measure visitor demand.

### Group comparisons

Kruskal-Wallis tests detected differences in ratings and rating counts across categories and regencies. Effect sizes were small to modest, with epsilon-squared values between 0.012 and 0.056. Twenty-seven pairwise Dunn comparisons remained significant after Holm adjustment. These tests do not control for category composition, access, promotion, destination age, or unobserved factors.

### Spatial autocorrelation

Global Moran's I was estimated for 1,430 records with valid Bali coordinates and a rating above zero.

| Variable | k = 4 | k = 8 | k = 12 |
|---|---|---|---|
| Google rating | 0.082 | 0.059 | 0.050 |
| log1p number of Google ratings | 0.126 | 0.118 | 0.105 |

All permutation p-values were 0.001 with 999 permutations. At k = 8, the weights formed two connected components: the Nusa Penida and Lembongan records were not linked to the mainland. A largest-component sensitivity check gave I = 0.119 for log rating count. The coordinate-level aggregation produced similar results.

These are modest global spatial autocorrelation statistics, not local hotspot results. The statistic depends on the weights design and on uneven sampling density.

### Robustness

The rank association stayed negative and weak across alternative specifications:

| Specification | N | Spearman rho |
|---|---|---|
| Primary sample | 1,437 | -0.218 |
| Include zero ratings and zero counts as observed values | 1,452 | -0.181 |
| Exclude all records flagged as likely duplicates | 1,433 | -0.219 |
| Deduplicate matching records, keep first | 1,435 | -0.219 |
| Exclude records sharing a coordinate | 1,414 | -0.215 |
| Restrict to records inside the Bali bounding box | 1,430 | -0.217 |
| Restrict to ratings of 4 or above | 1,380 | -0.272 |

## Figures

![Destination records in Bali by category](outputs/figures/07_map_destinations.png)

![Google rating and number of Google ratings](outputs/figures/05_rating_vs_count.png)

More figures are available in `outputs/figures/`, including category counts, regency counts, rating and rating-count distributions, group comparisons, and attribute maps.

## Repository structure

```text
.
├── data/
│   ├── raw/                          # Original input, preserved unchanged
│   └── processed/                    # Analysis-ready data and flagged records
├── notebooks/
│   └── 01_exploratory_geospatial_analysis.ipynb
├── src/
│   ├── config.py                     # Paths, constants, seeds, bounding box
│   ├── data_validation.py            # Loading and schema audit
│   ├── cleaning.py                   # Flags, derived fields, cleaning log
│   ├── statistics.py                 # Descriptive statistics and tests
│   ├── geospatial.py                 # Projection, spatial weights, Moran's I
│   ├── visualizations.py             # Charts and maps
│   └── reporting.py                  # Markdown report generation
├── outputs/
│   ├── figures/                      # Saved figures at 300 dpi
│   ├── tables/                       # CSV tables
│   └── reports/                      # Markdown report
├── tests/
│   └── test_analysis.py
├── requirements.txt
├── PROJECT_SCOPE.md
├── REQUIREMENTS.md
├── METHODOLOGY.md
└── README.md
```

## Reproducing the analysis

### Local environment

```bash
git clone <repository-url>
cd <repository-name>
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
jupyter lab notebooks/01_exploratory_geospatial_analysis.ipynb
```

Run the notebook from the project root or from `notebooks/`. The input defaults to `data/raw/bali_tourist_destination.csv`.

Set these environment variables if the project folder or CSV is in another location:

```bash
export BALI_PROJECT_ROOT="/path/to/project"
export BALI_INPUT_CSV="/path/to/project/data/raw/bali_tourist_destination.csv"
```

### Google Colab

Upload or clone the project folder, then set the same two environment variables before running the notebook. The notebook uses the same code locally and in Colab.

### Tests

```bash
python -m pytest -q
```

The tests cover file loading, schema checks, missing-column handling, cleaning flags, Spearman correlation, coordinate projection, and Moran's I on synthetic clustered data.

## Outputs

### Processed data

- `data/processed/analysis_ready.csv`: all 1,452 source records with flags and derived fields.
- `data/processed/flagged_coordinate_records.csv`: records outside the broad Bali bounding box.
- `data/processed/likely_duplicate_records.csv`: records matching on name, coordinates, rating, and count.
- `data/processed/name_duplicate_candidates.csv`: case-insensitive name groups for manual review.
- `data/processed/coincident_coordinate_records.csv`: records sharing a coordinate.
- `data/processed/invalid_numeric_records.csv`: unparseable numeric values, if any.

### Tables

`outputs/tables/` contains:

- schema, missingness, duplicate, and cleaning audit tables
- category, regency, and subdistrict counts
- descriptive summaries and group summaries
- rating-popularity association and alternative correlation measures
- Kruskal-Wallis and Dunn post-hoc results
- spatial feasibility, Moran's I, aggregated-coordinate, and largest-component results
- robustness specifications
- environment versions

### Figures

`outputs/figures/` contains:

- `01_category_counts.png`
- `02_regency_counts.png`
- `03_rating_distribution.png`
- `04_rating_count_distribution.png`
- `05_rating_vs_count.png`
- `06_group_distributions.png`
- `07_map_destinations.png`
- `08_map_attributes.png`

### Report

`outputs/reports/analysis_report.md` contains the methods, results, limitations, and reproducibility notes generated from the executed analysis.

## Limitations

- The dataset is cross-sectional and has no documented extraction date in the supplied file, so no temporal or trend claims are made.
- `jumlah_rating` is the number of Google ratings or reviews, not the number of visitors, arrivals, or spending.
- `rating` is an observed platform score. It may reflect rounding, ceiling effects, and platform-specific review behaviour.
- The dataset has no validated sampling frame. It cannot be assumed to represent every destination in Bali.
- Seven records have coordinates outside the broad Bali bounding box and are excluded only from mapping and spatial analysis.
- Coordinates inside the broad box were not validated against official regency boundaries. Some records may have plausible coordinates with inconsistent region labels.
- Repeated names and matching records are retained in the primary analysis because names alone are not proof of duplication.
- Global Moran's I measures global spatial autocorrelation. It does not identify local hotspots.
- The spatial weights depend on the choice of k and do not connect the Nusa Penida and Lembongan records to the mainland at k = 8 or k = 12.
- Group comparisons are unadjusted for category composition, access, promotion, destination age, and other unobserved factors.
- A large sample can make a small association statistically significant. The reported effect sizes and confidence intervals should guide interpretation more than p-values alone.

## Data availability and licensing

The source CSV was supplied for this project. Its extraction date, collection method, and redistribution rights are not documented in the file. Before making this repository public, confirm that you have permission to publish the dataset. If you do not, remove the CSV files from the repository and provide a data access statement instead.

The code and report are separate from the dataset. The dataset may have terms that differ from the code license.

## Citation and license

Citation details have not been finalized. Add author names, year, title, repository URL, and a DOI or archive link before publishing.

No license has been selected for this repository yet. Add a license before distributing or reusing the code. If you use an open license, include a `LICENSE` file and update this section.

## Acknowledgements

The analysis was developed with assistance from the OpenCode coding agent. The research scope, methodology, and interpretation limits are documented in `PROJECT_SCOPE.md`, `REQUIREMENTS.md`, and `METHODOLOGY.md`.
