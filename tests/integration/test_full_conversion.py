"""Integration tests for full document conversion."""

from pathlib import Path

import pytest

from docx2latex.application.dto.conversion_options import ConversionOptions
from docx2latex.application.services.conversion_service import ConversionService
from docx2latex.infrastructure.parsing.docx_parser import DocxParser
from docx2latex.shared.result import Ok


class TestDocxParser:
    """Tests for DOCX parsing."""

    def test_parse_sample_file(self, sample_dir: Path) -> None:
        """Test parsing a real DOCX file."""
        # Find a sample file
        samples = list(sample_dir.glob("*.docx"))
        # Skip temp files
        samples = [s for s in samples if not s.name.startswith("~")]

        if not samples:
            pytest.skip("No sample DOCX files found")

        parser = DocxParser()
        result = parser.parse(samples[0])

        assert isinstance(result, Ok), f"Parse failed: {result}"
        doc = result.value

        # Basic sanity checks
        assert doc.paragraph_count >= 0
        assert len(doc.sections) >= 1


class TestConversionService:
    """Tests for the conversion service."""

    def test_convert_sample_file(self, sample_dir: Path, output_dir: Path) -> None:
        """Test converting a real DOCX file."""
        # Find a sample file
        samples = list(sample_dir.glob("*.docx"))
        samples = [s for s in samples if not s.name.startswith("~")]

        if not samples:
            pytest.skip("No sample DOCX files found")

        service = ConversionService()
        options = ConversionOptions(output_dir=output_dir)

        result = service.convert(samples[0], options)

        assert result.success, f"Conversion failed: {result.errors}"
        assert result.output_path is not None
        assert result.output_path.exists()

        # Check output content
        content = result.output_path.read_text()
        assert r"\documentclass" in content
        assert r"\begin{document}" in content
        assert r"\end{document}" in content

    def test_convert_all_samples(self, sample_dir: Path, output_dir: Path) -> None:
        """Test converting all sample files."""
        samples = list(sample_dir.glob("*.docx"))
        samples = [s for s in samples if not s.name.startswith("~")]

        if not samples:
            pytest.skip("No sample DOCX files found")

        service = ConversionService()

        for sample in samples:
            output_path = output_dir / f"{sample.stem}.tex"
            options = ConversionOptions(output_path=output_path)

            result = service.convert(sample, options)

            # Conversion should succeed (or have warnings, not errors)
            assert result.success or len(result.errors) == 0, (
                f"Failed to convert {sample.name}: {result.errors}"
            )

            if result.success:
                assert result.output_path is not None
                print(f"Converted {sample.name}: {result.paragraph_count} paragraphs, "
                      f"{result.math_count} math blocks")
