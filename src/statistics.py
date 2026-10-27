"""Descriptive statistics and associational tests."""

from __future__ import annotations

from itertools import combinations

import numpy as np
import pandas as pd
from scipy import stats


def describe_series(values: pd.Series, label: str) -> dict:
    """Summarise a numeric variable, including robust measures for skewed data."""
    numeric = pd.to_numeric(values, errors="coerce").dropna()
    if numeric.empty:
        return {
            "variable": label,
            "n": 0,
            "missing": int(values.isna().sum()),
            "mean": np.nan,
            "sd": np.nan,
            "median": np.nan,
            "q1": np.nan,
            "q3": np.nan,
            "iqr": np.nan,
            "min": np.nan,
            "max": np.nan,
            "skewness": np.nan,
        }
    q1, q3 = numeric.quantile([0.25, 0.75])
    return {
        "variable": label,
        "n": int(numeric.size),
        "missing": int(values.isna().sum()),
        "mean": float(numeric.mean()),
        "sd": float(numeric.std(ddof=1)) if numeric.size > 1 else np.nan,
        "median": float(numeric.median()),
        "q1": float(q1),
        "q3": float(q3),
        "iqr": float(q3 - q1),
        "min": float(numeric.min()),
        "max": float(numeric.max()),
        "skewness": float(numeric.skew()) if numeric.size > 2 else np.nan,
    }


def descriptive_table(frame: pd.DataFrame, columns: dict[str, str]) -> pd.DataFrame:
    rows = [describe_series(frame[column], label) for column, label in columns.items()]
    return pd.DataFrame(rows)


def group_summary(
    frame: pd.DataFrame,
    group_column: str,
    value_column: str,
    min_group_n: int = 1,
) -> pd.DataFrame:
    rows = []
    for group, subset in frame.groupby(group_column, dropna=False):
        values = pd.to_numeric(subset[value_column], errors="coerce").dropna()
        if len(values) < min_group_n:
            continue
        rows.append(
            {
                "group": group,
                "n": int(values.size),
                "mean": float(values.mean()),
                "sd": float(values.std(ddof=1)) if len(values) > 1 else np.nan,
                "median": float(values.median()),
                "q1": float(values.quantile(0.25)),
                "q3": float(values.quantile(0.75)),
                "iqr": float(values.quantile(0.75) - values.quantile(0.25)),
                "min": float(values.min()),
                "max": float(values.max()),
            }
        )
    return pd.DataFrame(rows).sort_values("n", ascending=False).reset_index(drop=True)


def spearman_association(
    frame: pd.DataFrame,
    x_column: str,
    y_column: str,
    n_bootstrap: int = 2000,
    seed: int = 20261027,
) -> dict:
    """Estimate Spearman's rho with a percentile bootstrap confidence interval."""
    subset = frame[[x_column, y_column]].apply(pd.to_numeric, errors="coerce").dropna()
    n = len(subset)
    if n < 3:
        raise ValueError("At least three complete pairs are required for Spearman's correlation.")
    x = subset[x_column].to_numpy()
    y = subset[y_column].to_numpy()
    rho, p_value = stats.spearmanr(x, y)

    rng = np.random.default_rng(seed)
    boot = np.empty(n_bootstrap)
    boot[:] = np.nan
    for i in range(n_bootstrap):
        indices = rng.integers(0, n, n)
        if np.unique(x[indices]).size < 2 or np.unique(y[indices]).size < 2:
            continue
        boot[i] = stats.spearmanr(x[indices], y[indices]).statistic
    boot = boot[np.isfinite(boot)]
    if boot.size >= 50:
        ci_low, ci_high = np.percentile(boot, [2.5, 97.5])
    else:
        ci_low, ci_high = np.nan, np.nan

    return {
        "analysis": "Spearman rank correlation",
        "x": x_column,
        "y": y_column,
        "n": int(n),
        "rho": float(rho),
        "p_value": float(p_value),
        "ci_low": float(ci_low) if np.isfinite(ci_low) else np.nan,
        "ci_high": float(ci_high) if np.isfinite(ci_high) else np.nan,
        "bootstrap_replicates": int(boot.size),
        "bootstrap_requested": int(n_bootstrap),
        "unique_x": int(np.unique(x).size),
        "unique_y": int(np.unique(y).size),
        "ci_method": "Percentile bootstrap of paired records; seed set.",
    }


def holm_adjust(p_values: np.ndarray) -> np.ndarray:
    p_values = np.asarray(p_values, dtype=float)
    adjusted = np.full(p_values.shape, np.nan)
    finite = np.flatnonzero(np.isfinite(p_values))
    if finite.size == 0:
        return adjusted
    order = finite[np.argsort(p_values[finite])]
    m = order.size
    running = 0.0
    for rank, index in enumerate(order):
        value = min(1.0, (m - rank) * p_values[index])
        running = max(running, value)
        adjusted[index] = running
    return adjusted


def kruskal_wallis(frame: pd.DataFrame, group_column: str, value_column: str, min_group_n: int = 5) -> dict:
    """Kruskal-Wallis test with epsilon-squared effect size."""
    subset = frame[[group_column, value_column]].dropna()
    counts = subset[group_column].value_counts()
    eligible = counts[counts >= min_group_n].index
    subset = subset[subset[group_column].isin(eligible)]
    groups = [group[value_column].to_numpy() for _, group in subset.groupby(group_column)]
    if len(groups) < 2:
        raise ValueError("Fewer than two groups meet the minimum sample size.")
    result = stats.kruskal(*groups)
    n = len(subset)
    k = len(groups)
    epsilon_squared = (result.statistic - k + 1) / (n - k) if n > k else np.nan
    return {
        "analysis": "Kruskal-Wallis rank test",
        "group": group_column,
        "value": value_column,
        "n": int(n),
        "groups": int(k),
        "statistic": float(result.statistic),
        "p_value": float(result.pvalue),
        "epsilon_squared": float(max(0.0, epsilon_squared)) if np.isfinite(epsilon_squared) else np.nan,
        "min_group_n": int(min_group_n),
    }


def dunn_posthoc(frame: pd.DataFrame, group_column: str, value_column: str, min_group_n: int = 5) -> pd.DataFrame:
    """Pairwise Dunn test with tie correction and Holm adjustment."""
    subset = frame[[group_column, value_column]].dropna().copy()
    counts = subset[group_column].value_counts()
    eligible = counts[counts >= min_group_n].index
    subset = subset[subset[group_column].isin(eligible)]
    subset["_rank"] = stats.rankdata(subset[value_column].to_numpy())
    n = len(subset)
    if n < 3:
        return pd.DataFrame()

    tie_counts = subset[value_column].value_counts().to_numpy()
    tie_term = np.sum(tie_counts**3 - tie_counts)
    variance_base = (n * (n + 1) / 12) - tie_term / (12 * (n - 1))

    summaries = subset.groupby(group_column).agg(n=("_rank", "size"), mean_rank=("_rank", "mean"))
    rows = []
    for left, right in combinations(summaries.index, 2):
        n_left = summaries.loc[left, "n"]
        n_right = summaries.loc[right, "n"]
        denominator = np.sqrt(variance_base * (1 / n_left + 1 / n_right))
        z_value = (summaries.loc[left, "mean_rank"] - summaries.loc[right, "mean_rank"]) / denominator
        p_value = 2 * stats.norm.sf(abs(z_value))
        rows.append(
            {
                "group_a": left,
                "group_b": right,
                "n_a": int(n_left),
                "n_b": int(n_right),
                "z": float(z_value),
                "p_value": float(p_value),
            }
        )
    result = pd.DataFrame(rows)
    result["p_holm"] = holm_adjust(result["p_value"].to_numpy())
    result["significant_holm_0_05"] = result["p_holm"] < 0.05
    return result.sort_values("p_value").reset_index(drop=True)
