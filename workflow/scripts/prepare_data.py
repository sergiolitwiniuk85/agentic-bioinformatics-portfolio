"""Download + cache the two dataset fixtures and write a checksum manifest."""

import json
import sys
from pathlib import Path

import scanpy as sc


def sha256(path: Path) -> str:
    import hashlib

    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()


def main(raw_dir: str, manifest_path: str) -> None:
    raw = Path(raw_dir)
    raw.mkdir(parents=True, exist_ok=True)

    pbmc_path = raw / "pbmc3k.h5ad"
    if not pbmc_path.exists():
        sc.datasets.pbmc3k().write_h5ad(pbmc_path)

    vis_path = raw / "visium_sge.h5ad"
    if not vis_path.exists():
        sc.datasets.visium_sge(sample_id="V1_Human_Lymph_Node").write_h5ad(vis_path)

    manifest = {
        pbmc_path.name: sha256(pbmc_path),
        vis_path.name: sha256(vis_path),
    }
    Path(manifest_path).write_text(json.dumps(manifest, indent=2))
    print(f"Manifest written to {manifest_path}")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
