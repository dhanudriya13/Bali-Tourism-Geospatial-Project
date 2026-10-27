"""Transparent cleaning, flagging, and analysis-specific sample definitions."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

from . import config
from .data_validation import duplicate_tables


@dataclass
class CleanResult:
    data: pd.DataFrame
    cleaning_log: pd.DataFrame
    name_duplicate_candidates: pd.DataFrame
    coincident_coordinate_groups: pd.DataFrame
    likely_duplicate_records: pd.DataFrame
    invalid_numeric_records: pd.DataFrame


def _normalise_name(values: pd.Series) -> pd.Series:
    return values.fillna("").str.strip().str.casefold()


def clean_dataset(raw: pd.DataFrame) -> CleanResult:
    """Add derived fields and validation flags without dropping source records."""
    missing = [column for column in config.EXPECTED_COLUMNS if column not in raw.columns]
    if missing:
        raise ValueError(
            "Cannot clean the dataset because expected columns are absent: "
            + ", ".join(missing)
            + ". Inspect the source header before continuing."
        )
    frame = raw.copy()
    log_rows: list[dict] = []

    def add_log(step: str, rule: str, rows_flagged: int, rows_excluded: int = 0, note: str = "") -> None:
        log_rows.append(
            {
                "step": step,
                "rule": rule,
                "rows_flagged": int(rows_flagged),
                "rows_excluded": int(rows_excluded),
                "note": note,
            }
        )

    add_log("Audit", "Rows in source file", len(frame), 0, "Raw file is preserved unchanged.")

    whitespace_changed = pd.Series(False, index=frame.index)
    for column in config.TEXT_COLUMNS:
        if column not in frame.columns:
            continue
        original = frame[column]
        cleaned = original.str.strip()
        whitespace_changed |= original.fillna("") != cleaned.fillna("")
        frame[column] = cleaned
    add_log(
        "Cleaning",
        "Leading or trailing whitespace trimmed in text fields",
        int(whitespace_changed.sum()),
        0,
        "Only surrounding whitespace was removed.",
    )

    for column in config.NUMERIC_COLUMNS:
        frame[f"{column}_raw"] = frame[column]
        frame[column] = pd.to_numeric(frame[column], errors="coerce")

    failed_parse = frame[config.NUMERIC_COLUMNS].isna() & frame[
        [f"{column}_raw" for column in config.NUMERIC_COLUMNS]
    ].notna().to_numpy()
    invalid_numeric = frame[failed_parse.any(axis=1)].copy()
    add_log(
        "Cleaning",
        "Numeric fields that could not be parsed",
        len(invalid_numeric),
        0,
        "Unparseable values are retained in the audit output.",
    )

    rating = frame["rating"]
    count = frame["jumlah_rating"]
    latitude = frame["latitude"]
    longitude = frame["longitude"]

    frame["flag_missing_rating"] = rating.isna()
    frame["flag_rating_zero"] = rating.eq(0)
    frame["flag_rating_out_of_range"] = rating.notna() & ~rating.between(0, 5)
    frame["flag_missing_count"] = count.isna()
    frame["flag_count_negative"] = count.notna() & (count < 0)
    frame["flag_count_fractional"] = count.notna() & (count % 1 != 0)
    frame["flag_missing_coords"] = latitude.isna() | longitude.isna()

    global_invalid = (
        latitude.notna()
        & longitude.notna()
        & (~latitude.between(-90, 90) | ~longitude.between(-180, 180))
    )
    frame["flag_coord_global_invalid"] = global_invalid

    bbox = config.BALI_BBOX
    in_bbox = (
        latitude.between(bbox["lat_min"], bbox["lat_max"])
        & longitude.between(bbox["lon_min"], bbox["lon_max"])
    )
    frame["flag_coord_outside_bali_bbox"] = (
        latitude.notna() & longitude.notna() & ~global_invalid & ~in_bbox
    )

    has_coords = latitude.notna() & longitude.notna()
    frame["flag_coincident_coords"] = False
    if has_coords.any():
        coincident = frame.loc[has_coords].duplicated(subset=["latitude", "longitude"], keep=False)
        frame.loc[coincident[coincident].index, "flag_coincident_coords"] = True

    frame["nama_tempat_norm"] = _normalise_name(frame["nama_tempat_wisata"])
    frame["flag_name_duplicate"] = frame["nama_tempat_norm"].duplicated(keep=False)

    duplicate_key = ["nama_tempat_norm", "latitude", "longitude", "rating", "jumlah_rating"]
    group_size = frame.groupby(duplicate_key, dropna=False)["id_tempat"].transform("size")
    frame["flag_likely_duplicate_record"] = group_size.gt(1)
    likely_duplicates = frame[frame["flag_likely_duplicate_record"]].copy()

    frame["flag_missing_image_link"] = frame["link_gambar"].isna()

    frame["log_jumlah_rating"] = np.log1p(count.where(count >= 0))
    frame["rating_valid"] = rating.notna() & rating.gt(0) & rating.le(5)
    frame["count_valid"] = count.notna() & count.ge(0) & (count % 1 == 0)
    frame["coords_in_bali"] = has_coords & ~global_invalid & in_bbox
    frame["analytic_rating"] = frame["rating_valid"]
    frame["analytic_popularity"] = frame["rating_valid"] & frame["count_valid"] & count.gt(0)
    frame["analytic_geo"] = frame["coords_in_bali"]

    zeros = int(frame["flag_rating_zero"].sum())
    add_log(
        "Flagging",
        "Rating recorded as zero",
        zeros,
        int((~frame["analytic_rating"]).sum()),
        "A zero is treated as an unrated record, not as a literal quality score.",
    )
    add_log("Flagging", "Rating outside 0 to 5", int(frame["flag_rating_out_of_range"].sum()))
    add_log("Flagging", "Missing rating", int(frame["flag_missing_rating"].sum()))
    add_log("Flagging", "Missing rating count", int(frame["flag_missing_count"].sum()))
    add_log("Flagging", "Negative rating count", int(frame["flag_count_negative"].sum()))
    add_log("Flagging", "Fractional rating count", int(frame["flag_count_fractional"].sum()))
    add_log(
        "Flagging",
        "Rating count recorded as zero",
        int(count.eq(0).sum()),
        0,
        "Retained in the data but excluded from the rating-count association.",
    )
    add_log("Flagging", "Missing coordinates", int(frame["flag_missing_coords"].sum()))
    add_log(
        "Flagging",
        "Coordinates invalid at global scale",
        int(frame["flag_coord_global_invalid"].sum()),
    )
    add_log(
        "Flagging",
        "Coordinates outside the broad Bali bounding box",
        int(frame["flag_coord_outside_bali_bbox"].sum()),
        int((~frame["analytic_geo"]).sum()),
        "Excluded only from geographic mapping and spatial analysis.",
    )
    add_log(
        "Flagging",
        "Rows sharing a coordinate with at least one other record",
        int(frame["flag_coincident_coords"].sum()),
        0,
        "Retained; sensitivity analysis aggregates coincident locations.",
    )
    add_log(
        "Flagging",
        "Rows whose name is repeated after case and whitespace normalisation",
        int(frame["flag_name_duplicate"].sum()),
        0,
        "Names alone are not treated as evidence of duplication.",
    )
    add_log(
        "Flagging",
        "Rows matching another record on name, coordinates, rating, and count",
        len(likely_duplicates),
        0,
        "Exported for review; retained in the primary analysis.",
    )
    add_log("Flagging", "Missing image link", int(frame["flag_missing_image_link"].sum()))
    add_log(
        "Sample",
        "Eligible for geographic mapping",
        int(frame["analytic_geo"].sum()),
        int((~frame["analytic_geo"]).sum()),
        "Requires non-missing coordinates inside the broad Bali bounding box.",
    )
    add_log(
        "Sample",
        "Eligible for rating summaries and rating-count association",
        int(frame["analytic_popularity"].sum()),
        int((~frame["analytic_popularity"]).sum()),
        "Requires a rating above zero, at most 5, and a positive whole-number rating count.",
    )

    duplicates = duplicate_tables(frame)
    log = pd.DataFrame(log_rows)
    return CleanResult(
        data=frame,
        cleaning_log=log,
        name_duplicate_candidates=duplicates["name_candidates"],
        coincident_coordinate_groups=duplicates["coordinate_groups"],
        likely_duplicate_records=likely_duplicates,
        invalid_numeric_records=invalid_numeric,
    )
