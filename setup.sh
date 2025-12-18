#!/bin/bash
set -e

echo "Creating virtual environment..."
python3 -m venv venv

echo "Activating virtual environment..."
source venv/bin/activate

echo "Installing dependencies..."
pip install -e ".[dev]"

echo ""
echo "Setup complete! Virtual environment is active."
echo ""
echo "To activate later, run: source venv/bin/activate"
echo "To run tests: python -m pytest"
echo "To run the tool: docx2latex --help"
