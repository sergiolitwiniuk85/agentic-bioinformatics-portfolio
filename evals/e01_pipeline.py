"""E01 eval gate: pipeline correctness + reproducibility + privacy.

Checks:
1. Correctness — expected PBMC cell-type markers appear in the DE output.
2. Reproducibility — recorded artifact hashes match recomputed hashes.
3. Privacy — no obvious PII / raw cell barcodes leak into outputs.

Usage:
    python evals/e01_pipeline.py
"""

import hashlib
import json
import re
import sys
from pathlib import Path

import pandas as pd

REPO = Path(__file__).resolve().parents[1]
MARKERS = REPO / "results/de/pbmc3k_markers.csv"
PROV = REPO / "results/report/provenance.json"

EXPECTED_MARKERS = [
    "CD3D", "CD3E", "IL7R",  # T cells
    "MS4A1", "CD79A", "CD79B",  # B cells
    "LYZ", "CD14", "S100A8",  # monocytes
    "NKG7", "GNLY", "KLRD1",  # NK cells
    "PPBP", "PF4",  # megakaryocytes
    "FCER1A", "CST3",  # dendritic
]

PII_PATTERNS = [
    re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"),
    re.compile(r"AAAC[A-Z0-9-]{12,}"),  # 10x cell barcodes
]


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()


def logical_fingerprint(adata) -> str:
    labels = ",".join(sorted(adata.obs["leiden"].astype(str).tolist()))
    payload = f"{labels}|cells={adata.n_obs}|genes={adata.n_vars}"
    return hashlib.sha256(payload.encode()).hexdigest()


def check_correctness() -> tuple[bool, int]:
    markers = pd.read_csv(MARKERS)
    found = set(markers["gene"].str.upper())
    hits = [m for m in EXPECTED_MARKERS if m in found]
    n = len(hits)
    ok = n >= 6
    print(f"[correctness] {n}/{len(EXPECTED_MARKERS)} expected markers found: {hits}")
    return ok, n


def check_reproducibility() -> bool:
    import anndata as ad

    prov = json.loads(PROV.read_text())
    all_ok = True
    for name, meta in prov["artifacts"].items():
        if name == "cluster":
            adata = ad.read_h5ad(REPO / meta["path"])
            actual = logical_fingerprint(adata)
            expected = meta["logical_sha256"]
        else:
            actual = sha256(REPO / meta["path"])
            expected = meta["sha256"]
        match = actual == expected
        all_ok &= match
        print(f"[reproducibility] {name}: {'match' if match else 'MISMATCH'}")
    return all_ok


def check_privacy() -> bool:
    text = MARKERS.read_text() + PROV.read_text()
    for pattern in PII_PATTERNS:
        m = pattern.search(text)
        if m:
            print(f"[privacy] FAIL — suspicious pattern: {m.group(0)}")
            return False
    print("[privacy] no obvious PII / raw cell barcodes found")
    return True


def main() -> None:
    print("=== E01 eval gate ===")
    ok_c, _ = check_correctness()
    ok_r = check_reproducibility()
    ok_p = check_privacy()
    passed = ok_c and ok_r and ok_p
    print(f"=== RESULT: {'PASS' if passed else 'FAIL'} ===")
    sys.exit(0 if passed else 1)


if __name__ == "__main__":
    main()
