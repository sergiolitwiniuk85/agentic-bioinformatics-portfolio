"""Differential expression: rank marker genes per cluster, export top markers."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import anndata as ad  # noqa: E402
import pandas as pd  # noqa: E402
import scanpy as sc  # noqa: E402
from common import load_config  # noqa: E402


def main(input_path: str, output_csv: str) -> None:
    cfg = load_config()["de"]
    adata = ad.read_h5ad(input_path)

    sc.tl.rank_genes_groups(adata, groupby="leiden", method=cfg["method"])

    result = adata.uns["rank_genes_groups"]
    groups = result["names"].dtype.names
    frames = []
    for g in groups:
        frames.append(
            pd.DataFrame(
                {
                    "group": g,
                    "gene": result["names"][g],
                    "logfoldchanges": result["logfoldchanges"][g],
                    "pvals_adj": result["pvals_adj"][g],
                }
            ).head(cfg["n_markers"])
        )
    markers = pd.concat(frames, ignore_index=True)

    Path(output_csv).parent.mkdir(parents=True, exist_ok=True)
    markers.to_csv(output_csv, index=False)
    print(f"DE: {len(markers)} marker rows -> {output_csv}")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
