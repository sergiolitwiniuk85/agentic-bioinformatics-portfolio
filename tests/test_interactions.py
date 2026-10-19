"""Tests for the spatial-interaction filters (on synthetic data, CI-safe)."""

import anndata as ad
import numpy as np
import pandas as pd
import pytest

from agentic_bio.interactions import analyze_interaction, list_filters


def _synthetic(n: int = 200) -> ad.AnnData:
    rng = np.random.default_rng(0)
    coords = rng.uniform(0, 100, size=(n, 2))
    genes = ["COL1A1", "FN1", "PTPRC", "MS4A1", "CD3E", "CXCL12", "geneA", "geneB"]
    X = rng.poisson(2, size=(n, len(genes))).astype(float)
    adata = ad.AnnData(X=X, var=pd.DataFrame(index=genes))
    adata.obsm["spatial"] = coords
    adata.obs["leiden"] = pd.Categorical(rng.integers(0, 5, size=n).astype(str))
    return adata


def test_list_filters_has_seven():
    assert len(list_filters()) == 7


def test_neighborhood_enrichment():
    adata, _ = analyze_interaction(_synthetic(), "neighborhood_enrichment")
    assert "leiden_nhood_enrichment" in adata.uns


def test_tissue_borders():
    adata, _ = analyze_interaction(_synthetic(), "tissue_borders")
    assert "interface_score" in adata.obs


def test_paracrine_distance():
    adata, m = analyze_interaction(_synthetic(), "paracrine_distance", ligand_gene="CXCL12")
    assert "paracrine_distance" in adata.obs
    assert m["n_sources"] > 0


def test_immune_tls():
    adata, _ = analyze_interaction(_synthetic(), "immune_tls")
    assert "immune_density" in adata.obs


def test_niche():
    adata, m = analyze_interaction(_synthetic(), "niche")
    assert "niche" in adata.obs
    assert m["n_niches"] >= 1


def test_ecm_cell():
    adata, _ = analyze_interaction(_synthetic(), "ecm_cell")
    assert "ecm_score" in adata.obs


def test_ecm_cell_missing_genes_raises():
    adata = _synthetic()[:, ["geneA", "geneB"]].copy()
    with pytest.raises(ValueError):
        analyze_interaction(adata, "ecm_cell")


def test_unknown_filter_raises():
    with pytest.raises(ValueError):
        analyze_interaction(_synthetic(), "does_not_exist")
