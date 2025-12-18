"""
Main conversion service.

Orchestrates the full DOCX to LaTeX conversion pipeline.
"""

from __future__ import annotations

import time
from pathlib import Path
from typing import TYPE_CHECKING

from docx2latex.application.dto.conversion_options import ConversionOptions
from docx2latex.application.dto.conversion_result import ConversionResult
from docx2latex.domain.entities.elements import Image, ListBlock, Paragraph, Table
from docx2latex.domain.protocols.converter import ConversionContext
from docx2latex.infrastructure.converters.registry import create_default_registry
from docx2latex.infrastructure.parsing.docx_parser import DocxParser
from docx2latex.infrastructure.writing.latex_writer import LatexWriter
from docx2latex.shared.logging import get_logger
from docx2latex.shared.result import Err, Ok

if TYPE_CHECKING:
    from docx2latex.domain.entities.document import Document
    from docx2latex.infrastructure.converters.registry import ConverterRegistry

logger = get_logger("service")


class ConversionService:
    """
    Main service for converting DOCX documents to LaTeX.

    Orchestrates parsing, conversion, and writing steps.
    """

    def __init__(
        self,
        parser: DocxParser | None = None,
        registry: ConverterRegistry | None = None,
        writer: LatexWriter | None = None,
    ) -> None:
        """
        Initialize the conversion service.

        Args:
            parser: Document parser (default: DocxParser)
            registry: Converter registry (default: create_default_registry)
            writer: LaTeX writer (default: LatexWriter)
        """
        self._parser = parser or DocxParser()
        self._registry = registry or create_default_registry()
        self._writer = writer or LatexWriter()

    def convert(
        self,
        input_path: Path,
        options: ConversionOptions | None = None,
    ) -> ConversionResult:
        """
        Convert a DOCX file to LaTeX.

        Args:
            input_path: Path to the DOCX file
            options: Conversion options

        Returns:
            ConversionResult with output path and statistics
        """
        options = options or ConversionOptions()
        result = ConversionResult()

        # Determine output paths
        output_path = options.get_output_path(input_path)
        output_dir = options.get_output_dir(input_path)

        # Step 1: Parse DOCX
        logger.info(f"Parsing: {input_path}")
        start_time = time.perf_counter()

        parse_result = self._parser.parse(input_path)
        result.parse_time_ms = (time.perf_counter() - start_time) * 1000

        if isinstance(parse_result, Err):
            result.success = False
            result.errors.append(f"Parse error: {parse_result.error}")
            return result

        document = parse_result.value
        logger.info(f"Parsed: {document.paragraph_count} paragraphs, {document.table_count} tables")

        # Step 2: Convert to LaTeX
        logger.info("Converting to LaTeX...")
        start_time = time.perf_counter()

        context = ConversionContext(
            document=document,
            output_dir=output_dir,
            image_dir=options.image_dir,
            options={
                "extract_images": options.extract_images,
                "display_math_style": options.display_math_style,
            },
        )

        latex_content = self._convert_document(document, context)
        result.convert_time_ms = (time.perf_counter() - start_time) * 1000

        # Collect statistics
        result.paragraph_count = document.paragraph_count
        result.table_count = document.table_count
        result.image_count = document.image_count
        result.math_count = document.math_count

        # Collect warnings
        result.warnings = context.warnings.copy()

        # Step 3: Write output
        logger.info(f"Writing: {output_path}")
        start_time = time.perf_counter()

        write_result = self._writer.write(latex_content, context, output_path)
        result.write_time_ms = (time.perf_counter() - start_time) * 1000

        if isinstance(write_result, Err):
            result.success = False
            result.errors.append(f"Write error: {write_result.error}")
            return result

        result.output_path = write_result.value
        result.success = True

        logger.info(f"Conversion complete in {result.total_time_ms:.0f}ms")

        return result

    def _convert_document(
        self, document: Document, context: ConversionContext
    ) -> str:
        """
        Convert document content to LaTeX.

        Args:
            document: Parsed document
            context: Conversion context

        Returns:
            LaTeX content string
        """
        parts = []

        for section in document.sections:
            section_content = self._convert_section_elements(
                section.elements, context
            )
            parts.append(section_content)

            # Add section break if there are multiple sections
            if len(document.sections) > 1:
                parts.append("\n\\clearpage\n")

        return "\n\n".join(parts)

    def _convert_section_elements(
        self,
        elements: list[Paragraph | Table | ListBlock | Image],
        context: ConversionContext,
    ) -> str:
        """
        Convert a list of section elements.

        Args:
            elements: Section elements
            context: Conversion context

        Returns:
            LaTeX content for the section
        """
        parts = []

        for element in elements:
            result = self._registry.convert(element, context)
            if isinstance(result, Ok):
                content = result.value.strip()
                if content:
                    parts.append(content)

        return "\n\n".join(parts)

    def convert_bytes(
        self,
        data: bytes,
        output_path: Path,
        options: ConversionOptions | None = None,
    ) -> ConversionResult:
        """
        Convert DOCX data from bytes.

        Args:
            data: DOCX file bytes
            output_path: Output path for LaTeX file
            options: Conversion options

        Returns:
            ConversionResult
        """
        options = options or ConversionOptions()
        options.output_path = output_path
        result = ConversionResult()

        # Parse
        parse_result = self._parser.parse_bytes(data)
        if isinstance(parse_result, Err):
            result.success = False
            result.errors.append(f"Parse error: {parse_result.error}")
            return result

        document = parse_result.value

        # Convert
        output_dir = output_path.parent
        context = ConversionContext(
            document=document,
            output_dir=output_dir,
            image_dir=options.image_dir,
        )

        latex_content = self._convert_document(document, context)

        # Write
        write_result = self._writer.write(latex_content, context, output_path)
        if isinstance(write_result, Err):
            result.success = False
            result.errors.append(f"Write error: {write_result.error}")
            return result

        result.output_path = write_result.value
        result.success = True
        result.warnings = context.warnings.copy()

        return result
