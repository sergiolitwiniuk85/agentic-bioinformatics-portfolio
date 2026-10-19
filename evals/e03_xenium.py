"""E03 eval gate: Xenium subcellular analysis (integrity + reproducibility)."""

import json
import sys
from pathlib import Path

import anndata as ad
import numpy as np

REPO = Path(__file__).resolve().parents[1]
SUMMARY = REPO / "results" / "xenium" / "xenium_summary.json"
H5 = REPO / "results" / "xenium" / "xenium_clustered.h5ad"


def main() -> None:
    print("=== E03 eval gate (Xenium) ===")
    if not SUMMARY.exists() or not H5.exists():
        print("No Xenium results. Run: snakemake -s workflow/Snakefile --directory . xenium_figure")
        sys.exit(0)

    summary = json.loads(SUMMARY.read_text())
    adata = ad.read_h5ad(H5)

    ok_counts = summary["n_cells"] > 1000 and summary["n_clusters"] >= 3
    print(
        f"[integrity] {summary['n_cells']} cells, {summary['n_clusters']} clusters "
        f"-> {'OK' if ok_counts else 'FAIL'}"
    )

    coords = adata.obsm["spatial"]
    ok_coords = bool(np.isfinite(coords).all()) and coords.shape == (adata.n_obs, 2)
    print(f"[subcellular] coords finite, shape {coords.shape} -> {'OK' if ok_coords else 'FAIL'}")

    from agentic_bio.data.xenium import xenium_fingerprint

    ok_fp = xenium_fingerprint(adata) == summary["fingerprint"]
    print(f"[reproducibility] fingerprint -> {'match' if ok_fp else 'MISMATCH'}")

    passed = ok_counts and ok_coords and ok_fp
    print(f"=== RESULT: {'PASS' if passed else 'FAIL'} ===")
    sys.exit(0 if passed else 1)


if __name__ == "__main__":
    main()
