# DOCX to LaTeX Converter - Project Plan

## Project Overview

**Goal:** Build a high-quality DOCX to LaTeX converter with excellent math formula support.

**Target Platforms:** Windows (x64), macOS (arm64, x64)

**Distribution:** Single binary via PyInstaller

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              PRESENTATION LAYER                              │
│                              (CLI with Typer)                                │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                            APPLICATION LAYER                                 │
│                     (ConversionService, Use Cases)                          │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                              DOMAIN LAYER                                    │
│              (Entities, Value Objects, Protocols - NO DEPENDENCIES)         │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                          INFRASTRUCTURE LAYER                                │
│           (DocxParser, Converters, LatexWriter, AssetManager)               │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Tech Stack

| Component | Library | Purpose |
|-----------|---------|---------|
| DOCX Parsing | `lxml` + `python-docx` | Direct XML access |
| Math Conversion | Custom OMML→LaTeX | High-fidelity formulas |
| Images | `Pillow` | Format conversion |
| CLI | `Typer` + `Rich` | Modern CLI |
| Config | `Pydantic` | Type-safe config |
| Templates | `Jinja2` | LaTeX templates |
| Packaging | `PyInstaller` | Binary distribution |

---

## Roadmap

### Phase 1: Foundation ✅ COMPLETE
- [x] Project structure with pyproject.toml
- [x] Modern tooling (ruff, mypy strict)
- [x] Shared kernel (Result, constants, exceptions)

### Phase 2: Domain Layer ✅ COMPLETE
- [x] Value Objects (Dimension, Color, Font, Style, Layout)
- [x] Entities (Run, Paragraph, Table, Math, Image, List)
- [x] Document aggregate root
- [x] Protocols (IDocumentParser, IElementConverter, ILatexWriter)

### Phase 3: Infrastructure - Parser ✅ COMPLETE
- [x] XML namespace manager
- [x] DOCX zip extraction
- [x] document.xml parser
- [x] styles.xml parser (inheritance)
- [x] relationships parser
- [x] Section properties

### Phase 4: Infrastructure - Converters ✅ COMPLETE
- [x] Base converter (template method)
- [x] Converter registry (factory)
- [x] Paragraph converter
- [x] **Math converter** (CRITICAL)
- [x] Table converter
- [x] List converter
- [x] Image converter

### Phase 5: Infrastructure - LaTeX Writer ✅ COMPLETE
- [x] Document builder
- [x] Preamble generator
- [x] Jinja2 templates
- [x] Safe text escaping

### Phase 6: Application Layer ✅ COMPLETE
- [x] ConversionService
- [x] ConversionOptions DTO
- [x] ConversionResult DTO

### Phase 7: Presentation Layer ✅ COMPLETE
- [x] CLI commands
- [x] DI container
- [x] Progress display

### Phase 8: Packaging ✅ COMPLETE
- [x] PyInstaller config
- [x] Setup scripts (setup.bat, setup.sh)
- [x] Windows build
- [x] macOS builds

### Phase 9: Testing ✅ COMPLETE
- [x] Unit tests (9 tests)
- [x] Integration tests (3 tests)
- [x] Math test suite
- [x] Pandoc compatibility tests (64/64 = 100%)

---

## Project Status: COMPLETE ✅

**All phases complete.** The converter achieves:
- **100% compilation success** on Pandoc test suite (64/64 files)
- Full CJK (Chinese/Japanese/Korean) character support
- Comprehensive math formula conversion (OMML to LaTeX)

---

## Math Conversion Pipeline

```
OMML (Word XML)
      │
      ▼ [Parse structure]
Internal AST
      │
      ▼ [Element handlers]
LaTeX primitives
      │
      ▼ [Optimize]
Clean amsmath output
```

### Math Features to Support

| Feature | LaTeX Output | Priority |
|---------|-------------|----------|
| Fractions | `\frac{}{}`, `\dfrac` | HIGH |
| Subscripts | `x_{i}` | HIGH |
| Superscripts | `x^{2}` | HIGH |
| Square roots | `\sqrt{}`, `\sqrt[n]{}` | HIGH |
| Greek letters | `\alpha`, `\beta` | HIGH |
| Matrices | `\begin{pmatrix}` | HIGH |
| Integrals | `\int_{}^{}` | HIGH |
| Summations | `\sum_{}^{}` | HIGH |
| Limits | `\lim_{}` | MEDIUM |
| Accents | `\hat{}`, `\bar{}` | MEDIUM |
| Brackets | `\left( \right)` | HIGH |
| Functions | `\sin`, `\cos`, `\log` | HIGH |

---

## Quality Results

| Metric | Target | Achieved |
|--------|--------|----------|
| Pandoc test suite | - | 100% (64/64) |
| Math accuracy | > 95% | ✅ |
| Table support | Merged cells, borders | ✅ |
| Image handling | PNG, JPG, PDF | ✅ |
| Style preservation | Bold, italic, colors | ✅ |
| List nesting | Up to 5 levels | ✅ |
| CJK support | - | ✅ |

---

## Commands Reference

```bash
# Setup (creates venv + installs dependencies)
setup.bat          # Windows
./setup.sh         # Linux/macOS

# Development
python -m pytest
python -m mypy src/
python -m ruff check src/

# Usage
docx2latex convert input.docx -o output.tex
docx2latex convert input.docx -o output/ --extract-images

# Build
python scripts/build.py
```

---

## File Structure

```
docx2latex/
├── PLAN.md              # This file - project plan
├── TRACKING.md          # Progress tracking
├── pyproject.toml       # Dependencies & config
├── setup.bat            # Windows setup script
├── setup.sh             # Linux/macOS setup script
├── src/docx2latex/
│   ├── shared/          # Result, constants, exceptions
│   ├── domain/          # Entities, value objects, protocols
│   ├── application/     # Services, use cases
│   ├── infrastructure/  # Parser, converters, writer
│   └── presentation/    # CLI
├── tests/
└── scripts/             # Build scripts
```
