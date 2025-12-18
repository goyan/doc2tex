"""Pytest configuration and fixtures."""

from pathlib import Path

import pytest


@pytest.fixture
def sample_dir() -> Path:
    """Return path to sample DOCX files."""
    return Path(__file__).parent.parent / "samples"


@pytest.fixture
def output_dir(tmp_path: Path) -> Path:
    """Return temporary output directory."""
    output = tmp_path / "output"
    output.mkdir()
    return output
