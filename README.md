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
pip install -e .
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
# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Type checking
mypy src/

# Linting
ruff check src/
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
