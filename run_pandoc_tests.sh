#!/bin/bash
# Run full Pandoc samples compatibility test with fresh output
#
# Usage: ./run_pandoc_tests.sh [--clean]
#   --clean: Remove all cached output files before running

set -e
cd "$(dirname "$0")"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "=========================================="
echo "  Pandoc Samples Compatibility Test"
echo "=========================================="

# Clean if requested
if [[ "$1" == "--clean" ]]; then
    echo -e "${YELLOW}Cleaning cached output files...${NC}"
    rm -f tests/samples/pandoc_outputs/*.tex
    rm -f tests/samples/pandoc_outputs/*.pdf
    rm -f tests/samples/pandoc_outputs/*.log
    rm -f tests/samples/pandoc_outputs/*.aux
    rm -f tests/samples/pandoc_outputs/*.out
    rm -f tests/samples/pandoc_outputs/compatibility_report.txt
    echo "Done."
fi

# Activate virtualenv
source venv/bin/activate

# Run the test
echo ""
echo "Running tests..."
echo ""

python -m pytest tests/samples/test_pandoc_samples.py::TestPandocSamplesReport -v -s 2>&1 | tee /tmp/pandoc_test_output.txt

# Show summary
echo ""
echo -e "${GREEN}Test complete!${NC}"
echo ""
echo "Report saved to: tests/samples/pandoc_outputs/compatibility_report.txt"
