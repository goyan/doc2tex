"""
Math element converter.

Converts MathBlock entities to LaTeX using the OMML parser.
"""

from __future__ import annotations

from docx2latex.domain.entities.elements import DocumentElement, MathBlock
from docx2latex.domain.protocols.converter import ConversionContext
from docx2latex.domain.value_objects.style import MathType
from docx2latex.infrastructure.converters.base import BaseConverter
from docx2latex.infrastructure.converters.math.omml_parser import OmmlParser
from docx2latex.shared.logging import get_logger
from docx2latex.shared.result import Ok, Result

logger = get_logger("math")


class MathConverter(BaseConverter[MathBlock]):
    """
    Converter for math blocks.

    Transforms OMML XML to LaTeX math notation.
    """

    def __init__(self) -> None:
        self._parser = OmmlParser()

    @property
    def element_type(self) -> str:
        return "math"

    def can_convert(self, element: DocumentElement) -> bool:
        return isinstance(element, MathBlock)

    def do_convert(
        self, element: MathBlock, context: ConversionContext
    ) -> Result[str, str]:
        """
        Convert a math block to LaTeX.

        Args:
            element: MathBlock to convert
            context: Conversion context

        Returns:
            Result containing LaTeX math string
        """
        # Ensure amsmath package is included
        context.require_package("amsmath")
        context.require_package("amssymb")
        context.require_package("mathtools")

        # Parse OMML to LaTeX
        latex_content = self._parser.parse(element.omml_xml)

        # Clean up the LaTeX
        latex_content = self._clean_latex(latex_content)

        # Store converted LaTeX back in element for reference
        element.latex = latex_content

        # Wrap based on math type
        if element.math_type == MathType.INLINE:
            # Inline math
            return Ok(f"${latex_content}$")
        elif element.math_type == MathType.DISPLAY:
            # Display math (centered, no number)
            return Ok(f"\\[\n{latex_content}\n\\]")
        elif element.math_type == MathType.EQUATION:
            # Numbered equation
            return Ok(f"\\begin{{equation}}\n{latex_content}\n\\end{{equation}}")
        else:
            return Ok(f"${latex_content}$")

    def _clean_latex(self, latex: str) -> str:
        """
        Clean and optimize LaTeX output.

        Args:
            latex: Raw LaTeX string

        Returns:
            Cleaned LaTeX string
        """
        # Remove excessive whitespace
        latex = " ".join(latex.split())

        # Remove empty groups
        while "{}" in latex:
            latex = latex.replace("{}", "")

        # Note: We DO NOT remove braces around single characters because
        # commands like \frac{k}{m} need those braces.
        # The previous regex was incorrectly transforming \frac{k}{m} to \frackm
        import re

        # Normalize spacing around operators
        latex = re.sub(r"\s+([+\-=])\s+", r" \1 ", latex)

        # Remove trailing/leading spaces within braces
        latex = re.sub(r"\{\s+", "{", latex)
        latex = re.sub(r"\s+\}", "}", latex)

        return latex.strip()
