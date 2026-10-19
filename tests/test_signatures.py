"""Tests for the gene-signature filters (on synthetic data, CI-safe)."""

import numpy as np
import pandas as pd
import pytest

pytest.importorskip("scanpy", reason="scanpy not installed (omics extra)")

import anndata as ad

from agentic_bio.interactions.signatures import list_signatures, score_signature


def _signature_synthetic(n: int = 100) -> ad.AnnData:
    rng = np.random.default_rng(1)
    genes = ["MKI67", "TOP2A", "CD274", "PDCD1", "CTLA4", "CD8A", "ESR1", "PGR", "FOXA1", "ERBB2"]
    X = rng.poisson(2, size=(n, len(genes))).astype(float)
    adata = ad.AnnData(X=X, var=pd.DataFrame(index=genes))
    adata.obsm["spatial"] = rng.uniform(0, 100, size=(n, 2))
    return adata


def test_list_signatures_has_ten():
    assert len(list_signatures()) == 10


def test_score_checkpoint():
    adata, m = score_signature(_signature_synthetic(), "checkpoint")
    assert "signature_checkpoint" in adata.obs
    assert m["n_genes"] >= 2


def test_score_er_signaling():
    adata, m = score_signature(_signature_synthetic(), "er_signaling")
    assert "signature_er_signaling" in adata.obs
    assert m["n_genes"] == 3


def test_score_unavailable_signature_raises():
    # "hypoxia" genes are not in the synthetic panel
    with pytest.raises(ValueError):
        score_signature(_signature_synthetic(), "hypoxia")


def test_unknown_signature_raises():
    with pytest.raises(ValueError):
        score_signature(_signature_synthetic(), "does_not_exist")
