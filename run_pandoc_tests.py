#!/usr/bin/env python3
"""
Run full Pandoc samples compatibility test with fresh output.

Usage:
    python run_pandoc_tests.py [--clean]

Options:
    --clean     Remove all cached output files before running
"""

import subprocess
import sys
from pathlib import Path

# Get project root directory
PROJECT_ROOT = Path(__file__).parent.resolve()
OUTPUT_DIR = PROJECT_ROOT / "tests" / "samples" / "pandoc_outputs"


def clean_outputs():
    """Remove cached output files."""
    print("Cleaning cached output files...")
    extensions = [".tex", ".pdf", ".log", ".aux", ".out"]
    count = 0
    for ext in extensions:
        for f in OUTPUT_DIR.glob(f"*{ext}"):
            f.unlink()
            count += 1

    report = OUTPUT_DIR / "compatibility_report.txt"
    if report.exists():
        report.unlink()
        count += 1

    print(f"Removed {count} files.")


def run_tests():
    """Run the pandoc samples test."""
    print("\n" + "=" * 50)
    print("  Pandoc Samples Compatibility Test")
    print("=" * 50 + "\n")

    # Run pytest
    result = subprocess.run(
        [
            sys.executable, "-m", "pytest",
            "tests/samples/test_pandoc_samples.py::TestPandocSamplesReport",
            "-v", "-s"
        ],
        cwd=PROJECT_ROOT,
    )

    print("\n" + "=" * 50)
    if result.returncode == 0:
        print("Test complete!")
    else:
        print("Test failed!")
    print("=" * 50)

    report = OUTPUT_DIR / "compatibility_report.txt"
    if report.exists():
        print(f"\nReport saved to: {report}")

    return result.returncode


def main():
    if "--clean" in sys.argv:
        clean_outputs()

    return run_tests()


if __name__ == "__main__":
    sys.exit(main())
