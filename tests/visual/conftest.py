"""Pytest configuration for visual validation tests."""

from pathlib import Path

import pytest


def pytest_addoption(parser: pytest.Parser) -> None:
    """Add custom command line options for visual tests."""
    parser.addoption(
        "--update-baselines",
        action="store_true",
        default=False,
        help="Update baseline images with current output",
    )
    parser.addoption(
        "--generate-only",
        action="store_true",
        default=False,
        help="Generate screenshots without comparison",
    )


@pytest.fixture
def update_baselines(request: pytest.FixtureRequest) -> bool:
    """Return True if baselines should be updated."""
    return bool(request.config.getoption("--update-baselines", default=False))


@pytest.fixture
def generate_only(request: pytest.FixtureRequest) -> bool:
    """Return True if only generating screenshots (no comparison)."""
    return bool(request.config.getoption("--generate-only", default=False))


@pytest.fixture
def sample_dir() -> Path:
    """Return path to sample DOCX files."""
    return Path(__file__).parent.parent.parent / "samples"
