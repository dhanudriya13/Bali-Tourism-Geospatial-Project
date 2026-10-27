# Research Methodology and Analysis Plan

## 1. Design

Use a quantitative, observational, cross-sectional design based on secondary data. The primary analysis is descriptive and associational. Spatial inferential analysis is conditional on data quality and methodological feasibility.

## 2. Variables

### Main variables
- `rating`: platform-provided Google rating, expected range 0–5.
- `jumlah_rating`: count of Google ratings/reviews.
- `latitude`, `longitude`: coordinates for mapping.
- `kategori`: destination category.
- `kabupaten_kota`: regency/city.
- `kecamatan`: subdistrict.

Verify field definitions against the dataset documentation or source before final publication. If no source date or extraction date is available, report that limitation.

### Operational definition of popularity
In this project, “online popularity” means **the number of Google ratings recorded in the supplied dataset**. It is a proxy for online review engagement, not a direct measure of tourist arrivals, visitation, or total popularity.

## 3. Workflow

### Stage A — Data audit
1. Load the CSV and inspect its actual schema.
2. Check dimensions, data types, missing values, and numeric ranges.
3. Count exact duplicate rows and repeated identifiers.
4. Generate a separate file of possible name duplicates for inspection.
5. Check coordinates for global validity and approximate Bali-region plausibility.
6. Record data issues and decisions in a cleaning log.

### Stage B — Cleaning
1. Preserve the original source file.
2. Normalize obvious whitespace and missing-value encodings.
3. Convert rating, rating count, latitude, and longitude to numeric values, preserving unparseable values in an audit output.
4. Flag invalid values; do not automatically discard every flagged record.
5. Create analysis-specific subsets and report their sample sizes.
6. Retain records with valid coordinates for geographic counts even if ratings are missing.
7. Do not deduplicate by destination name alone.

### Stage C — Exploratory data analysis
Produce:
- Counts by category, regency/city, and subdistrict.
- Rating and rating-count summaries, including median and IQR.
- Histograms or distribution plots.
- Box/violin plots for relevant category and regional comparisons.
- A scatter plot of rating versus rating count with a logarithmic count axis.
- A missingness and exclusion summary.

### Stage D — Rating–popularity association
Primary analysis:
1. Define the eligible sample as records with valid rating and valid positive rating count; explain any treatment of zero rating counts.
2. Calculate Spearman's rank correlation between rating and `jumlah_rating`.
3. Report Spearman's rho, N, p-value, and a confidence interval if implemented with a defensible method such as bootstrap resampling.
4. Visualize the relationship using a log y-axis or log-transformed count.
5. Inspect the distribution and consider ties, which are likely for ratings rounded to one decimal place.
6. Avoid causal wording.

Interpretation template:
“Among records meeting the stated inclusion criteria, rating and rating-count values showed [direction and strength] of rank association (Spearman's rho = ..., N = ..., p = ...). This describes an association in the supplied dataset and does not establish that ratings cause review engagement.”

Do not fill placeholders until code has produced verified results.

### Stage E — Geographic description
1. Map valid destination coordinates.
2. Use marker colour or size to represent a clearly defined attribute, with legends and sensible scaling.
3. Summarize record counts by regency/city.
4. If a choropleth is desired, obtain a suitable administrative-boundary dataset from a documented, permitted source. Do not fabricate boundaries or join regions using unverified labels.
5. Clearly distinguish point distribution, administrative summaries, and statistical hotspot results.

### Stage F — Optional spatial autocorrelation
Only proceed if coordinate validity, duplicate/coincident points, and spatial weights can be handled defensibly.

Possible exploratory method:
- Global Moran's I on a selected variable such as rating or log-transformed rating count.
- Use a documented spatial weights approach, such as k-nearest neighbours, with a justified choice of k and a sensitivity check.
- Use permutation-based inference when supported.
- Explain the implications of using point-level records, repeated/coincident locations, and unequal spatial sampling density.
- Report the weights specification and the number of observations used.

Important: Moran's I measures global spatial autocorrelation; it does not identify local hotspots by itself. Local indicators or Getis-Ord Gi* require separate methods and interpretation. Do not run spatial statistics solely to make the paper appear more advanced.

### Stage G — Robustness checks
Where feasible:
- Compare results after excluding clearly invalid coordinates or ratings.
- Check sensitivity to repeated/coincident coordinates.
- Compare Spearman correlation with an alternative specification only if justified.
- For spatial autocorrelation, compare a small number of reasonable spatial weights settings.
- Report whether conclusions change materially.

### Stage H — Reporting
Report:
- Data source and provenance, including collection/extraction date if known.
- Inclusion/exclusion rules.
- Final sample sizes for every analysis.
- Descriptive statistics and figures.
- Test names, statistics, p-values, confidence intervals/effect sizes where feasible.
- Limitations and plausible alternative explanations.
- Code and dependency details for reproducibility.

## 4. Statistical cautions

- A very large sample can make small associations statistically significant; discuss magnitude and uncertainty, not only p-values.
- Google ratings are bounded and may have ceiling effects.
- Review counts are typically right-skewed; medians and logarithmic visualizations are useful.
- Rating counts may reflect destination age, visibility, access, promotion, or platform usage, none of which are necessarily observed.
- Regional comparisons may be confounded by differences in category composition and dataset coverage.
- Spatial patterns can be affected by uneven sampling, duplicate coordinates, and the choice of spatial weights.
- Avoid overinterpreting subgroup analyses or testing many hypotheses without appropriate correction.
- Do not infer causality, time trends, or actual visitor numbers from these variables.

## 5. Suggested paper structure

1. Introduction
2. Related Work
3. Data and Methods
4. Results
   - Data quality and dataset profile
   - Geographic distribution
   - Rating and rating-count distributions
   - Rating–popularity association
   - Optional spatial autocorrelation
5. Discussion
6. Limitations
7. Conclusion
8. Data/code availability statement, as appropriate
