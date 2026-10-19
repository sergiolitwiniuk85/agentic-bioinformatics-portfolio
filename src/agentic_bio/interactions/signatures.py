"""Functional/developmental gene-signature filters (pre-indexed panels).

Each signature is a curated gene set; applying it scores every cell with
`scanpy.tl.score_genes` and paints the tissue by that score — a one-click
functional readout that complements the spatial-interaction filters.
"""

from __future__ import annotations

import anndata as ad
import scanpy as sc

from agentic_bio.interactions.core import _plot_scatter

SIGNATURES: dict[str, dict] = {
    "proliferation": {"name": "Proliferation", "genes": ["MKI67", "PCNA", "TOP2A", "MCM2", "CCNB1"]},
    "hypoxia": {"name": "Hypoxia", "genes": ["HIF1A", "VEGFA", "CA9", "SLC2A1", "LDHA"]},
    "emt": {"name": "EMT", "genes": ["VIM", "FN1", "SNAI1", "SNAI2", "ZEB1"]},
    "interferon": {"name": "Interferon / inflammation", "genes": ["IFNG", "STAT1", "IRF1", "CXCL10", "CXCL9", "ISG15"]},
    "apoptosis": {"name": "Apoptosis", "genes": ["BAX", "BCL2", "CASP3", "CASP8"]},
    "angiogenesis": {"name": "Angiogenesis", "genes": ["VEGFA", "PECAM1", "VWF", "KDR"]},
    "checkpoint": {"name": "Immunotherapy / checkpoint", "genes": ["CD274", "PDCD1", "CTLA4", "CD8A", "IFNG"]},
    "er_signaling": {"name": "ER signaling", "genes": ["ESR1", "PGR", "FOXA1"]},
    "her2": {"name": "HER2", "genes": ["ERBB2", "GRB7"]},
    "stemness": {"name": "Stemness", "genes": ["ALDH1A1", "PROM1", "SOX2", "NANOG"]},
}


def list_signatures() -> list[str]:
    return list(SIGNATURES.keys())


def _available_genes(adata: ad.AnnData, signature_id: str) -> list[str]:
    return [g for g in SIGNATURES[signature_id]["genes"] if g in adata.var_names]


def score_signature(adata: ad.AnnData, signature_id: str):
    """Score every cell for a signature; returns (adata, metrics)."""
    if signature_id not in SIGNATURES:
        raise ValueError(f"unknown signature '{signature_id}'. Available: {list_signatures()}")
    genes = _available_genes(adata, signature_id)
    if len(genes) < 2:
        raise ValueError(
            f"signature '{signature_id}' has {len(genes)} gene(s) in this panel "
            f"({genes}); needs whole-transcriptome data (Visium)"
        )
    sc.tl.score_genes(adata, genes, score_name=f"signature_{signature_id}")
    return adata, {"n_genes": len(genes), "genes": genes}


def plot_signature(adata: ad.AnnData, signature_id: str, output_fig: str) -> None:
    """Plot cells colored by the signature score."""
    color = f"signature_{signature_id}"
    name = SIGNATURES[signature_id]["name"]
    _plot_scatter(adata, color, output_fig, f"{name} signature", cmap="magma")
