"""Normalize: total-count normalize, log1p, select highly variable genes."""

import sys

import anndata as ad
import scanpy as sc

from common import load_config


def main(input_path: str, output_path: str) -> None:
    cfg = load_config()["normalize"]
    adata = ad.read_h5ad(input_path)

    sc.pp.normalize_total(adata, target_sum=cfg["target_sum"])
    sc.pp.log1p(adata)
    sc.pp.highly_variable_genes(adata, n_top_genes=cfg["n_top_genes"])

    adata.write_h5ad(output_path)
    print(f"Normalize: {adata.n_obs} cells, HVG selected")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
