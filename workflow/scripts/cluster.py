"""Cluster: scale, PCA, neighbors, UMAP, Leiden. Save h5ad + UMAP figure."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import anndata as ad  # noqa: E402
import scanpy as sc  # noqa: E402
from common import load_config  # noqa: E402


def main(input_path: str, output_h5: str, output_fig: str) -> None:
    cfg = load_config()["cluster"]
    adata = ad.read_h5ad(input_path)

    sc.pp.scale(adata, max_value=10)
    sc.tl.pca(adata, n_comps=cfg["n_pcs"])
    sc.pp.neighbors(adata, n_neighbors=cfg["n_neighbors"])
    sc.tl.umap(adata)
    sc.tl.leiden(adata, resolution=cfg["resolution"])

    adata.write_h5ad(output_h5)

    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt  # noqa: E402

    sc.pl.umap(adata, color=["leiden"], show=False)
    Path(output_fig).parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_fig, bbox_inches="tight", dpi=150)
    print(f"Cluster: {adata.obs['leiden'].nunique()} clusters")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], sys.argv[3])
