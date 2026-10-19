"""Provenance report: summary stats + artifact hashes for reproducibility."""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import anndata as ad  # noqa: E402
from common import sha256  # noqa: E402


def main(cluster_h5: str, de_csv: str, perturb_csv: str, output_json: str) -> None:
    adata = ad.read_h5ad(cluster_h5)
    n_clusters = int(adata.obs["leiden"].nunique()) if "leiden" in adata.obs else None

    prov = {
        "created_at": datetime.now(timezone.utc).isoformat(),
        "summary": {
            "n_cells": int(adata.n_obs),
            "n_genes": int(adata.n_vars),
            "n_clusters": n_clusters,
        },
        "artifacts": {
            "cluster": {"path": str(cluster_h5), "sha256": sha256(Path(cluster_h5))},
            "de_markers": {"path": str(de_csv), "sha256": sha256(Path(de_csv))},
            "perturbation": {"path": str(perturb_csv), "sha256": sha256(Path(perturb_csv))},
        },
    }

    Path(output_json).parent.mkdir(parents=True, exist_ok=True)
    Path(output_json).write_text(json.dumps(prov, indent=2))
    print(f"Provenance -> {output_json}")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
