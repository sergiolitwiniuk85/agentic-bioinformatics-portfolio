"""Xenium analysis CLI (used by the Snakemake workflow).

Modes:
    analyze <data_dir> <out_h5> <out_summary>   # load + cluster + save
    figure  <in_h5> <out_fig>                    # plot the subcellular map
"""

import json
import sys
from pathlib import Path

from agentic_bio.data.xenium import analyze_xenium, load_xenium, plot_subcellular, xenium_summary


def _analyze(data_dir: str, out_h5: str, out_summary: str) -> None:
    adata = load_xenium(Path(data_dir))
    adata = analyze_xenium(adata)
    adata.write_h5ad(out_h5)
    summary = xenium_summary(adata)
    Path(out_summary).parent.mkdir(parents=True, exist_ok=True)
    Path(out_summary).write_text(json.dumps(summary, indent=2))
    print(f"Xenium: {summary['n_cells']} cells, {summary['n_clusters']} clusters")


def _figure(in_h5: str, out_fig: str) -> None:
    import anndata as ad

    adata = ad.read_h5ad(in_h5)
    plot_subcellular(adata, out_fig)
    print(f"Xenium figure -> {out_fig}")


if __name__ == "__main__":
    mode = sys.argv[1]
    if mode == "analyze":
        _analyze(sys.argv[2], sys.argv[3], sys.argv[4])
    elif mode == "figure":
        _figure(sys.argv[2], sys.argv[3])
    else:
        raise SystemExit(f"unknown mode: {mode}")
