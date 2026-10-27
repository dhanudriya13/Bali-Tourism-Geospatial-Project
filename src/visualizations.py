"""Publication-oriented charts and descriptive maps."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.lines import Line2D
from matplotlib.patches import Patch

from . import config

TEXT_COLOR = "#222222"
GRID_COLOR = "#D9D9D4"
ACCENT = "#2A6F97"
MAP_XLIM = (114.35, 115.85)
MAP_YLIM = (-9.05, -8.05)
MEAN_LATITUDE = np.mean(MAP_YLIM)
SOURCE_NOTE = (
    "Source: supplied Bali tourist destination dataset (cross-sectional). "
    "Locations are records in the dataset, not verified visitor movements."
)


def apply_style() -> None:
    plt.rcParams.update(
        {
            "figure.facecolor": "#FCFCFA",
            "axes.facecolor": "#FCFCFA",
            "savefig.facecolor": "#FCFCFA",
            "axes.edgecolor": "#4A4A46",
            "axes.labelcolor": TEXT_COLOR,
            "axes.titlecolor": TEXT_COLOR,
            "text.color": TEXT_COLOR,
            "xtick.color": TEXT_COLOR,
            "ytick.color": TEXT_COLOR,
            "axes.grid": True,
            "grid.color": GRID_COLOR,
            "grid.linewidth": 0.6,
            "grid.alpha": 0.7,
            "axes.spines.top": False,
            "axes.spines.right": False,
            "font.family": "DejaVu Sans",
            "font.size": 10,
            "axes.titlesize": 13,
            "axes.titleweight": "bold",
            "axes.labelsize": 10,
            "legend.frameon": False,
        }
    )


def save_and_show(figure: plt.Figure, path: str | Path) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(path, dpi=300, bbox_inches="tight")
    plt.show()


def figure_note(figure: plt.Figure, note: str = SOURCE_NOTE, y: float = -0.01) -> None:
    figure.text(0.01, y, note, ha="left", va="top", fontsize=8, color="#555550")


def plot_category_counts(counts: pd.Series, path: str | Path) -> plt.Figure:
    counts = counts.reindex(config.CATEGORY_ORDER).fillna(0).astype(int)
    figure, axis = plt.subplots(figsize=(8, 4.8))
    bars = axis.bar(
        counts.index,
        counts.values,
        color=[config.CATEGORY_COLORS[category] for category in counts.index],
        width=0.68,
    )
    axis.set_title("Destination records by category")
    axis.set_xlabel("Destination category")
    axis.set_ylabel("Number of records")
    axis.set_ylim(0, counts.max() * 1.15)
    for bar, value in zip(bars, counts.values):
        axis.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + counts.max() * 0.02,
            f"{value:,}",
            ha="center",
            va="bottom",
            fontsize=9,
        )
    figure_note(figure, f"{SOURCE_NOTE} Total records = {counts.sum():,}.")
    figure.tight_layout()
    save_and_show(figure, path)


def plot_regency_counts(counts: pd.Series, path: str | Path) -> plt.Figure:
    ordered = counts.sort_values()
    figure, axis = plt.subplots(figsize=(8.6, 5.2))
    bars = axis.barh(ordered.index, ordered.values, color=ACCENT, height=0.66)
    axis.set_title("Destination records by regency or city")
    axis.set_xlabel("Number of records")
    axis.set_ylabel("")
    axis.set_xlim(0, ordered.max() * 1.16)
    axis.grid(axis="y", visible=False)
    for bar, value in zip(bars, ordered.values):
        axis.text(
            value + ordered.max() * 0.01,
            bar.get_y() + bar.get_height() / 2,
            f"{value:,}",
            va="center",
            fontsize=9,
        )
    figure_note(figure, f"{SOURCE_NOTE} Total records = {counts.sum():,}.")
    figure.tight_layout()
    save_and_show(figure, path)


def plot_rating_distribution(values: pd.Series, path: str | Path) -> plt.Figure:
    data = pd.to_numeric(values, errors="coerce").dropna()
    median = data.median()
    q1, q3 = data.quantile([0.25, 0.75])
    figure, axis = plt.subplots(figsize=(8.4, 4.8))
    bins = np.arange(0, 5.05, 0.1)
    axis.hist(data, bins=bins, color=ACCENT, edgecolor="white", linewidth=0.5)
    axis.axvline(median, color="#B4545B", linewidth=1.8, label=f"Median = {median:.2f}")
    axis.axvline(q1, color="#B4545B", linewidth=1, linestyle="--", label=f"IQR = {q1:.2f} to {q3:.2f}")
    axis.axvline(q3, color="#B4545B", linewidth=1, linestyle="--")
    axis.set_title("Distribution of Google ratings")
    axis.set_xlabel("Google rating (0 to 5 scale)")
    axis.set_ylabel("Number of records")
    axis.set_xlim(0, 5.05)
    axis.legend(loc="upper left")
    figure_note(
        figure,
        f"Records with a rating above zero and at most 5. N = {len(data):,}. "
        "Zero values are treated as unrated and excluded.",
    )
    figure.tight_layout()
    save_and_show(figure, path)


def plot_count_distribution(values: pd.Series, path: str | Path) -> plt.Figure:
    data = pd.to_numeric(values, errors="coerce").dropna()
    logged = np.log1p(data)
    median = data.median()
    figure, axis = plt.subplots(figsize=(8.4, 4.8))
    axis.hist(logged, bins=32, color="#5F7A52", edgecolor="white", linewidth=0.5)
    axis.axvline(np.log1p(median), color="#B4545B", linewidth=1.8, label=f"Median = {median:,.0f}")
    axis.set_title("Distribution of Google rating counts")
    axis.set_xlabel("log1p(number of Google ratings); 0 on this scale means 0 ratings")
    axis.set_ylabel("Number of records")
    axis.legend(loc="upper right")
    figure_note(
        figure,
        f"Valid non-negative rating counts, N = {len(data):,}. "
        "The log1p scale compresses the long right tail; it is not a count of visitors.",
    )
    figure.tight_layout()
    save_and_show(figure, path)


def plot_rating_vs_count(
    frame: pd.DataFrame,
    correlation: dict,
    path: str | Path,
) -> plt.Figure:
    data = frame.dropna(subset=["rating", "jumlah_rating"]).copy()
    rng = np.random.default_rng(config.RANDOM_SEED)
    data["rating_jitter"] = data["rating"] + rng.uniform(-0.025, 0.025, len(data))
    figure, axis = plt.subplots(figsize=(8.6, 5.4))
    axis.scatter(
        data["rating_jitter"],
        data["jumlah_rating"],
        s=15,
        alpha=0.38,
        color=ACCENT,
        edgecolor="none",
    )
    axis.set_yscale("log")
    axis.set_title("Google rating and number of Google ratings")
    axis.set_xlabel("Google rating (slight horizontal jitter for visibility)")
    axis.set_ylabel("Number of Google ratings (log scale)")
    axis.set_xlim(1.8, 5.1)
    annotation = (
        f"Spearman rho = {correlation['rho']:.3f}\n"
        f"95% bootstrap CI = {correlation['ci_low']:.3f} to {correlation['ci_high']:.3f}\n"
        f"N = {correlation['n']:,}, p = {correlation['p_value']:.2e}"
    )
    axis.text(
        0.02,
        0.97,
        annotation,
        transform=axis.transAxes,
        ha="left",
        va="top",
        fontsize=9,
        bbox={"boxstyle": "round,pad=0.45", "facecolor": "white", "edgecolor": GRID_COLOR},
    )
    figure_note(
        figure,
        "Records with a rating above zero and a positive whole-number rating count. "
        "The association is descriptive and does not imply causation.",
    )
    figure.tight_layout()
    save_and_show(figure, path)


def plot_group_distributions(frame: pd.DataFrame, path: str | Path) -> plt.Figure:
    rating_data = frame[frame["analytic_rating"]].copy()
    count_data = frame[frame["analytic_popularity"]].copy()
    count_data["log_count"] = np.log1p(count_data["jumlah_rating"])

    figure, axes = plt.subplots(2, 2, figsize=(14, 10))
    category_positions = np.arange(len(config.CATEGORY_ORDER))
    category_colors = [config.CATEGORY_COLORS[category] for category in config.CATEGORY_ORDER]

    rating_by_category = [
        rating_data.loc[rating_data["kategori"] == category, "rating"].dropna().to_numpy()
        for category in config.CATEGORY_ORDER
    ]
    axes[0, 0].boxplot(
        rating_by_category,
        positions=category_positions,
        patch_artist=True,
        widths=0.55,
        boxprops={"facecolor": "#E8EEF2", "edgecolor": "#4A4A46"},
        medianprops={"color": "#B4545B", "linewidth": 1.6},
        whiskerprops={"color": "#4A4A46"},
        capprops={"color": "#4A4A46"},
        flierprops={"marker": "o", "markersize": 2.5, "alpha": 0.35, "markerfacecolor": "#777770", "markeredgecolor": "none"},
    )
    axes[0, 0].set_xticks(category_positions)
    axes[0, 0].set_xticklabels(config.CATEGORY_ORDER)
    axes[0, 0].set_title("Google rating by category")
    axes[0, 0].set_xlabel("Destination category")
    axes[0, 0].set_ylabel("Google rating")
    axes[0, 0].set_ylim(1.8, 5.1)

    count_by_category = [
        count_data.loc[count_data["kategori"] == category, "log_count"].dropna().to_numpy()
        for category in config.CATEGORY_ORDER
    ]
    axes[0, 1].boxplot(
        count_by_category,
        positions=category_positions,
        patch_artist=True,
        widths=0.55,
        boxprops={"facecolor": "#EDF1EA", "edgecolor": "#4A4A46"},
        medianprops={"color": "#B4545B", "linewidth": 1.6},
        whiskerprops={"color": "#4A4A46"},
        capprops={"color": "#4A4A46"},
        flierprops={"marker": "o", "markersize": 2.5, "alpha": 0.35, "markerfacecolor": "#777770", "markeredgecolor": "none"},
    )
    axes[0, 1].set_xticks(category_positions)
    axes[0, 1].set_xticklabels(config.CATEGORY_ORDER)
    axes[0, 1].set_title("Rating count by category")
    axes[0, 1].set_xlabel("Destination category")
    axes[0, 1].set_ylabel("log1p(number of Google ratings)")

    regency_rating = (
        rating_data.groupby("kabupaten_kota")["rating"].median().sort_values()
    )
    regency_positions = np.arange(len(regency_rating))
    axes[1, 0].boxplot(
        [rating_data.loc[rating_data["kabupaten_kota"] == region, "rating"].dropna().to_numpy() for region in regency_rating.index],
        positions=regency_positions,
        vert=False,
        patch_artist=True,
        widths=0.55,
        boxprops={"facecolor": "#E8EEF2", "edgecolor": "#4A4A46"},
        medianprops={"color": "#B4545B", "linewidth": 1.6},
        whiskerprops={"color": "#4A4A46"},
        capprops={"color": "#4A4A46"},
        flierprops={"marker": "o", "markersize": 2.5, "alpha": 0.35, "markerfacecolor": "#777770", "markeredgecolor": "none"},
    )
    axes[1, 0].set_yticks(regency_positions)
    axes[1, 0].set_yticklabels([region.replace("Kabupaten ", "").replace("Kota ", "") for region in regency_rating.index])
    axes[1, 0].set_title("Google rating by regency or city")
    axes[1, 0].set_xlabel("Google rating")
    axes[1, 0].set_ylabel("")
    axes[1, 0].set_xlim(1.8, 5.1)

    regency_count = (
        count_data.groupby("kabupaten_kota")["log_count"].median().sort_values()
    )
    regency_positions = np.arange(len(regency_count))
    axes[1, 1].boxplot(
        [count_data.loc[count_data["kabupaten_kota"] == region, "log_count"].dropna().to_numpy() for region in regency_count.index],
        positions=regency_positions,
        vert=False,
        patch_artist=True,
        widths=0.55,
        boxprops={"facecolor": "#EDF1EA", "edgecolor": "#4A4A46"},
        medianprops={"color": "#B4545B", "linewidth": 1.6},
        whiskerprops={"color": "#4A4A46"},
        capprops={"color": "#4A4A46"},
        flierprops={"marker": "o", "markersize": 2.5, "alpha": 0.35, "markerfacecolor": "#777770", "markeredgecolor": "none"},
    )
    axes[1, 1].set_yticks(regency_positions)
    axes[1, 1].set_yticklabels([region.replace("Kabupaten ", "").replace("Kota ", "") for region in regency_count.index])
    axes[1, 1].set_title("Rating count by regency or city")
    axes[1, 1].set_xlabel("log1p(number of Google ratings)")
    axes[1, 1].set_ylabel("")

    for axis in axes.flat:
        axis.grid(axis="x", visible=True)
    figure.suptitle("Descriptive comparisons by category and regency or city", fontsize=14, fontweight="bold")
    figure_note(
        figure,
        "Top row uses records with a rating above zero. Bottom row uses records with a positive rating count. "
        "Boxes show the median and interquartile range; whiskers extend to 1.5 times the IQR.",
        y=0.005,
    )
    figure.tight_layout(rect=(0, 0.02, 1, 0.97))
    save_and_show(figure, path)


def _set_map_extent(axis: plt.Axes) -> None:
    axis.set_xlim(*MAP_XLIM)
    axis.set_ylim(*MAP_YLIM)
    axis.set_aspect(1 / np.cos(np.deg2rad(MEAN_LATITUDE)))
    axis.set_xlabel("Longitude (degrees east)")
    axis.set_ylabel("Latitude (degrees north)")
    axis.grid(True, linestyle=":", linewidth=0.6, alpha=0.65)


def _add_scale_bar(axis: plt.Axes, length_km: float = 20) -> None:
    x0 = MAP_XLIM[0] + 0.06 * (MAP_XLIM[1] - MAP_XLIM[0])
    y0 = MAP_YLIM[0] + 0.07 * (MAP_YLIM[1] - MAP_YLIM[0])
    delta_lon = length_km / (111.32 * np.cos(np.deg2rad(MEAN_LATITUDE)))
    axis.plot([x0, x0 + delta_lon], [y0, y0], color="#222222", linewidth=2.2, solid_capstyle="butt")
    axis.plot([x0, x0], [y0 - 0.006, y0 + 0.006], color="#222222", linewidth=1)
    axis.plot([x0 + delta_lon, x0 + delta_lon], [y0 - 0.006, y0 + 0.006], color="#222222", linewidth=1)
    axis.text(x0 + delta_lon / 2, y0 + 0.012, f"{length_km:.0f} km", ha="center", va="bottom", fontsize=8)


def _add_north_arrow(axis: plt.Axes) -> None:
    x = MAP_XLIM[1] - 0.08 * (MAP_XLIM[1] - MAP_XLIM[0])
    y = MAP_YLIM[1] - 0.13 * (MAP_YLIM[1] - MAP_YLIM[0])
    axis.annotate(
        "N",
        xy=(x, y + 0.035),
        xytext=(x, y),
        ha="center",
        va="center",
        fontsize=9,
        fontweight="bold",
        arrowprops={"arrowstyle": "-|>", "color": "#222222", "linewidth": 1.2},
    )


def plot_point_map(frame: pd.DataFrame, path: str | Path, excluded: int = 0) -> plt.Figure:
    data = frame[frame["analytic_geo"]].copy()
    figure, axis = plt.subplots(figsize=(10.5, 7.4))
    for category in config.CATEGORY_ORDER:
        subset = data[data["kategori"] == category]
        axis.scatter(
            subset["longitude"],
            subset["latitude"],
            s=19,
            alpha=0.82,
            color=config.CATEGORY_COLORS[category],
            edgecolor="white",
            linewidth=0.35,
            label=f"{category} (n = {len(subset):,})",
        )
    axis.set_title("Destination records in Bali by category")
    _set_map_extent(axis)
    _add_scale_bar(axis)
    _add_north_arrow(axis)
    axis.legend(loc="lower right", title="Category", fontsize=8, title_fontsize=9)
    figure_note(
        figure,
        f"Records with coordinates inside the broad Bali bounding box, N = {len(data):,}. "
        f"{excluded:,} record(s) outside that box are not shown. "
        "The box is a screening aid, not an official boundary.",
    )
    figure.tight_layout()
    save_and_show(figure, path)


def plot_attribute_maps(frame: pd.DataFrame, path: str | Path) -> plt.Figure:
    data = frame[frame["analytic_geo"] & frame["analytic_rating"]].copy()
    figure, axes = plt.subplots(1, 2, figsize=(15, 6.6), constrained_layout=True)
    figure.suptitle("Destination records by rating and by number of ratings", fontsize=14, fontweight="bold")

    rating_points = axes[0].scatter(
        data["longitude"],
        data["latitude"],
        c=data["rating"],
        cmap="viridis",
        vmin=2,
        vmax=5,
        s=20,
        edgecolor="white",
        linewidth=0.3,
    )
    axes[0].set_title("Google rating")
    _set_map_extent(axes[0])
    _add_scale_bar(axes[0])
    _add_north_arrow(axes[0])
    rating_bar = figure.colorbar(rating_points, ax=axes[0], shrink=0.72, pad=0.02)
    rating_bar.set_label("Google rating")

    count_points = axes[1].scatter(
        data["longitude"],
        data["latitude"],
        c=data["log_jumlah_rating"],
        cmap="cividis",
        s=20,
        edgecolor="white",
        linewidth=0.3,
    )
    axes[1].set_title("Number of Google ratings, log1p scale")
    _set_map_extent(axes[1])
    _add_scale_bar(axes[1])
    _add_north_arrow(axes[1])
    count_bar = figure.colorbar(count_points, ax=axes[1], shrink=0.72, pad=0.02)
    count_bar.set_label("log1p(number of Google ratings)")

    axes[0].set_ylabel("Latitude (degrees north)")
    axes[1].set_ylabel("")
    figure_note(
        figure,
        f"Records with coordinates inside the broad Bali bounding box and a rating above zero, N = {len(data):,}. "
        "Colour shows the observed platform value for each record. Descriptive only.",
        y=0.01,
    )
    save_and_show(figure, path)
