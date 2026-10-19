"""QC: filter cells/genes, compute QC metrics, drop low-quality cells."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import anndata as ad  # noqa: E402
import scanpy as sc  # noqa: E402
from common import load_config  # noqa: E402


def main(input_path: str, output_path: str) -> None:
    cfg = load_config()["qc"]
    adata = ad.read_h5ad(input_path)
    adata.var_names_make_unique()

    sc.pp.filter_cells(adata, min_genes=cfg["min_genes"])
    sc.pp.filter_genes(adata, min_cells=cfg["min_cells"])

    adata.var["mt"] = adata.var_names.str.startswith("MT-")
    sc.pp.calculate_qc_metrics(adata, qc_vars=["mt"], inplace=True)

    adata = adata[adata.obs["n_genes_by_counts"] < cfg["max_genes"], :]
    adata = adata[adata.obs["pct_counts_mt"] < cfg["max_pct_mt"], :]

    adata.write_h5ad(output_path)
    print(f"QC: {adata.n_obs} cells x {adata.n_vars} genes")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
