# Project Requirements

## 1. Functional requirements

### FR-01 — Load input data
The workflow must load the source CSV from a configurable path. It must not assume a fixed machine-specific path. For Google Colab, document how to upload the CSV or mount Google Drive.

**Acceptance criteria**
- The source file path can be changed in one configuration cell or configuration file.
- A clear error message is shown if the file cannot be found.
- The original input is not overwritten.

### FR-02 — Inspect the schema
The workflow must report row/column counts, column names, data types, missing values, duplicate rows, and descriptive statistics.

**Acceptance criteria**
- A data-audit table is exported.
- Unexpected or absent expected columns produce a useful warning or error.

### FR-03 — Validate fields
Expected fields, based on the currently understood schema:
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

The implementation must verify the actual CSV header before relying on this list. Do not silently rename or discard columns.

Validation checks:
- Ratings should ordinarily be within 0–5; flag out-of-range values for inspection.
- Rating counts should be non-negative numeric values; flag invalid or fractional values for inspection.
- Latitude must be between -90 and 90; longitude must be between -180 and 180.
- Bali-specific coordinates should be checked against a documented approximate bounding box or map, with flagged records reviewed rather than automatically deleted.
- Trim leading/trailing whitespace in text fields where safe.
- Standardize missing-value representations without converting valid labels into nulls.

### FR-04 — Handle duplicates transparently
Check exact duplicate rows, repeated IDs, and repeated destination names. Repeated names are not sufficient by themselves to prove duplication.

**Acceptance criteria**
- Exact duplicate rows and repeated IDs are reported separately.
- Name-based potential duplicates are exported for manual review.
- No potentially distinct destinations are removed solely because their names match.
- All exclusions are counted and documented.

### FR-05 — Create analysis-ready fields
Create derived fields only when their meaning is documented. Examples:
- `log_jumlah_rating = log1p(jumlah_rating)` for analysis/visualisation when the count is valid and non-negative.
- Cleaned category/region labels where a clear, documented normalization is possible.
- A record-validity flag for records excluded from specific analyses.

Do not overwrite raw variables; retain them or preserve a clean raw copy.

### FR-06 — Descriptive analysis
Generate:
- Counts by destination category, regency/city, and subdistrict.
- Rating summary statistics overall and by relevant groups.
- Rating-count summary statistics overall and by relevant groups.
- Missingness and exclusion summaries.

Use median and interquartile range alongside mean and standard deviation where distributions are skewed.

### FR-07 — Rating–popularity analysis
Use `rating` and `jumlah_rating` to estimate the association.

Minimum analysis:
- State the analytic sample size and exclusion criteria.
- Plot rating against rating count, using a logarithmic y-axis or a transformed count for legibility.
- Estimate Spearman's rho and its p-value.
- Report uncertainty where feasible; document the method used for confidence intervals.
- Include a plain-language interpretation that does not imply causation.

Optional:
- Compare Pearson correlation as a secondary analysis only if its assumptions and purpose are explained.
- Fit a regression model only if the research question and diagnostics justify it. Do not interpret a model coefficient as causal.

### FR-08 — Geographic visualization
Create:
- A static geographic scatter map of destination points, with a clear legend or sensible colour encoding.
- A map or chart summarizing destination-record counts by regency/city.
- At least one map showing a rating-related or rating-count-related attribute, if the coordinate quality supports it.
- Optionally, an interactive HTML map.

Map requirements:
- Use a suitable geographic projection for distance-based calculations.
- Do not use raw latitude/longitude Euclidean distances for inferential distance calculations without a justified local projection or geodesic approach.
- Include map scale/context, legend, and a note that locations represent records in the dataset.
- Avoid plotting personal or sensitive information; none is expected in this dataset.

### FR-09 — Spatial statistical analysis
Spatial inference is optional and gated by feasibility.

If Global Moran's I is implemented:
- Explain the outcome variable being tested.
- Explain the spatial weights matrix (e.g., k-nearest neighbours or distance-based weights) and why it is appropriate.
- Address islands, duplicate/coincident coordinates, disconnected components, and sensitivity to weights choices.
- Use permutation inference where supported.
- Report statistic, p-value, permutations, sample size, and weights specification.
- Do not describe a result as a hotspot analysis unless the chosen statistic actually tests local hotspots.
- If the dataset does not support a defensible test, omit the inferential claim and retain descriptive maps.

### FR-10 — Regional/category comparisons
Any inferential group comparison must:
- Check group sample sizes and distribution.
- Use an appropriate test (e.g., Kruskal–Wallis for suitable independent-group comparisons).
- Apply a suitable post-hoc procedure and multiple-comparison correction if follow-up tests are performed.
- Report effect sizes and uncertainty where feasible.
- Distinguish statistical significance from practical importance.

### FR-11 — Export outputs
Save results to configurable output folders:
- `outputs/tables/`
- `outputs/figures/`
- `outputs/reports/`
- `data/processed/`

Use informative, stable filenames and avoid overwriting the source CSV.

### FR-12 — Reproducibility
The notebook must include imports, configuration, data loading, validation, cleaning, analysis, visualisation, and exports in a clear sequence. Document package versions or dependencies.

## 2. Non-functional requirements

- **Reproducibility:** same input and environment should produce equivalent results.
- **Transparency:** every exclusion, transformation, and test must be explained.
- **Maintainability:** use clear function names, short functions, and modular code where useful.
- **Portability:** support Google Colab and, where practical, local Python execution.
- **Robustness:** handle missing values, unexpected columns, invalid numeric values, and empty analysis subsets gracefully.
- **Accessibility:** charts should use readable fonts, sufficient contrast, non-colour-only distinctions where practical, and descriptive labels.
- **Efficiency:** the workflow should run comfortably on a standard Colab CPU for a dataset of this size.
- **Research integrity:** do not fabricate values, results, data sources, or statistical significance.
- **Privacy/licensing:** do not scrape extra data or publish source data unless permissions and terms allow it.

## 3. Technical requirements

Suggested stack:
- Python 3
- pandas
- NumPy
- SciPy
- Matplotlib
- seaborn (optional)
- GeoPandas (optional, for vector/geospatial workflows)
- Folium (optional, for interactive maps)
- `libpysal` and `esda` (optional, only if a justified spatial-autocorrelation analysis is pursued)
- statsmodels (optional, for regression and statistical diagnostics)
- pytest (optional, for lightweight data-validation tests)

Use a small, documented dependency list. Do not install every optional package unless needed.

## 4. Data quality and decision rules

- Preserve the raw CSV unchanged.
- Do not silently drop records with missing ratings if they can still be used for geographic distribution counts.
- Create separate analytic subsets for each question, because each analysis may require different fields.
- Report denominators for every summary and test.
- Missing values are not equivalent to zero.
- A rating count of zero, if present, should be investigated; it may indicate a data-entry convention rather than a genuine zero-review destination.
- Do not infer a rating from the number of ratings or vice versa.
- Do not use imputation as a default solution for missing coordinates or ratings.
- Keep a cleaning log recording original row count, each rule applied, rows flagged, rows excluded, and final analytic sample sizes.

## 5. Acceptance checklist

- [ ] Source data are preserved unchanged.
- [ ] Schema is checked at runtime.
- [ ] Audit and cleaning log are generated.
- [ ] Duplicate candidates are reviewed rather than blindly removed.
- [ ] Invalid coordinates and ratings are flagged.
- [ ] Every figure is saved to disk and displayed in the notebook.
- [ ] Correlation analysis reports N, statistic, p-value, and interpretation.
- [ ] Spatial inference, if any, documents weights and assumptions.
- [ ] All tables and figures are reproducible.
- [ ] Conclusions are limited to what the data can support.
