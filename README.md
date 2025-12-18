# DOCX to LaTeX Converter

High-quality DOCX to LaTeX converter with excellent math formula support.

## Features

- **High-quality math conversion**: OMML to LaTeX with support for fractions, matrices, integrals, Greek letters, and more
- **Table support**: Including merged cells, borders, and booktabs styling
- **Image handling**: Automatic extraction and proper sizing
- **List support**: Bulleted and numbered lists with nesting
- **Style preservation**: Bold, italic, colors, fonts
- **Cross-platform**: Windows, macOS, and Linux support

## Installation

```bash
pip install docx2latex
```

Or install from source:

```bash
git clone https://github.com/user/docx2latex
cd docx2latex

# Windows
setup.bat

# Linux/macOS
chmod +x setup.sh && ./setup.sh
```

This creates a virtual environment and installs all dependencies.

**Manual setup:**

```bash
# Create and activate venv
python -m venv venv
venv\Scripts\activate      # Windows
source venv/bin/activate   # Linux/macOS

# Install
pip install -e ".[dev]"
```

## Usage

### Command Line

```bash
# Basic conversion
docx2latex convert document.docx

# Specify output file
docx2latex convert document.docx -o output.tex

# Specify output directory
docx2latex convert document.docx -d output_folder/

# Show document info without converting
docx2latex info document.docx
```

### Python API

```python
from pathlib import Path
from docx2latex import ConversionService
from docx2latex.application.dto import ConversionOptions

# Create service
service = ConversionService()

# Convert with default options
result = service.convert(Path("document.docx"))

if result.success:
    print(f"Converted to: {result.output_path}")
    print(f"Paragraphs: {result.paragraph_count}")
    print(f"Math blocks: {result.math_count}")
else:
    print(f"Error: {result.errors}")

# Convert with custom options
options = ConversionOptions(
    output_path=Path("output.tex"),
    document_class="report",
    font_size=12,
)
result = service.convert(Path("document.docx"), options)
```

## Supported Elements

| Element | Support |
|---------|---------|
| Paragraphs | Full |
| Headings | Full (section, subsection, etc.) |
| Bold/Italic | Full |
| Colors | Full (requires xcolor) |
| Hyperlinks | Full |
| Math formulas | Full (OMML to LaTeX) |
| Tables | Full (including merged cells) |
| Lists | Full (nested) |
| Images | Full (PNG, JPG, PDF) |
| CJK characters | Full (Chinese, Japanese, Korean) |

## Compatibility

Tested against Pandoc's DOCX test suite (78 files):

| Metric | Result |
|--------|--------|
| Conversion success | 98% (64/65) |
| Compilation success | 100% (64/64) |

The only conversion failure is a malformed test file with missing `document.xml`.

## Math Conversion

The converter supports comprehensive math formula conversion:

- Fractions (`\frac`, `\dfrac`)
- Subscripts and superscripts
- Square roots and nth roots
- Matrices and determinants
- Integrals, sums, products
- Greek letters
- Mathematical operators
- Brackets with auto-sizing
- Equation arrays

## Development

```bash
# Run tests
python -m pytest

# Run Pandoc compatibility tests (requires pdflatex)
python run_pandoc_tests.py --clean

# Type checking
python -m mypy src/

# Linting
python -m ruff check src/
```

### CJK Support

For Chinese/Japanese/Korean character support, install the TeX Live CJK packages:

```bash
# macOS/Linux
sudo tlmgr install collection-langchinese

# Windows (run as Administrator)
tlmgr install collection-langchinese
```

## Building Executables

```bash
# Install build dependencies
pip install -e ".[build]"

# Build for current platform
python scripts/build.py
```

## License

MIT License
