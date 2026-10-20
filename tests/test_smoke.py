"""Smoke tests for the package (beta v1)."""

from agentic_bio import __version__


def test_version():
    assert __version__ == "1.0.0"
