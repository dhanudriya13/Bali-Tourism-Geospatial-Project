from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from src import config
from src.cleaning import clean_dataset
from src.data_validation import check_schema, load_dataset
from src.geospatial import knn_weights, morans_i, project_coordinates
from src.statistics import spearman_association


def make_frame(rows: list[dict]) -> pd.DataFrame:
    base = {
        "id_tempat": "BL0000000",
        "nama_tempat_wisata": "Example",
        "kategori": "Alam",
        "kecamatan": "Example",
        "kabupaten_kota": "Kabupaten Badung",
        "rating": "4.5",
        "jumlah_rating": "100",
        "latitude": "-8.5",
        "longitude": "115.2",
        "link_google_maps": "https://example.test",
        "link_gambar": "https://example.test/image.jpg",
    }
    return pd.DataFrame([{**base, **row} for row in rows])


def test_load_dataset_missing_file_raises(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError, match="Input CSV not found"):
        load_dataset(tmp_path / "absent.csv")


def test_load_dataset_preserves_raw_strings(tmp_path: Path) -> None:
    path = tmp_path / "data.csv"
    make_frame([{"id_tempat": "BL1", "rating": "4.5"}]).to_csv(path, index=False)
    frame = load_dataset(path)
    assert frame.loc[0, "rating"] == "4.5"
    assert str(frame["rating"].dtype) in {"str", "string", "object"}


def test_check_schema_reports_missing_and_unexpected() -> None:
    frame = make_frame([{}]).drop(columns=["kategori"])
    report = check_schema(frame)
    assert "kategori" in report["missing_columns"]
    assert not report["unexpected_columns"]


def test_clean_dataset_missing_columns_raises() -> None:
    raw = make_frame([{}]).drop(columns=["kategori"])
    with pytest.raises(ValueError, match="expected columns are absent"):
        clean_dataset(raw)


def test_clean_dataset_flags_without_dropping_rows() -> None:
    raw = make_frame(
        [
            {"id_tempat": "BL1", "nama_tempat_wisata": "A"},
            {"id_tempat": "BL2", "nama_tempat_wisata": "A", "rating": "0", "jumlah_rating": "0"},
            {"id_tempat": "BL3", "nama_tempat_wisata": "B", "latitude": "-7.8", "longitude": "112.0"},
            {"id_tempat": "BL4", "nama_tempat_wisata": "C", "latitude": "-8.6", "longitude": "115.2"},
        ]
    )
    result = clean_dataset(raw)
    data = result.data
    assert len(data) == len(raw)
    assert data.loc[data["id_tempat"] == "BL2", "flag_rating_zero"].all()
    assert data.loc[data["id_tempat"] == "BL3", "flag_coord_outside_bali_bbox"].all()
    assert not data.loc[data["id_tempat"] == "BL3", "analytic_geo"].all()
    assert data.loc[data["id_tempat"].isin(["BL1", "BL4"]), "analytic_geo"].all()
    assert data.loc[data["id_tempat"] == "BL3", "analytic_rating"].all()
    assert not data.loc[data["id_tempat"] == "BL2", "analytic_popularity"].all()
    assert result.cleaning_log["rows_flagged"].sum() > 0


def test_spearman_detects_monotonic_relation() -> None:
    frame = pd.DataFrame({"rating": np.arange(1, 21), "count": np.arange(1, 21) ** 2})
    result = spearman_association(frame, "rating", "count", n_bootstrap=100, seed=1)
    assert result["rho"] == pytest.approx(1.0)
    assert result["n"] == 20
    assert result["ci_low"] <= result["rho"] <= result["ci_high"]


def test_morans_i_is_positive_for_spatially_clustered_values() -> None:
    longitude = np.linspace(115.0, 115.3, 60)
    latitude = np.linspace(-8.8, -8.2, 60)
    frame = pd.DataFrame({"longitude": longitude, "latitude": latitude})
    x, y = project_coordinates(frame)
    weights = knn_weights(np.column_stack([x, y]), 4)
    values = np.concatenate([np.zeros(30), np.ones(30)])
    result = morans_i(values, weights, permutations=199, seed=2)
    assert -1 <= result["morans_i"] <= 1
    assert result["morans_i"] > 0
    assert 0 <= result["p_perm_greater"] <= 1


def test_project_coordinates_returns_metres_near_bali() -> None:
    frame = pd.DataFrame({"longitude": [115.2], "latitude": [-8.5]})
    x, y = project_coordinates(frame)
    assert x[0] > 100_000
    assert y[0] > 9_000_000
