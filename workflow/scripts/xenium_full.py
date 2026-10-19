"""Full Xenium analysis: subset -> cluster -> cell types -> filters x thresholds.

Reproducible recipe for the 50k-cell Xenium example. Every plot is labeled with
its parameters and recorded in `manifest.json`.

Run:
    python workflow/scripts/xenium_full.py \
        --data /path/to/Xenium_FFPE_Human_Breast_Cancer_Rep1_outs \
        --n-cells 50000 \
        --out results/xenium_full
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import anndata as ad
import numpy as np
import scanpy as sc

from agentic_bio.data.xenium import (
    analyze_xenium,
    annotate_cell_types,
    load_xenium,
    plot_subcellular,
)
from agentic_bio.interactions import analyze_interaction, plot_interaction
from agentic_bio.interactions.signatures import (
    SIGNATURES,
    list_signatures,
    score_signature,
)

SIGNATURE_THRESHOLDS = [50, 75, 90]  # score percentile to highlight
PARACRINE_THRESHOLDS = [75, 90, 95]  # source-detection percentile
TLS_RADII = [30.0, 50.0, 80.0]  # µm


def subset_cells(adata: ad.AnnData, n: int, seed: int = 0) -> ad.AnnData:
    """Random subset of n cells (seeded for reproducibility)."""
    if adata.n_obs <= n:
        return adata
    rng = np.random.default_rng(seed)
    idx = rng.choice(adata.n_obs, size=n, replace=False)
    idx.sort()
    return adata[idx].copy()


def plot_threshold_highlight(adata, obs_key, pct, out_fig, title) -> None:
    """Highlight cells above the pct-th percentile of `obs_key`."""
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    vals = adata.obs[obs_key].to_numpy()
    thr = float(np.percentile(vals, pct))
    adata.obs["_hl"] = np.where(vals >= thr, f"high (>{pct}th)", "low")
    sc.pl.embedding(
        adata,
        basis="spatial",
        color="_hl",
        palette={"low": "lightgray", f"high (>{pct}th)": "crimson"},
        size=12,
        show=False,
    )
    plt.suptitle(f"{title} — >{pct}th percentile", fontweight="bold")
    Path(out_fig).parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(out_fig, bbox_inches="tight", dpi=120)
    plt.close()


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", required=True, help="path to the Xenium outs/ directory")
    ap.add_argument("--n-cells", type=int, default=50000)
    ap.add_argument("--out", default="results/xenium_full")
    ap.add_argument("--resolution", type=float, default=0.5)
    ap.add_argument("--seed", type=int, default=0)
    args = ap.parse_args()

    out = Path(args.out)
    figdir = out / "figures"
    figdir.mkdir(parents=True, exist_ok=True)

    manifest: dict = {"params": vars(args), "plots": []}

    # 1) load + subset
    adata = load_xenium(Path(args.data))
    adata = subset_cells(adata, args.n_cells, seed=args.seed)
    print(f"subset: {adata.n_obs} cells x {adata.n_vars} genes")

    # 2) cluster + annotate cell types
    adata = analyze_xenium(adata, resolution=args.resolution)
    adata = annotate_cell_types(adata)
    adata.write_h5ad(out / "xenium_clustered.h5ad")
    manifest["cell_types"] = adata.obs["cell_type"].value_counts().to_dict()

    plot_subcellular(
        adata, str(figdir / "cell_types.png"), color="cell_type",
        title=f"Xenium breast {adata.n_obs} cells — cell types",
    )
    manifest["plots"].append({"file": "cell_types.png", "kind": "cell_types"})

    # 3) interaction filters
    for filt in ["neighborhood_enrichment", "tissue_borders", "niche", "juxtacrine"]:
        a, m = analyze_interaction(adata, filt)
        plot_interaction(a, filt, str(figdir / f"interaction_{filt}.png"))
        manifest["plots"].append({"file": f"interaction_{filt}.png", "filter": filt, "metrics": m})

    # paracrine distance: 3 source-detection thresholds
    for t in PARACRINE_THRESHOLDS:
        a, m = analyze_interaction(adata, "paracrine_distance", ligand_gene="CXCL12", threshold_pct=t)
        f = f"interaction_paracrine_t{t}.png"
        plot_interaction(a, "paracrine_distance", str(figdir / f))
        manifest["plots"].append({"file": f, "filter": "paracrine_distance", "ligand": "CXCL12", "threshold_pct": t, "metrics": m})

    # immune TLS: 3 radii
    for r in TLS_RADII:
        a, m = analyze_interaction(adata, "immune_tls", radius=r)
        f = f"interaction_immune_tls_r{int(r)}.png"
        plot_interaction(a, "immune_tls", str(figdir / f))
        manifest["plots"].append({"file": f, "filter": "immune_tls", "radius_um": r, "metrics": m})

    # 4) signature filters: 3 score thresholds each
    for sig in list_signatures():
        try:
            a, m = score_signature(adata, sig)
        except ValueError as e:
            manifest["plots"].append({"signature": sig, "skipped": str(e)})
            continue
        for t in SIGNATURE_THRESHOLDS:
            f = f"signature_{sig}_p{t}.png"
            plot_threshold_highlight(a, f"signature_{sig}", t, str(figdir / f), SIGNATURES[sig]["name"])
            manifest["plots"].append(
                {"file": f, "signature": sig, "threshold_pct": t, "n_genes": m["n_genes"], "genes": m["genes"]}
            )

    (out / "manifest.json").write_text(json.dumps(manifest, indent=2))
    print(f"done -> {out / 'manifest.json'}")


if __name__ == "__main__":
    main()
