"""
Document parser protocol.

Defines the interface for parsing DOCX files into domain entities.
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Protocol, runtime_checkable

if TYPE_CHECKING:
    from docx2latex.domain.entities.document import Document
    from docx2latex.shared.result import Result


@runtime_checkable
class IDocumentParser(Protocol):
    """
    Protocol for document parsers.

    Implementations parse DOCX files and produce Document entities.
    """

    def parse(self, path: Path) -> Result[Document, str]:
        """
        Parse a DOCX file into a Document entity.

        Args:
            path: Path to the DOCX file

        Returns:
            Result containing the parsed Document or an error message
        """
        ...

    def parse_bytes(self, data: bytes) -> Result[Document, str]:
        """
        Parse DOCX data from bytes.

        Args:
            data: Raw DOCX file bytes

        Returns:
            Result containing the parsed Document or an error message
        """
        ...
