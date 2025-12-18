#!/usr/bin/env python3
"""
Build script for creating standalone executables with PyInstaller.

Creates executables for Windows and macOS.
"""

import platform
import shutil
import subprocess
import sys
from pathlib import Path

# Project root
PROJECT_ROOT = Path(__file__).parent.parent
SRC_DIR = PROJECT_ROOT / "src"
DIST_DIR = PROJECT_ROOT / "dist"
BUILD_DIR = PROJECT_ROOT / "build"


def get_platform_name() -> str:
    """Get platform identifier for filename."""
    system = platform.system().lower()
    machine = platform.machine().lower()

    if system == "darwin":
        if machine == "arm64":
            return "macos-arm64"
        return "macos-x64"
    elif system == "windows":
        return "windows-x64"
    elif system == "linux":
        return "linux-x64"
    return f"{system}-{machine}"


def clean_build() -> None:
    """Clean previous build artifacts."""
    print("Cleaning previous builds...")

    if BUILD_DIR.exists():
        shutil.rmtree(BUILD_DIR)

    # Clean PyInstaller artifacts
    spec_files = list(PROJECT_ROOT.glob("*.spec"))
    for spec in spec_files:
        spec.unlink()


def build_executable() -> Path:
    """Build the executable using PyInstaller."""
    print(f"Building for {get_platform_name()}...")

    # Ensure dist directory exists
    DIST_DIR.mkdir(exist_ok=True)

    # Build command
    cmd = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--onefile",
        "--name",
        f"docx2latex-{get_platform_name()}",
        "--clean",
        "--noconfirm",
        # Add data files
        "--add-data",
        f"{SRC_DIR / 'docx2latex' / 'infrastructure' / 'writing' / 'templates'}:docx2latex/infrastructure/writing/templates",
        # Hidden imports that PyInstaller might miss
        "--hidden-import",
        "lxml.etree",
        "--hidden-import",
        "PIL",
        "--hidden-import",
        "jinja2",
        # Entry point
        f"{SRC_DIR / 'docx2latex' / 'presentation' / 'cli' / 'app.py'}",
    ]

    # Add icon on Windows
    if platform.system() == "Windows":
        icon_path = PROJECT_ROOT / "assets" / "icon.ico"
        if icon_path.exists():
            cmd.extend(["--icon", str(icon_path)])

    # Add icon on macOS
    if platform.system() == "Darwin":
        icon_path = PROJECT_ROOT / "assets" / "icon.icns"
        if icon_path.exists():
            cmd.extend(["--icon", str(icon_path)])

    # Run PyInstaller
    result = subprocess.run(cmd, cwd=PROJECT_ROOT)

    if result.returncode != 0:
        print("Build failed!")
        sys.exit(1)

    # Find output
    platform_name = get_platform_name()
    if platform.system() == "Windows":
        output_name = f"docx2latex-{platform_name}.exe"
    else:
        output_name = f"docx2latex-{platform_name}"

    output_path = DIST_DIR / output_name

    if output_path.exists():
        print(f"Build successful: {output_path}")
        print(f"Size: {output_path.stat().st_size / 1024 / 1024:.1f} MB")
        return output_path
    else:
        print("Build output not found!")
        sys.exit(1)


def main() -> None:
    """Main build process."""
    import argparse

    parser = argparse.ArgumentParser(description="Build docx2latex executable")
    parser.add_argument("--clean", action="store_true", help="Clean build artifacts only")
    parser.add_argument("--no-clean", action="store_true", help="Don't clean before build")
    args = parser.parse_args()

    if args.clean:
        clean_build()
        return

    if not args.no_clean:
        clean_build()

    output = build_executable()
    print(f"\nExecutable created: {output}")


if __name__ == "__main__":
    main()
