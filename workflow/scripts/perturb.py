"""Perturbation-style analysis: pathway activity via decoupler PROGENy."""

import sys
from pathlib import Path

import anndata as ad
import decoupler as dc

from common import load_config


def main(input_path: str, output_csv: str) -> None:
    cfg = load_config()["perturbation"]
    adata = ad.read_h5ad(input_path)

    progeny = dc.op.progeny(organism="human", top=cfg["top"])
    dc.mt.mlm(adata, progeny, verbose=False)

    df = adata.obsm["score_mlm"]
    df["leiden"] = adata.obs["leiden"].values
    summary = df.groupby("leiden").mean()

    Path(output_csv).parent.mkdir(parents=True, exist_ok=True)
    summary.to_csv(output_csv)
    print(f"Perturbation: PROGENy activity per cluster -> {output_csv}")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
