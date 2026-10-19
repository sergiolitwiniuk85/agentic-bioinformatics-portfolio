"""Spatial: spatial neighbors + neighborhood enrichment (squidpy)."""

import sys
from pathlib import Path

import anndata as ad
import scanpy as sc
import squidpy as sq

from common import load_config


def main(input_path: str, output_h5: str, output_fig: str) -> None:
    cfg = load_config()["cluster"]
    adata = ad.read_h5ad(input_path)
    adata.var_names_make_unique()

    sc.pp.normalize_total(adata, target_sum=1e4)
    sc.pp.log1p(adata)
    sc.pp.highly_variable_genes(adata)
    sc.pp.scale(adata, max_value=10)
    sc.tl.pca(adata, n_comps=min(30, adata.n_obs, adata.n_vars))
    sc.pp.neighbors(adata)
    sc.tl.leiden(adata, resolution=cfg["resolution"])

    sq.gr.spatial_neighbors(adata)
    sq.gr.nhood_enrichment(adata, cluster_key="leiden")

    adata.write_h5ad(output_h5)

    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    sq.pl.nhood_enrichment(adata, cluster_key="leiden", show=False)
    Path(output_fig).parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_fig, bbox_inches="tight", dpi=150)
    print(f"Spatial: nhood enrichment -> {output_fig}")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], sys.argv[3])
