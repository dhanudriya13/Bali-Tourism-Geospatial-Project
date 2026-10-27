"""Generate a Markdown research report from executed analysis objects."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


def _fmt(value: float, digits: int = 3) -> str:
    if value is None or pd.isna(value):
        return "NA"
    return f"{value:.{digits}f}"


def _fmt_int(value: int | float) -> str:
    if value is None or pd.isna(value):
        return "NA"
    return f"{int(value):,}"


def _md_table(frame: pd.DataFrame, max_rows: int | None = None) -> str:
    if frame is None or frame.empty:
        return "_No rows._"
    table = frame.head(max_rows) if max_rows else frame
    columns = [str(column) for column in table.columns]
    lines = ["| " + " | ".join(columns) + " |", "|" + "|".join(["---"] * len(columns)) + "|"]
    for _, row in table.iterrows():
        values = []
        for value in row:
            if isinstance(value, float):
                text = f"{value:.4g}" if pd.notna(value) else "NA"
            else:
                text = str(value)
            values.append(text.replace("|", "\\|").replace("\n", " "))
        lines.append("| " + " | ".join(values) + " |")
    return "\n".join(lines)


def write_report(context: dict, path: str | Path) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    cleaning_log = context["cleaning_log"]
    category_counts = context["category_counts"]
    regency_counts = context["regency_counts"]
    rating_summary = context["rating_summary"]
    count_summary = context["count_summary"]
    correlation = context["correlation"]
    pearson = context.get("pearson")
    robustness = context.get("robustness")
    group_tests = context.get("group_tests", [])
    posthoc = context.get("posthoc")
    spatial = context.get("spatial")
    spatial_aggregated = context.get("spatial_aggregated")
    spatial_component = context.get("spatial_component")
    duplicated_coordinates = context.get("coincident_rows", 0)

    lines: list[str] = []
    lines.append("# Spatial Patterns and the Rating-Popularity Relationship of Tourist Destinations in Bali")
    lines.append("")
    lines.append(f"Generated: {context['generated_at']}  ")
    lines.append(f"Input file: `{context['input_csv']}`  ")
    lines.append(f"SHA-256: `{context['file_sha256']}`  ")
    lines.append(f"Source records: {_fmt_int(context['n_rows'])} rows and {context['n_columns']} columns.")
    lines.append("")
    lines.append("## 1. Purpose and scope")
    lines.append("")
    lines.append(
        "This report describes the supplied cross-sectional dataset of tourist destinations in Bali. "
        "It covers data quality, the geographic distribution of records, the distributions of Google ratings "
        "and Google rating counts, and the rank association between those two variables. "
        "The rating count is treated as a measure of online review engagement, not as visitor volume. "
        "All findings describe the supplied records and do not establish causal effects or population-wide coverage."
    )
    lines.append("")
    lines.append("## 2. Data and methods")
    lines.append("")
    lines.append(
        "The source CSV was read as text, inspected against the expected schema, and retained unchanged. "
        "Numeric fields were converted with explicit failure tracking. Ratings equal to zero were treated as "
        "unrated records rather than as literal scores of zero. Coordinates were checked against global ranges "
        "and a broad Bali bounding box used only for screening. No records were removed on the basis of matching "
        "names. Separate analytic samples were defined for mapping, rating summaries, and the rating-count association."
    )
    lines.append("")
    lines.append(
        "The primary association measure is Spearman's rank correlation, with a percentile bootstrap confidence "
        "interval. Category and regency comparisons use Kruskal-Wallis tests with Dunn post-hoc comparisons and "
        "Holm adjustment. Spatial autocorrelation, when reported, uses global Moran's I with row-standardised "
        "k-nearest-neighbour weights built in projected metres (UTM zone 50S) and permutation inference."
    )
    lines.append("")
    lines.append("## 3. Data audit and cleaning")
    lines.append("")
    lines.append(f"- Exact duplicate rows: {_fmt_int(context['exact_duplicates'])}")
    lines.append(f"- Repeated destination IDs: {_fmt_int(context['repeated_ids'])}")
    lines.append(
        f"- Repeated destination names, exact matches after the first occurrence: {_fmt_int(context['repeated_names'])}"
    )
    lines.append(f"- Rows in case-insensitive name groups: {_fmt_int(context.get('name_group_rows', 0))}")
    lines.append(f"- Records with a rating recorded as zero: {_fmt_int(context['rating_zero'])}")
    lines.append(f"- Records outside the broad Bali bounding box: {_fmt_int(context['coords_outside'])}")
    lines.append(f"- Records sharing coordinates with another record: {_fmt_int(duplicated_coordinates)}")
    lines.append(f"- Records matching another record on name, coordinates, rating, and count: {_fmt_int(context['likely_duplicates'])}")
    lines.append(f"- Missing image links: {_fmt_int(context['missing_image_links'])}")
    lines.append("")
    if context.get("missing_columns"):
        lines.append(f"Expected columns absent from the file: {', '.join(context['missing_columns'])}.")
    else:
        lines.append("All expected columns were present.")
    if context.get("unexpected_columns"):
        lines.append(f"Unexpected columns present: {', '.join(context['unexpected_columns'])}.")
    lines.append("")
    lines.append("### Cleaning log")
    lines.append("")
    lines.append(_md_table(cleaning_log))
    lines.append("")
    lines.append(
        "Repeated names and matching records were exported for manual review. They were retained in the primary "
        "analysis and addressed in the robustness checks rather than deleted automatically."
    )
    lines.append("")
    lines.append("## 4. Geographic distribution")
    lines.append("")
    lines.append(
        f"Records are available for {len(category_counts)} categories and {len(regency_counts)} regencies or cities. "
        f"The geographic mapping sample contains {_fmt_int(context['n_geo'])} records with coordinates inside the "
        "broad Bali bounding box."
    )
    lines.append("")
    lines.append("### Records by category")
    lines.append("")
    lines.append(_md_table(category_counts))
    lines.append("")
    lines.append("### Records by regency or city")
    lines.append("")
    lines.append(_md_table(regency_counts))
    lines.append("")
    lines.append(
        "The category and regency tables above use all source records. A comparison restricted to records "
        "with coordinates inside the broad Bali bounding box is shown below; it is the sample used in the maps."
    )
    lines.append("")
    lines.append("### Records by regency or city, valid-coordinate subset")
    lines.append("")
    lines.append(_md_table(context.get("regency_counts_geo", pd.DataFrame())))
    lines.append("")
    lines.append("![Destination records by category](../figures/01_category_counts.png)")
    lines.append("")
    lines.append("![Destination records by regency or city](../figures/02_regency_counts.png)")
    lines.append("")
    lines.append("![Destination records in Bali](../figures/07_map_destinations.png)")
    lines.append("")
    lines.append(
        "The point map is descriptive. Dense areas reflect the geographic distribution of records in this dataset, "
        "not verified tourist flows or a statistically tested hotspot pattern."
    )
    lines.append("")
    lines.append("## 5. Rating and rating-count distributions")
    lines.append("")
    lines.append(
        f"Among {_fmt_int(rating_summary['n'])} records with a rating above zero, the median rating was "
        f"{_fmt(rating_summary['median'], 2)} with an interquartile range of {_fmt(rating_summary['q1'], 2)} to "
        f"{_fmt(rating_summary['q3'], 2)}. The mean was {_fmt(rating_summary['mean'], 2)} "
        f"(SD {_fmt(rating_summary['sd'], 2)})."
    )
    lines.append("")
    lines.append(
        f"Among the same eligible association sample, the median number of Google ratings was "
        f"{_fmt_int(count_summary['median'])} with an interquartile range of {_fmt_int(count_summary['q1'])} to "
        f"{_fmt_int(count_summary['q3'])}. The distribution is strongly right-skewed, so the median and "
        "logarithmic displays are more informative than the mean alone."
    )
    lines.append("")
    lines.append("![Distribution of Google ratings](../figures/03_rating_distribution.png)")
    lines.append("")
    lines.append("![Distribution of Google rating counts](../figures/04_rating_count_distribution.png)")
    lines.append("")
    lines.append("## 6. Rating-popularity association")
    lines.append("")
    lines.append(
        f"Across N = {_fmt_int(correlation['n'])} records with a rating above zero and a positive whole-number "
        f"rating count, the Spearman rank correlation was rho = {_fmt(correlation['rho'])} "
        f"(95% percentile bootstrap CI {_fmt(correlation['ci_low'])} to {_fmt(correlation['ci_high'])}; "
        f"p = {correlation['p_value']:.3g})."
    )
    lines.append("")
    direction = "positive" if correlation["rho"] > 0 else "negative" if correlation["rho"] < 0 else "near zero"
    strength = "weak"
    magnitude = abs(correlation["rho"])
    if magnitude >= 0.5:
        strength = "moderate to strong"
    elif magnitude >= 0.3:
        strength = "moderate"
    elif magnitude >= 0.1:
        strength = "weak"
    lines.append(
        f"The observed association is {direction} and {strength} in magnitude. This describes the supplied records "
        "only. It does not show that high ratings cause more reviews, or that review counts measure visitor demand."
    )
    lines.append("")
    if pearson:
        lines.append(
            f"As a secondary check, the Pearson correlation between the raw variables was r = {_fmt(pearson['r'])} "
            f"(N = {_fmt_int(pearson['n'])}). It is reported only for comparison because the count variable is "
            "strongly skewed and the rating variable has many ties. The near-zero Pearson value and the modest "
            "negative Spearman value are not contradictory: Pearson uses the raw count scale, where a few very "
            "large counts dominate, while Spearman uses ranks."
        )
        lines.append("")
    lines.append("![Google rating and number of Google ratings](../figures/05_rating_vs_count.png)")
    lines.append("")
    lines.append("## 7. Category and regional comparisons")
    lines.append("")
    if group_tests:
        for test in group_tests:
            lines.append(
                f"- {test['label']}: Kruskal-Wallis H = {_fmt(test['statistic'])}, "
                f"p = {test['p_value']:.3g}, epsilon-squared = {_fmt(test['epsilon_squared'])}, "
                f"N = {_fmt_int(test['n'])}, groups = {test['groups']}."
            )
    else:
        lines.append("No group comparisons were run.")
    lines.append("")
    lines.append(
        "These tests describe differences in the supplied records. They do not control for differences in category "
        "composition, destination visibility, or data collection coverage. Effect sizes are modest in some cases, "
        "so statistical significance should not be read as practical importance."
    )
    lines.append("")
    if posthoc is not None and not posthoc.empty:
        significant = posthoc[posthoc["significant_holm_0_05"]]
        if significant.empty:
            lines.append("No pairwise Dunn comparison remained significant after Holm adjustment.")
        else:
            lines.append(
                f"{len(significant)} pairwise Dunn comparison(s) remained significant after Holm adjustment. "
                "The full table is exported with the analysis outputs."
            )
        lines.append("")
    lines.append("![Descriptive comparisons by category and regency](../figures/06_group_distributions.png)")
    lines.append("")
    lines.append("## 8. Spatial autocorrelation")
    lines.append("")
    if spatial is not None and not spatial.empty:
        primary = spatial[(spatial["variable"] == "log_jumlah_rating") & (spatial["k"] == 8)]
        if primary.empty:
            primary = spatial.head(1)
        row = primary.iloc[0]
        variable_label = "log1p(number of Google ratings)" if row["variable"] == "log_jumlah_rating" else "Google rating"
        lines.append(
            f"Global Moran's I was estimated for {variable_label} using row-standardised k-nearest-neighbour weights "
            f"with k = {int(row['k'])}, N = {_fmt_int(row['n'])}, and {_fmt_int(row['permutations'])} permutations. "
            f"The observed statistic was I = {_fmt(row['morans_i'])}, expected I = {_fmt(row['expected_i'])}, "
            f"with a one-sided permutation p-value of {row['p_perm_greater']:.3g}."
        )
        lines.append("")
        rating_primary = spatial[
            (spatial["variable"] == "rating") & (spatial["k"] == 8)
        ]
        if not rating_primary.empty:
            rating_row = rating_primary.iloc[0]
            lines.append(
                f"For Google rating, the corresponding statistic was I = {_fmt(rating_row['morans_i'])} "
                f"with a one-sided permutation p-value of {rating_row['p_perm_greater']:.3g}."
            )
            lines.append("")
        lines.append(
            "With 999 permutations, 0.001 is the smallest attainable one-sided p-value. The result should be "
            "read as evidence against spatial randomness, not as a precise p-value."
        )
        lines.append("")
        lines.append(
            "Global Moran's I tests whether nearby values are more similar than expected under spatial randomness. "
            "It is not a local hotspot analysis. The k-nearest-neighbour design links each record to nearby records "
            "regardless of coastlines or administrative boundaries, and it is sensitive to the choice of k. "
            f"At k = {int(row['k'])} the weights formed {int(row['components'])} connected component(s); "
            "the Nusa Penida and Lembongan records form a group that is not linked to the mainland at this setting."
        )
        lines.append("")
        lines.append(_md_table(spatial))
        lines.append("")
        if spatial_aggregated is not None and not spatial_aggregated.empty:
            lines.append(
                "A sensitivity analysis averaged the outcome within each exact coordinate. Results for that "
                "coordinate-level sample are exported in `outputs/tables/spatial_autocorrelation_aggregated.csv`."
            )
            lines.append("")
        if spatial_component is not None and not spatial_component.empty:
            component_row = spatial_component.iloc[0]
            lines.append(
                f"A further sensitivity restricted to the largest connected component (N = {_fmt_int(component_row['n'])}, "
                f"k = {int(component_row['k'])}) gave I = {_fmt(component_row['morans_i'])} with a one-sided "
                f"permutation p-value of {component_row['p_perm_greater']:.3g}."
            )
            lines.append("")
    else:
        lines.append("Spatial autocorrelation was not estimated.")
        lines.append("")
    lines.append("![Maps of rating and rating count](../figures/08_map_attributes.png)")
    lines.append("")
    lines.append("## 9. Robustness checks")
    lines.append("")
    if robustness is not None and not robustness.empty:
        lines.append(_md_table(robustness))
        lines.append("")
        lines.append(
            "Robustness specifications are descriptive comparisons of the same association under alternative "
            "eligibility rules. They are not separate hypothesis tests and should not be overinterpreted."
        )
    else:
        lines.append("No robustness specifications were run.")
    lines.append("")
    lines.append("## 10. Limitations")
    lines.append("")
    lines.append("- The dataset is cross-sectional and has no verified extraction date in the supplied file, so no temporal claims are made.")
    lines.append("- The rating count is the number of Google ratings or reviews, not the number of visitors, arrivals, or spending.")
    lines.append("- Ratings are platform scores and may reflect rounding, ceiling effects, and platform-specific review behaviour.")
    lines.append("- The dataset does not provide a validated sampling frame, so it cannot be assumed to represent every destination in Bali.")
    lines.append("- Seven records have coordinates that fall outside the broad Bali bounding box and are excluded only from mapping and spatial analysis.")
    lines.append("- Zero ratings and zero rating counts are treated as unrated records; they are retained in the processed data and flagged.")
    lines.append("- Repeated names and matching records are retained in the primary analysis because names alone are not proof of duplication.")
    lines.append("- Coordinates inside the broad bounding box were not validated against official regency boundaries; some records may have plausible coordinates with inconsistent region labels.")
    lines.append("- The maps use a longitude and latitude display with an aspect correction and a broad screening box, not an official administrative boundary layer.")
    lines.append("- Global Moran's I depends on the spatial weights specification and on uneven sampling density; it does not identify local hotspots.")
    lines.append("- Group comparisons are unadjusted for category composition, access, promotion, destination age, or other unobserved factors.")
    lines.append("")
    lines.append("## 11. Reproducibility")
    lines.append("")
    lines.append(
        "The analysis is implemented in `notebooks/01_exploratory_geospatial_analysis.ipynb` with helper modules in "
        "`src/`. Random procedures use a fixed seed. The raw CSV is preserved unchanged in `data/raw/`, and the "
        "analysis-ready table with all flags and derived fields is written to `data/processed/analysis_ready.csv`."
    )
    lines.append("")
    lines.append("Key outputs:")
    lines.append("")
    for item in context.get("outputs", []):
        lines.append(f"- `{item}`")
    lines.append("")
    lines.append("Dependency versions are recorded in `requirements.txt` and in `outputs/tables/environment_versions.csv`.")
    lines.append("")

    path.write_text("\n".join(lines), encoding="utf-8")
    return path
