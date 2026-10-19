"""In silico spatial-interaction filters (the 'virtual microscope').

Each filter reveals one class of cell-cell interaction, computed in silico from
spatial coordinates + expression. Filters 1-7 map to the interaction-type table.

Filters 8-11 (homotypic segregation, metabolic/hypoxia gradients, cross spatial
autocorrelation, autocrine density) are deferred to a later version.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import anndata as ad
import numpy as np
import scanpy as sc
import squidpy as sq
from scipy import sparse
from scipy.spatial import cKDTree

IMMUNE_MARKERS = ["PTPRC", "MS4A1", "CD79A", "CD3D", "CD3E", "CD8A", "CD4", "NKG7", "CD68"]
ECM_GENES = ["COL1A1", "COL1A2", "COL3A1", "COL4A1", "COL6A1", "FN1", "LAMA1", "LAMC1", "SPARC"]


def _spatial_graph(adata: ad.AnnData) -> None:
    if "spatial_connectivities" not in adata.obsp:
        sq.gr.spatial_neighbors(adata, coord_type="generic")


def _dense(adata: ad.AnnData, gene: str) -> np.ndarray:
    x = adata[:, gene].X
    return x.toarray().ravel() if sparse.issparse(x) else np.asarray(x).ravel()


def _plot_scatter(adata, color, output_fig, title, cmap=None) -> None:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    sc.pl.embedding(adata, basis="spatial", color=color, size=12, cmap=cmap, show=False)
    plt.suptitle(title, fontweight="bold")
    Path(output_fig).parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_fig, bbox_inches="tight", dpi=120)
    plt.close()


# 1. neighborhood enrichment / co-occurrence
def neighborhood_enrichment(adata: ad.AnnData):
    _spatial_graph(adata)
    sq.gr.nhood_enrichment(adata, cluster_key="leiden")
    return adata, {"enrichment": "leiden_nhood_enrichment"}


def plot_neighborhood_enrichment(adata, output_fig) -> None:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    sq.pl.nhood_enrichment(adata, cluster_key="leiden", show=False)
    plt.suptitle("Neighborhood enrichment (co-occurrence)", fontweight="bold")
    Path(output_fig).parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_fig, bbox_inches="tight", dpi=120)
    plt.close()


# 2. tissue interface (borders)
def tissue_borders(adata: ad.AnnData):
    _spatial_graph(adata)
    conn = adata.obsp["spatial_connectivities"].tocoo()
    labels = adata.obs["leiden"].to_numpy()
    scores = np.zeros(adata.n_obs)
    for i, j in zip(conn.row, conn.col):
        if labels[i] != labels[j]:
            scores[i] += 1
    degree = np.asarray(adata.obsp["spatial_connectivities"].sum(axis=1)).ravel()
    scores = scores / np.maximum(degree, 1)
    adata.obs["interface_score"] = scores
    return adata, {"mean_interface_score": float(scores.mean())}


# 3. paracrine signaling by distance
def paracrine_distance(adata: ad.AnnData, ligand_gene: str, threshold_pct: float = 75):
    if ligand_gene not in adata.var_names:
        raise ValueError(f"gene '{ligand_gene}' not in panel")
    expr = _dense(adata, ligand_gene)
    positive = expr[expr > 0]
    if positive.size == 0:
        raise ValueError(f"no cells express {ligand_gene}")
    thr = np.percentile(positive, threshold_pct)
    src = expr > thr
    tree = cKDTree(adata.obsm["spatial"][src])
    dist, _ = tree.query(adata.obsm["spatial"])
    adata.obs["paracrine_distance"] = dist
    return adata, {"mean_distance": float(dist.mean()), "n_sources": int(src.sum())}


# 4. immune microarchitecture / TLS
def immune_tls(adata: ad.AnnData, radius: float = 50.0):
    markers = [g for g in IMMUNE_MARKERS if g in adata.var_names]
    if not markers:
        raise ValueError("no immune markers in panel")
    expr = adata[:, markers].X
    expr = expr.toarray() if sparse.issparse(expr) else np.asarray(expr)
    immune_mask = (expr > 0).any(axis=1)
    immune_set = set(np.where(immune_mask)[0].tolist())
    coords = adata.obsm["spatial"]
    tree = cKDTree(coords)
    density = np.array(
        [sum(1 for n in tree.query_ball_point(c, radius) if n in immune_set) for c in coords]
    )
    adata.obs["immune_density"] = density
    return adata, {"n_immune_cells": int(immune_mask.sum()), "mean_density": float(density.mean())}


# 5. juxtacrine (direct contact) — Xenium only (requires cell boundaries)
def juxtacrine(adata: ad.AnnData, boundaries_path: str = "data/xenium/cell_boundaries.parquet"):
    import pandas as pd
    from shapely.geometry import Polygon
    from shapely.strtree import STRtree

    cb = pd.read_parquet(boundaries_path)
    cb["cell_id"] = cb["cell_id"].astype(str)
    cb = cb[cb["cell_id"].isin(adata.obs_names)]
    poly_by_cell: dict[str, Any] = {}
    for cid, grp in cb.groupby("cell_id"):
        poly_by_cell[cid] = Polygon(list(zip(grp["vertex_x"], grp["vertex_y"])))

    cells = list(poly_by_cell.keys())
    polys = [poly_by_cell[c] for c in cells]
    tree = STRtree(polys)
    labels = dict(zip(adata.obs_names, adata.obs["leiden"]))
    n_contacts = {c: 0 for c in cells}

    for i, poly in enumerate(polys):
        cid = cells[i]
        for cand in tree.query(poly):
            if cand == i:
                continue
            other_id = cells[cand]
            if poly.touches(polys[cand]) and labels.get(cid) != labels.get(other_id):
                n_contacts[cid] += 1

    adata.obs["n_contacts"] = [n_contacts.get(c, 0) for c in adata.obs_names]
    return adata, {"mean_contacts": float(np.mean(list(n_contacts.values())))}


# 6. niche domains
def niche(adata: ad.AnnData, n_neighbors: int = 30):
    coords = ad.AnnData(X=adata.obsm["spatial"].astype(float))
    sc.pp.neighbors(coords, n_neighbors=n_neighbors)
    sc.tl.leiden(coords, resolution=0.5)
    adata.obs["niche"] = coords.obs["leiden"].astype(str).values
    return adata, {"n_niches": int(adata.obs["niche"].nunique())}


# 7. ECM-cell interactions
def ecm_cell(adata: ad.AnnData):
    genes = [g for g in ECM_GENES if g in adata.var_names]
    if not genes:
        raise ValueError("no ECM genes (collagens) in panel — use whole-transcriptome data (Visium)")
    expr = adata[:, genes].X
    expr = expr.toarray() if sparse.issparse(expr) else np.asarray(expr)
    score = expr.mean(axis=1)
    adata.obs["ecm_score"] = score
    return adata, {"mean_ecm_score": float(score.mean()), "n_ecm_genes": len(genes)}


FILTERS: dict[str, dict[str, Any]] = {
    "neighborhood_enrichment": {
        "name": "Neighborhood enrichment / co-occurrence",
        "analyze": neighborhood_enrichment,
        "plot": plot_neighborhood_enrichment,
    },
    "tissue_borders": {
        "name": "Tissue interface (borders)",
        "analyze": tissue_borders,
        "plot": lambda a, o: _plot_scatter(a, "interface_score", o, "Tissue interface (borders)"),
    },
    "paracrine_distance": {
        "name": "Paracrine signaling by distance",
        "analyze": paracrine_distance,
        "plot": lambda a, o: _plot_scatter(a, "paracrine_distance", o, "Paracrine distance"),
    },
    "immune_tls": {
        "name": "Immune microarchitecture / TLS",
        "analyze": immune_tls,
        "plot": lambda a, o: _plot_scatter(a, "immune_density", o, "Immune density (TLS)"),
    },
    "juxtacrine": {
        "name": "Juxtacrine (direct contact)",
        "analyze": juxtacrine,
        "plot": lambda a, o: _plot_scatter(a, "n_contacts", o, "Juxtacrine contacts"),
    },
    "niche": {
        "name": "Niche domains",
        "analyze": niche,
        "plot": lambda a, o: _plot_scatter(a, "niche", o, "Niche domains"),
    },
    "ecm_cell": {
        "name": "ECM-cell interactions",
        "analyze": ecm_cell,
        "plot": lambda a, o: _plot_scatter(a, "ecm_score", o, "ECM score"),
    },
}


def list_filters() -> list[str]:
    return list(FILTERS.keys())


def analyze_interaction(adata: ad.AnnData, interaction_type: str, **params):
    if interaction_type not in FILTERS:
        raise ValueError(f"unknown interaction type '{interaction_type}'. Available: {list_filters()}")
    return FILTERS[interaction_type]["analyze"](adata, **params)


def plot_interaction(adata: ad.AnnData, interaction_type: str, output_fig: str) -> None:
    if interaction_type not in FILTERS:
        raise ValueError(f"unknown interaction type '{interaction_type}'")
    FILTERS[interaction_type]["plot"](adata, output_fig)
