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

### Phase 2: Domain Layer 🔄 IN PROGRESS
- [x] Value Objects (Dimension, Color, Font, Style, Layout)
- [x] Entities (Run, Paragraph, Table, Math, Image, List)
- [ ] Document aggregate root
- [ ] Protocols (IDocumentParser, IElementConverter, ILatexWriter)

### Phase 3: Infrastructure - Parser ⏳ NEXT
- [ ] XML namespace manager
- [ ] DOCX zip extraction
- [ ] document.xml parser
- [ ] styles.xml parser (inheritance)
- [ ] relationships parser
- [ ] Section properties

### Phase 4: Infrastructure - Converters
- [ ] Base converter (template method)
- [ ] Converter registry (factory)
- [ ] Paragraph converter
- [ ] **Math converter** (CRITICAL)
- [ ] Table converter
- [ ] List converter
- [ ] Image converter

### Phase 5: Infrastructure - LaTeX Writer
- [ ] Document builder
- [ ] Preamble generator
- [ ] Jinja2 templates
- [ ] Safe text escaping

### Phase 6: Application Layer
- [ ] ConversionService
- [ ] ConversionOptions DTO
- [ ] ConversionResult DTO

### Phase 7: Presentation Layer
- [ ] CLI commands
- [ ] DI container
- [ ] Progress display

### Phase 8: Packaging
- [ ] PyInstaller config
- [ ] Windows build
- [ ] macOS builds

### Phase 9: Testing
- [ ] Unit tests
- [ ] Integration tests
- [ ] Math test suite

---

## Current Sprint Tasks

### Now (Session 1)
1. ✅ Create project structure
2. ✅ Implement shared kernel
3. ✅ Implement value objects
4. ✅ Implement element entities
5. 🔄 Implement Document entity
6. ⏳ Implement Protocols
7. ⏳ Start DOCX Parser

### Next
1. Complete DOCX Parser
2. Implement Paragraph Converter
3. Implement Math Converter (high priority)
4. Implement Table Converter

---

## Critical Path

```
Domain Layer → DOCX Parser → Math Converter → LaTeX Writer → CLI → Build
     ↓              ↓              ↓
   (now)        (next)       (critical)
```

**Math Converter is the critical component** - this is where conversion quality is won or lost.

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

## Quality Targets

| Metric | Target |
|--------|--------|
| Math accuracy | > 95% correct LaTeX |
| Table support | Merged cells, borders |
| Image handling | PNG, JPG, PDF |
| Style preservation | Bold, italic, colors |
| List nesting | Up to 5 levels |

---

## Commands Reference

```bash
# Development
pip install -e ".[dev]"
pytest
mypy src/
ruff check src/

# Usage (after completion)
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
├── src/docx2latex/
│   ├── shared/          # Result, constants, exceptions
│   ├── domain/          # Entities, value objects, protocols
│   ├── application/     # Services, use cases
│   ├── infrastructure/  # Parser, converters, writer
│   └── presentation/    # CLI
├── tests/
└── scripts/             # Build scripts
```
