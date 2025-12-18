#!/usr/bin/env python3
"""
Batch test script for docx2latex.

Tests conversion and LaTeX compilation on a sample of DOCX files.

Usage:
    python scripts/batch_test.py [OPTIONS]

Options:
    --dir PATH      Directory containing DOCX files (default: samples/)
    --count N       Number of files to test (default: 50)
    --compile       Also test LaTeX compilation (requires pdflatex)
    --output PATH   Output directory for generated files (default: tests/batch_test_output)
"""

import argparse
import random
import subprocess
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from docx2latex.application.dto.conversion_options import ConversionOptions
from docx2latex.application.services.conversion_service import ConversionService


def main():
    parser = argparse.ArgumentParser(description="Batch test docx2latex conversion")
    parser.add_argument("--dir", type=Path, default=Path("samples"), help="Directory with DOCX files")
    parser.add_argument("--count", type=int, default=50, help="Number of files to test")
    parser.add_argument("--compile", action="store_true", help="Test LaTeX compilation")
    parser.add_argument("--output", type=Path, default=Path("tests/batch_test_output"), help="Output directory")
    args = parser.parse_args()

    # Find DOCX files
    docx_dir = args.dir
    if not docx_dir.exists():
        print(f"Error: Directory {docx_dir} does not exist")
        sys.exit(1)

    all_docx = [f for f in docx_dir.glob("*.docx") if not f.name.startswith("~")]
    if not all_docx:
        print(f"No DOCX files found in {docx_dir}")
        sys.exit(1)

    # Sample files
    sample = random.sample(all_docx, min(args.count, len(all_docx)))
    print(f"Testing {len(sample)} files from {docx_dir}\n")

    # Setup
    args.output.mkdir(parents=True, exist_ok=True)
    service = ConversionService()

    convert_ok = 0
    latex_ok = 0
    errors = {}

    for i, docx in enumerate(sample):
        try:
            opts = ConversionOptions(output_dir=args.output)
            result = service.convert(docx, opts)

            if result.success:
                convert_ok += 1
                status = "OK"

                if args.compile and result.output_path:
                    # Test LaTeX compilation
                    proc = subprocess.run(
                        ["pdflatex", "-interaction=nonstopmode",
                         "-output-directory", str(args.output),
                         str(result.output_path)],
                        capture_output=True, text=True, timeout=60,
                        errors="replace"
                    )
                    if "! " not in proc.stdout:
                        latex_ok += 1
                        status = "OK+TEX"
                    else:
                        err_lines = [l for l in proc.stdout.split("\n") if l.startswith("!")]
                        if err_lines:
                            err_type = err_lines[0].split(":")[0] if ":" in err_lines[0] else err_lines[0][:40]
                            errors[err_type] = errors.get(err_type, 0) + 1
                        status = "OK/ERR"
            else:
                status = "FAIL"

            print(f"[{i+1:3d}/{len(sample)}] {status:8s} {docx.name[:60]}")

        except subprocess.TimeoutExpired:
            convert_ok += 1
            print(f"[{i+1:3d}/{len(sample)}] TIMEOUT  {docx.name[:60]}")
        except Exception as e:
            print(f"[{i+1:3d}/{len(sample)}] ERROR    {docx.name[:60]} - {e}")

    # Summary
    print(f"\n{'='*60}")
    print(f"Conversion: {convert_ok}/{len(sample)} ({convert_ok*100//len(sample)}%)")
    if args.compile:
        print(f"LaTeX OK:   {latex_ok}/{convert_ok} ({latex_ok*100//convert_ok if convert_ok else 0}%)")
        if errors:
            print(f"\nLaTeX error types:")
            for err, count in sorted(errors.items(), key=lambda x: -x[1])[:10]:
                print(f"  {count:3d}x {err}")


if __name__ == "__main__":
    main()
