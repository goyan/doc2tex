"""
LaTeX writer protocol.

Defines the interface for writing LaTeX output.
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Protocol, runtime_checkable

if TYPE_CHECKING:
    from docx2latex.domain.protocols.converter import ConversionContext
    from docx2latex.shared.result import Result


@runtime_checkable
class ILatexWriter(Protocol):
    """
    Protocol for LaTeX writers.

    Implementations handle the final output of LaTeX documents.
    """

    def write(
        self,
        content: str,
        context: ConversionContext,
        output_path: Path,
    ) -> Result[Path, str]:
        """
        Write LaTeX content to file.

        Args:
            content: The LaTeX body content
            context: Conversion context (for preamble packages)
            output_path: Path for output file

        Returns:
            Result containing the output path or error message
        """
        ...

    def generate_preamble(self, context: ConversionContext) -> str:
        """
        Generate LaTeX preamble based on required packages.

        Args:
            context: Conversion context with required packages

        Returns:
            LaTeX preamble string
        """
        ...

    def wrap_document(self, content: str, preamble: str) -> str:
        """
        Wrap content in a complete LaTeX document.

        Args:
            content: Document body content
            preamble: Preamble content

        Returns:
            Complete LaTeX document string
        """
        ...
