"""Project paths and analysis constants.

Set the BALI_INPUT_CSV environment variable to override the default input path.
Set BALI_PROJECT_ROOT to run the notebook from outside the project directory.
"""

from __future__ import annotations

import os
from pathlib import Path

PROJECT_ROOT = Path(os.environ.get("BALI_PROJECT_ROOT", Path(__file__).resolve().parents[1]))

DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
OUTPUT_DIR = PROJECT_ROOT / "outputs"
FIGURE_DIR = OUTPUT_DIR / "figures"
TABLE_DIR = OUTPUT_DIR / "tables"
REPORT_DIR = OUTPUT_DIR / "reports"

DEFAULT_INPUT_CSV = RAW_DATA_DIR / "bali_tourist_destination.csv"
INPUT_CSV = Path(os.environ.get("BALI_INPUT_CSV", DEFAULT_INPUT_CSV))

EXPECTED_COLUMNS = [
    "id_tempat",
    "nama_tempat_wisata",
    "kategori",
    "kecamatan",
    "kabupaten_kota",
    "rating",
    "jumlah_rating",
    "latitude",
    "longitude",
    "link_google_maps",
    "link_gambar",
]

TEXT_COLUMNS = [
    "id_tempat",
    "nama_tempat_wisata",
    "kategori",
    "kecamatan",
    "kabupaten_kota",
    "link_google_maps",
    "link_gambar",
]

NUMERIC_COLUMNS = ["rating", "jumlah_rating", "latitude", "longitude"]

CATEGORY_ORDER = ["Alam", "Budaya", "Rekreasi", "Umum"]

CATEGORY_COLORS = {
    "Alam": "#2A6F97",
    "Budaya": "#B4545B",
    "Rekreasi": "#C77C2B",
    "Umum": "#5F7A52",
}

TABLE_LABELS = {
    "rating": "Google rating",
    "jumlah_rating": "Number of Google ratings",
    "log_jumlah_rating": "log1p(number of Google ratings)",
    "latitude": "Latitude",
    "longitude": "Longitude",
}

# Broad bounding box used only to flag coordinates that fall outside Bali.
# It is intentionally wider than the island and is not an administrative boundary.
BALI_BBOX = {
    "lat_min": -9.30,
    "lat_max": -7.70,
    "lon_min": 114.30,
    "lon_max": 115.90,
}

RANDOM_SEED = 20261027
N_BOOTSTRAP = 2000
N_PERMUTATIONS = 999
PRIMARY_K = 8
KNN_KS = (4, 8, 12)

UTM_EPSG = 32750  # WGS 84 / UTM zone 50S, suitable for Bali


def ensure_directories() -> None:
    for directory in (PROCESSED_DATA_DIR, FIGURE_DIR, TABLE_DIR, REPORT_DIR):
        directory.mkdir(parents=True, exist_ok=True)
