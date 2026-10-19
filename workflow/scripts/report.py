"""Provenance report: summary stats + artifact fingerprints for reproducibility."""

import hashlib
import json
import sys
from datetime import UTC, datetime
from pathlib import Path

import anndata as ad

from common import sha256


def logical_fingerprint(adata: ad.AnnData) -> str:
    """Deterministic fingerprint of the clustering result (stable across re-runs)."""
    labels = ",".join(sorted(adata.obs["leiden"].astype(str).tolist()))
    payload = f"{labels}|cells={adata.n_obs}|genes={adata.n_vars}"
    return hashlib.sha256(payload.encode()).hexdigest()


def main(cluster_h5: str, de_csv: str, perturb_csv: str, output_json: str) -> None:
    adata = ad.read_h5ad(cluster_h5)
    n_clusters = int(adata.obs["leiden"].nunique()) if "leiden" in adata.obs else None

    prov = {
        "created_at": datetime.now(UTC).isoformat(),
        "summary": {
            "n_cells": int(adata.n_obs),
            "n_genes": int(adata.n_vars),
            "n_clusters": n_clusters,
        },
        "artifacts": {
            "cluster": {"path": str(cluster_h5), "logical_sha256": logical_fingerprint(adata)},
            "de_markers": {"path": str(de_csv), "sha256": sha256(Path(de_csv))},
            "perturbation": {"path": str(perturb_csv), "sha256": sha256(Path(perturb_csv))},
        },
    }

    Path(output_json).parent.mkdir(parents=True, exist_ok=True)
    Path(output_json).write_text(json.dumps(prov, indent=2))
    print(f"Provenance -> {output_json}")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
