"""Spatial: spatial neighbors, neighborhood enrichment, and tissue maps (Visium)."""

import shutil
import sys
from pathlib import Path

import anndata as ad
import scanpy as sc
import squidpy as sq

from common import load_config

_LIBRARY_ID = "V1_Human_Lymph_Node"
_MARKER_CANDIDATES = ["MS4A1", "CD79A", "CD3D", "LYZ", "CD14"]


def _first_available(adata: ad.AnnData, candidates: list[str]) -> str | None:
    for g in candidates:
        if g in adata.var_names:
            return g
    return None


def main(
    input_path: str,
    output_h5: str,
    output_nhood: str,
    output_leiden: str,
    output_gene: str,
) -> None:
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

    # 1) statistical co-localization matrix
    sq.pl.nhood_enrichment(adata, cluster_key="leiden", show=False)
    plt.suptitle("Visium lymph node — neighborhood enrichment", fontweight="bold")
    Path(output_nhood).parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_nhood, bbox_inches="tight", dpi=120)
    plt.close()

    # 2) tissue map colored by cluster
    sc.pl.spatial(
        adata, color="leiden", img_key="hires", library_id=_LIBRARY_ID, size=1.5, show=False
    )
    plt.suptitle("Visium lymph node — spatial clusters (Leiden)", fontweight="bold")
    Path(output_leiden).parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_leiden, bbox_inches="tight", dpi=120)
    plt.close()

    # 3) tissue map colored by a marker gene
    marker = _first_available(adata, _MARKER_CANDIDATES)
    if marker:
        sc.pl.spatial(
            adata,
            color=marker,
            img_key="hires",
            library_id=_LIBRARY_ID,
            size=1.5,
            cmap="Reds",
            show=False,
        )
        plt.suptitle(f"Visium lymph node — {marker} expression", fontweight="bold")
        plt.savefig(output_gene, bbox_inches="tight", dpi=120)
        plt.close()
    else:
        shutil.copyfile(output_leiden, output_gene)

    print(f"Spatial: nhood + tissue maps (marker: {marker or 'none'})")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5])
