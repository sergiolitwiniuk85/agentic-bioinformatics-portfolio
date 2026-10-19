"""Xenium subcellular spatial data: load + analyze + plot."""

from __future__ import annotations

import hashlib
from pathlib import Path

import anndata as ad
import scanpy as sc

DEFAULT_DATA = Path("data/xenium")


def load_xenium(path: Path = DEFAULT_DATA) -> ad.AnnData:
    """Load a Xenium output bundle into AnnData with cell centroids as `obsm['spatial']`."""
    import pandas as pd

    adata = sc.read_10x_h5(path / "cell_feature_matrix.h5")
    cells = pd.read_parquet(path / "cells.parquet").set_index("cell_id")
    adata.obs = adata.obs.join(cells, how="left")
    adata.obsm["spatial"] = adata.obs[["x_centroid", "y_centroid"]].to_numpy()
    adata.var_names_make_unique()
    return adata


def analyze_xenium(adata: ad.AnnData, resolution: float = 0.5) -> ad.AnnData:
    """QC, normalize, and cluster a Xenium dataset."""
    sc.pp.filter_cells(adata, min_counts=5)
    sc.pp.filter_genes(adata, min_cells=3)
    sc.pp.normalize_total(adata, target_sum=1e4)
    sc.pp.log1p(adata)
    sc.pp.highly_variable_genes(adata, n_top_genes=200)
    sc.pp.scale(adata, max_value=10)
    sc.tl.pca(adata, n_comps=min(30, adata.n_obs - 1, adata.n_vars - 1))
    sc.pp.neighbors(adata)
    sc.tl.leiden(adata, resolution=resolution)
    return adata


def xenium_fingerprint(adata: ad.AnnData) -> str:
    """Deterministic fingerprint of the Xenium clustering (stable across re-runs)."""
    labels = ",".join(sorted(adata.obs["leiden"].astype(str).tolist()))
    payload = f"{labels}|cells={adata.n_obs}|genes={adata.n_vars}"
    return hashlib.sha256(payload.encode()).hexdigest()


def xenium_summary(adata: ad.AnnData) -> dict:
    """Summary + fingerprint of a clustered Xenium dataset."""
    return {
        "n_cells": int(adata.n_obs),
        "n_genes": int(adata.n_vars),
        "n_clusters": int(adata.obs["leiden"].nunique()),
        "fingerprint": xenium_fingerprint(adata),
    }


def plot_subcellular(
    adata: ad.AnnData,
    output_fig: str,
    title: str = "Xenium human breast — subcellular clusters",
) -> None:
    """Plot cells colored by cluster at their spatial (subcellular) coordinates."""
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    sc.pl.embedding(adata, basis="spatial", color="leiden", size=12, show=False)
    plt.suptitle(title, fontweight="bold")
    Path(output_fig).parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_fig, bbox_inches="tight", dpi=120)
    plt.close()
