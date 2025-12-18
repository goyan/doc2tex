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
    --retest-failed Re-test only files that failed in previous run (reads from failed.txt)
    --save-failed   Save failed files to failed.txt for later re-testing
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
    parser.add_argument("--retest-failed", action="store_true", help="Re-test only previously failed files")
    parser.add_argument("--save-failed", action="store_true", help="Save failed files to failed.txt")
    args = parser.parse_args()

    failed_file = args.output / "failed.txt"

    # Find DOCX files
    docx_dir = args.dir
    if not docx_dir.exists():
        print(f"Error: Directory {docx_dir} does not exist")
        sys.exit(1)

    if args.retest_failed:
        # Read failed files from previous run
        if not failed_file.exists():
            print(f"No failed.txt found in {args.output}")
            sys.exit(1)
        failed_names = failed_file.read_text().strip().split("\n")
        all_docx = [docx_dir / name for name in failed_names if (docx_dir / name).exists()]
        if not all_docx:
            print("No failed files found to re-test")
            sys.exit(0)
        sample = all_docx
        print(f"Re-testing {len(sample)} previously failed files\n")
    else:
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
    failed_files = []

    for i, docx in enumerate(sample):
        try:
            opts = ConversionOptions(output_dir=args.output)
            result = service.convert(docx, opts)

            if result.success:
                convert_ok += 1
                status = "OK"
                is_failed = False

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
                        is_failed = True
            else:
                status = "FAIL"
                is_failed = True

            if is_failed:
                failed_files.append(docx.name)

            print(f"[{i+1:3d}/{len(sample)}] {status:8s} {docx.name[:60]}")

        except subprocess.TimeoutExpired:
            convert_ok += 1
            failed_files.append(docx.name)
            print(f"[{i+1:3d}/{len(sample)}] TIMEOUT  {docx.name[:60]}")
        except Exception as e:
            failed_files.append(docx.name)
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

    # Save failed files
    if args.save_failed and failed_files:
        failed_file.write_text("\n".join(failed_files))
        print(f"\nSaved {len(failed_files)} failed files to {failed_file}")
        print(f"Re-run with --retest-failed to test only these files")


if __name__ == "__main__":
    main()
