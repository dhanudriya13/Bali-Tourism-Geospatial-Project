"""Loading, schema inspection, and record-level audit helpers."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from . import config


def load_dataset(path: str | Path | None = None) -> pd.DataFrame:
    """Load the source CSV as strings so that raw values are preserved."""
    source = Path(path) if path is not None else config.INPUT_CSV
    if not source.exists():
        raise FileNotFoundError(
            f"Input CSV not found at {source}. Place the file there, set BALI_INPUT_CSV, "
            "or change the input path in the configuration cell."
        )
    frame = pd.read_csv(source, encoding="utf-8-sig", dtype=str, keep_default_na=True)
    frame.columns = [str(column).strip() for column in frame.columns]
    return frame


def check_schema(frame: pd.DataFrame, expected: list[str] | None = None) -> dict:
    """Compare the observed header with the documented schema."""
    expected = expected or config.EXPECTED_COLUMNS
    observed = list(frame.columns)
    missing = [column for column in expected if column not in observed]
    unexpected = [column for column in observed if column not in expected]
    audit = pd.DataFrame(
        {
            "column": observed,
            "expected": [column in expected for column in observed],
            "non_null": [int(frame[column].notna().sum()) for column in observed],
            "missing": [int(frame[column].isna().sum()) for column in observed],
            "unique_values": [int(frame[column].nunique(dropna=True)) for column in observed],
            "example_value": [
                str(frame[column].dropna().iloc[0]) if frame[column].notna().any() else ""
                for column in observed
            ],
        }
    )
    return {
        "audit": audit,
        "missing_columns": missing,
        "unexpected_columns": unexpected,
        "n_rows": int(len(frame)),
        "n_columns": int(frame.shape[1]),
    }


def missingness_table(frame: pd.DataFrame) -> pd.DataFrame:
    counts = frame.isna().sum()
    table = pd.DataFrame(
        {
            "column": counts.index,
            "missing": counts.values.astype(int),
            "non_missing": (len(frame) - counts.values).astype(int),
            "percent_missing": (counts.values / max(len(frame), 1) * 100).round(2),
        }
    )
    return table.sort_values(["missing", "column"], ascending=[False, True]).reset_index(drop=True)


def duplicate_tables(frame: pd.DataFrame) -> dict:
    """Report exact duplicates, repeated IDs, name candidates, and coordinate groups."""
    exact_count = int(frame.duplicated().sum())
    id_table = (
        frame[frame["id_tempat"].duplicated(keep=False)]
        .sort_values("id_tempat")
        .reset_index(drop=True)
    )
    name_candidates = (
        frame.assign(nama_tempat_norm=frame["nama_tempat_wisata"].str.strip().str.casefold())
        .query("nama_tempat_norm.duplicated(keep=False)")
        .sort_values(["nama_tempat_norm", "id_tempat"])
        .reset_index(drop=True)
    )
    coordinate_groups = (
        frame.assign(
            coord_group_size=frame.groupby(["latitude", "longitude"])["id_tempat"].transform("size")
        )
        .query("coord_group_size > 1")
        .sort_values(["latitude", "longitude", "id_tempat"])
        .reset_index(drop=True)
    )
    return {
        "exact_duplicate_rows": exact_count,
        "repeated_ids": int(frame["id_tempat"].duplicated().sum()),
        "repeated_names": int(frame["nama_tempat_wisata"].duplicated().sum()),
        "id_table": id_table,
        "name_candidates": name_candidates,
        "coordinate_groups": coordinate_groups,
    }
