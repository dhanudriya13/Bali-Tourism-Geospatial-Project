"""Coordinate projection, k-nearest-neighbour weights, and global Moran's I."""

from __future__ import annotations

import numpy as np
import pandas as pd
from pyproj import Transformer
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import connected_components
from scipy.spatial import cKDTree


def project_coordinates(frame: pd.DataFrame, epsg: int = 32750) -> tuple[np.ndarray, np.ndarray]:
    """Project WGS 84 longitude and latitude to metres in UTM zone 50S."""
    transformer = Transformer.from_crs("EPSG:4326", f"EPSG:{epsg}", always_xy=True)
    x, y = transformer.transform(frame["longitude"].to_numpy(), frame["latitude"].to_numpy())
    return np.asarray(x), np.asarray(y)


def knn_weights(coordinates: np.ndarray, k: int) -> csr_matrix:
    """Build row-standardised k-nearest-neighbour weights.

    Neighbours are found in projected metres. Coincident points are handled
    deterministically by index; their influence is evaluated separately by
    aggregating records that share a coordinate.
    """
    n = coordinates.shape[0]
    if n < 2:
        raise ValueError("At least two locations are required to build spatial weights.")
    k = min(k, n - 1)
    tree = cKDTree(coordinates)
    _, indices = tree.query(coordinates, k=k + 1)

    rows: list[int] = []
    cols: list[int] = []
    for i in range(n):
        neighbours = [int(j) for j in np.atleast_1d(indices[i]) if int(j) != i][:k]
        rows.extend([i] * len(neighbours))
        cols.extend(neighbours)

    data = np.ones(len(rows), dtype=float)
    weights = csr_matrix((data, (rows, cols)), shape=(n, n))
    row_sums = np.asarray(weights.sum(axis=1)).ravel()
    row_sums[row_sums == 0] = 1.0
    weights = csr_matrix(weights.multiply(1.0 / row_sums[:, None]))
    return weights


def weights_diagnostics(weights: csr_matrix) -> dict:
    n_components, _ = connected_components(weights, directed=True, connection="weak")
    degrees = np.diff(weights.indptr)
    row_sums = np.asarray(weights.sum(axis=1)).ravel()
    return {
        "n_locations": int(weights.shape[0]),
        "components": int(n_components),
        "min_neighbours": int(degrees.min()),
        "max_neighbours": int(degrees.max()),
        "row_sums_close_to_one": bool(np.allclose(row_sums, 1.0)),
    }


def morans_i(
    values: np.ndarray | pd.Series,
    weights: csr_matrix,
    permutations: int = 999,
    seed: int = 20261027,
) -> dict:
    """Global Moran's I with permutation inference.

    Returns the observed statistic, expected value under no autocorrelation,
    and one-sided (positive) and two-sided permutation p-values.
    """
    values = np.asarray(values, dtype=float)
    if values.ndim != 1 or values.size != weights.shape[0]:
        raise ValueError("Values must be a vector matching the weights matrix.")
    if not np.all(np.isfinite(values)):
        raise ValueError("Values must be finite; define the analytic sample before testing.")

    n = values.size
    z = values - values.mean()
    denominator = float(z @ z)
    if denominator == 0:
        raise ValueError("Values are constant, so spatial autocorrelation is undefined.")

    s0 = float(weights.sum())
    observed = (n / s0) * float(z @ (weights @ z)) / denominator
    expected = -1.0 / (n - 1)

    rng = np.random.default_rng(seed)
    permuted = np.empty(permutations, dtype=float)
    for i in range(permutations):
        shuffled = rng.permutation(z)
        permuted[i] = (n / s0) * float(shuffled @ (weights @ shuffled)) / denominator

    p_greater = (1 + np.count_nonzero(permuted >= observed)) / (permutations + 1)
    p_two_sided = (1 + np.count_nonzero(np.abs(permuted) >= abs(observed))) / (permutations + 1)
    return {
        "n": int(n),
        "morans_i": float(observed),
        "expected_i": float(expected),
        "p_perm_greater": float(p_greater),
        "p_perm_two_sided": float(p_two_sided),
        "permutations": int(permutations),
        "permuted_mean": float(permuted.mean()),
        "permuted_sd": float(permuted.std(ddof=1)) if permutations > 1 else np.nan,
    }


def moran_sensitivity(
    frame: pd.DataFrame,
    value_column: str,
    ks: tuple[int, ...],
    permutations: int,
    seed: int,
) -> pd.DataFrame:
    """Run global Moran's I for several k-nearest-neighbour settings."""
    x, y = project_coordinates(frame)
    coordinates = np.column_stack([x, y])
    values = frame[value_column].to_numpy()
    rows = []
    for k in ks:
        weights = knn_weights(coordinates, k)
        diagnostics = weights_diagnostics(weights)
        result = morans_i(values, weights, permutations=permutations, seed=seed)
        rows.append(
            {
                "variable": value_column,
                "k": int(min(k, len(frame) - 1)),
                "n": result["n"],
                "morans_i": result["morans_i"],
                "expected_i": result["expected_i"],
                "p_perm_greater": result["p_perm_greater"],
                "p_perm_two_sided": result["p_perm_two_sided"],
                "permutations": result["permutations"],
                "components": diagnostics["components"],
                "min_neighbours": diagnostics["min_neighbours"],
                "max_neighbours": diagnostics["max_neighbours"],
            }
        )
    return pd.DataFrame(rows)


def aggregate_coincident_locations(frame: pd.DataFrame, value_column: str) -> pd.DataFrame:
    """Average a variable within each exact coordinate for a sensitivity analysis."""
    grouped = (
        frame.groupby(["latitude", "longitude"], as_index=False)
        .agg(
            value=(value_column, "mean"),
            n_records=("id_tempat", "size"),
            n_distinct_names=("nama_tempat_norm", "nunique"),
        )
        .rename(columns={"value": value_column})
    )
    return grouped
