# Project Scope

## 1. Project title

**Spatial Patterns and the Rating–Popularity Relationship of Tourist Destinations in Bali: A Geospatial Data Analysis**

## 2. Project overview

This project conducts a reproducible, cross-sectional analysis of a supplied dataset of tourist destinations in Bali. It combines data-quality assessment, exploratory statistics, geographic visualization, and statistical analysis to describe destination distribution and examine the relationship between Google ratings and the number of Google ratings.

The project is intended to support an academic research paper and to be implemented primarily in Python using Google Colab. Code should also be runnable locally where practical.

## 3. Research objectives

1. Assess the completeness, consistency, and suitability of the supplied dataset for geospatial and statistical analysis.
2. Describe how records in the dataset are distributed by regency/city, subdistrict, and destination category.
3. Characterize the distribution of Google ratings and rating counts.
4. Estimate the strength and direction of the association between ratings and rating counts.
5. Visualize geographic distributions and, where data and assumptions permit, investigate spatial clustering or spatial autocorrelation.
6. Produce reproducible tables, figures, and a concise report that transparently states limitations.

## 4. Research questions

- **RQ1 — Geographic distribution:** How are the tourist destinations represented in the dataset distributed across regencies/city and subdistricts?
- **RQ2 — Rating–popularity relationship:** What is the direction and strength of the association between Google rating and the number of Google ratings?
- **RQ3 — Geographic patterns:** Do rating values and rating counts show spatial concentration or spatial autocorrelation?
- **RQ4 — Robustness:** Do the main findings remain reasonably consistent after data-quality exclusions and alternative analytical choices?

RQ3 is conditional: spatial inferential tests should only be used if the data structure, coordinate quality, spatial weights, and sample size support them. If not, report descriptive mapping and explain why inferential spatial analysis was not performed.

## 5. Unit of analysis and study design

- **Unit of analysis:** one destination record after record-level validation and duplicate handling.
- **Study design:** observational, cross-sectional, secondary-data analysis.
- **Geographic scope:** Bali, Indonesia, as represented in the input dataset.
- **Platform scope:** Google Maps rating and rating-count fields as supplied in the dataset.
- **Environment:** Python, pandas, NumPy, SciPy, Matplotlib/Seaborn where appropriate, GeoPandas, and Folium or another suitable mapping library.

Do not claim that each row necessarily represents a unique, currently active destination until duplicates and record validity have been checked.

## 6. In scope

- Inspecting schema, data types, missingness, duplicate records, repeated names, and invalid values.
- Validating numeric rating/count fields and latitude/longitude ranges.
- Descriptive summaries by category, regency/city, and subdistrict.
- Distribution plots for ratings and rating counts.
- A log transformation such as `log1p(jumlah_rating)` for visualisation and suitable model diagnostics.
- Spearman rank correlation between rating and rating count, with sample size, p-value, and confidence interval if a defensible method is available.
- Regional/category comparisons as secondary analyses when sample sizes and assumptions are appropriate.
- Static maps and, optionally, an interactive point map.
- Optional spatial autocorrelation analysis, such as Global Moran's I, only after documenting spatial weights and assumptions.
- Sensitivity analyses for plausible cleaning decisions and analytical specifications.
- Exporting analysis-ready data, tables, figures, and a methods/results summary.
- Reproducible notebook and dependency documentation.

## 7. Out of scope

- Measuring actual tourist arrivals, visits, spending, or economic impact.
- Claiming that rating counts equal visitor counts or popularity in the full population.
- Causal claims about why destinations receive particular ratings or review counts.
- Forecasting future tourism demand or seasonal patterns without dated observations.
- Sentiment analysis of review text; review text is not included in the stated schema.
- Scraping Google Maps or bypassing platform restrictions.
- Building a production tourism recommendation application.
- Collecting surveys, interviews, or new primary data as a required project component.
- Claiming representative coverage of every destination in Bali without a validated sampling frame.
- Treating an ordinary point-density map as proof of statistically significant hotspots.

## 8. Primary deliverables

1. A documented data audit and cleaning log.
2. A reproducible Google Colab notebook.
3. Analysis-ready CSV output, with the raw file preserved unchanged.
4. Descriptive statistics tables.
5. Figures: category distribution, regional summaries, rating distribution, rating-count distribution, rating-versus-count plot, and geographic maps.
6. Statistical output for the rating–popularity relationship.
7. Spatial inferential output only if the analysis is justified and feasible.
8. A concise report containing methods, results, limitations, and recommendations for further work.
9. A `requirements.txt` file and instructions to reproduce the analysis.

## 9. Success criteria

The project is complete when:
- The notebook runs from start to finish in a fresh runtime after the input data is provided.
- All cleaning decisions are explicit and logged.
- All charts have readable titles, labels, units, legends where needed, and source/coverage notes.
- All reported statistics can be reproduced from code.
- The report distinguishes descriptive evidence, statistical association, and interpretation.
- No unsupported causal, temporal, or population-wide claims are made.
- Missing or unsuitable data are reported rather than silently fabricated or imputed without justification.
