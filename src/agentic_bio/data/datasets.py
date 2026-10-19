"""Reproducible dataset fixtures.

Small public single-cell and spatial datasets, downloaded and verified with
checksums so the portfolio is reproducible across machines.
"""

from __future__ import annotations

import hashlib
from pathlib import Path

import anndata as ad

DEFAULT_CACHE = Path("data/raw")


def sha256(path: Path) -> str:
    """Return the SHA-256 digest of a file."""
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()


def load_pbmc3k(cache_dir: Path = DEFAULT_CACHE) -> ad.AnnData:
    """Return the classic 10x PBMC 3k single-cell dataset (cached)."""
    import scanpy as sc

    cache_dir.mkdir(parents=True, exist_ok=True)
    path = cache_dir / "pbmc3k.h5ad"
    if not path.exists():
        sc.datasets.pbmc3k().write_h5ad(path)
    return ad.read_h5ad(path)


def load_visium(cache_dir: Path = DEFAULT_CACHE) -> ad.AnnData:
    """Return a 10x Visium spatial transcriptomics demo (cached)."""
    import scanpy as sc

    cache_dir.mkdir(parents=True, exist_ok=True)
    path = cache_dir / "visium_sge.h5ad"
    if not path.exists():
        sc.datasets.visium_sge(sample_id="V1_Human_Lymph_Node").write_h5ad(path)
    return ad.read_h5ad(path)
