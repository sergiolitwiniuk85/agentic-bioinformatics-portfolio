"""Tests for the Xenium loader (skip if the dataset is not downloaded)."""

from pathlib import Path

import pytest

HAS_DATA = Path("data/xenium/cell_feature_matrix.h5").exists()


@pytest.mark.skipif(not HAS_DATA, reason="Xenium data not downloaded")
def test_load_xenium():
    from agentic_bio.data.xenium import load_xenium

    adata = load_xenium()
    assert adata.n_obs > 100
    assert adata.n_vars > 100
    assert "spatial" in adata.obsm
    assert adata.obsm["spatial"].shape == (adata.n_obs, 2)
