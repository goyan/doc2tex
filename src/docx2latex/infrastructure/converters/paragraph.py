"""
Paragraph converter.

Converts Paragraph entities to LaTeX.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from docx2latex.domain.entities.elements import (
    DocumentElement,
    Hyperlink,
    MathBlock,
    Paragraph,
    Run,
)
from docx2latex.domain.protocols.converter import ConversionContext
from docx2latex.infrastructure.converters.base import BaseConverter
from docx2latex.shared.constants import LATEX_SPECIAL_CHARS
from docx2latex.shared.logging import get_logger
from docx2latex.shared.result import Ok, Result

if TYPE_CHECKING:
    from docx2latex.infrastructure.converters.registry import ConverterRegistry

logger = get_logger("paragraph")


class ParagraphConverter(BaseConverter[Paragraph]):
    """
    Converter for paragraphs.

    Handles text runs, math blocks, hyperlinks, and formatting.
    """

    def __init__(self, registry: ConverterRegistry | None = None) -> None:
        self._registry = registry

    @property
    def element_type(self) -> str:
        return "paragraph"

    def can_convert(self, element: DocumentElement) -> bool:
        return isinstance(element, Paragraph)

    def do_convert(
        self, element: Paragraph, context: ConversionContext
    ) -> Result[str, str]:
        """
        Convert a paragraph to LaTeX.

        Args:
            element: Paragraph to convert
            context: Conversion context

        Returns:
            Result containing LaTeX string
        """
        # Check if this is a heading
        if element.is_heading():
            return self._convert_heading(element, context)

        # Convert paragraph content
        content_parts = []
        for item in element.content:
            if isinstance(item, Run):
                content_parts.append(self._convert_run(item, context))
            elif isinstance(item, MathBlock):
                if self._registry:
                    result = self._registry.convert(item, context)
                    if isinstance(result, Ok):
                        content_parts.append(result.value)
                else:
                    # Fallback: just use stored LaTeX
                    content_parts.append(f"${item.latex}$")
            elif isinstance(item, Hyperlink):
                content_parts.append(self._convert_hyperlink(item, context))

        content = "".join(content_parts)

        # Skip empty paragraphs
        if not content.strip():
            return Ok("")

        # Apply paragraph-level formatting
        result = self._apply_paragraph_formatting(content, element, context)

        return Ok(result)

    def _convert_heading(
        self, element: Paragraph, context: ConversionContext
    ) -> Result[str, str]:
        """Convert a heading paragraph."""
        level = element.get_heading_level()
        cmd = element.style.to_latex_heading_cmd()

        # Get heading text
        text_parts = []
        for item in element.content:
            if isinstance(item, Run):
                # Don't apply formatting to heading text (LaTeX handles it)
                text_parts.append(self._escape_latex(item.text))
            elif isinstance(item, MathBlock):
                text_parts.append(f"${item.latex}$")

        text = "".join(text_parts).strip()

        if cmd:
            return Ok(f"\n{cmd}{{{text}}}\n")

        # Fallback if no command determined
        return Ok(f"\n\\section{{{text}}}\n")

    def _convert_run(self, run: Run, context: ConversionContext) -> str:
        """Convert a text run with formatting."""
        if not run.text:
            return ""

        # Handle special characters (newlines, tabs)
        text = run.text

        # Check for page break marker
        if "\\newpage" in text:
            return "\n\\newpage\n"

        # Escape LaTeX special characters
        text = self._escape_latex(text)

        # Apply text formatting
        if run.style.has_formatting():
            text = run.style.wrap_latex(text)

            # Check if we need ulem package for underline/strikethrough
            if run.style.underline.value > 1 or run.style.strike:
                context.require_package("ulem", "normalem")

            # Check if we need xcolor for colored text
            if run.style.color or run.style.highlight:
                context.require_package("xcolor", "table")

        return text

    def _convert_hyperlink(
        self, hyperlink: Hyperlink, context: ConversionContext
    ) -> str:
        """Convert a hyperlink."""
        context.require_package("hyperref")

        # Get link text
        text_parts = []
        for run in hyperlink.runs:
            text_parts.append(self._escape_latex(run.text))
        text = "".join(text_parts)

        if hyperlink.is_internal():
            # Internal bookmark reference
            return rf"\hyperref[{hyperlink.bookmark}]{{{text}}}"
        else:
            # External URL
            url = self._escape_url(hyperlink.url)
            return rf"\href{{{url}}}{{{text}}}"

    def _escape_latex(self, text: str) -> str:
        """Escape LaTeX special characters in text."""
        result = []
        i = 0
        while i < len(text):
            char = text[i]

            # Check for existing LaTeX commands (don't escape backslashes in commands)
            if char == "\\" and i + 1 < len(text) and text[i + 1].isalpha():
                # This looks like a LaTeX command, preserve it
                j = i + 1
                while j < len(text) and text[j].isalpha():
                    j += 1
                result.append(text[i:j])
                i = j
                continue

            if char in LATEX_SPECIAL_CHARS:
                result.append(LATEX_SPECIAL_CHARS[char])
            else:
                result.append(char)
            i += 1

        return "".join(result)

    def _escape_url(self, url: str) -> str:
        """Escape special characters in URLs for hyperref."""
        # Only escape the characters that break hyperref
        url = url.replace("%", r"\%")
        url = url.replace("#", r"\#")
        url = url.replace("&", r"\&")
        return url

    def _apply_paragraph_formatting(
        self, content: str, element: Paragraph, context: ConversionContext
    ) -> str:
        """Apply paragraph-level formatting."""
        style = element.style
        parts = []

        # Page break before
        if style.page_break_before:
            parts.append("\\newpage\n")

        # Space before
        spacing_before = style.to_latex_spacing()
        if spacing_before:
            parts.append(spacing_before + "\n")

        # Alignment
        if style.alignment.value > 1:  # Not left/justify
            align_cmd = style.alignment.to_latex()
            if align_cmd:
                parts.append(f"{{{align_cmd} {content}}}")
            else:
                parts.append(content)
        else:
            parts.append(content)

        # Space after (add blank line)
        if style.space_after:
            parts.append("\n")

        return "".join(parts)
