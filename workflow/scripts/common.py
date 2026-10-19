"""Shared helpers for pipeline scripts."""

from __future__ import annotations

import hashlib
from pathlib import Path

import yaml

_CONFIG_PATH = Path(__file__).resolve().parents[1] / "config.yaml"


def load_config() -> dict:
    with _CONFIG_PATH.open() as f:
        return yaml.safe_load(f)


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()
