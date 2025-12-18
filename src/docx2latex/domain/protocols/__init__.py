"""
Domain protocols - Interfaces for infrastructure.

These protocols define the contracts that infrastructure
implementations must fulfill.
"""

from docx2latex.domain.protocols.converter import ConversionContext, IElementConverter
from docx2latex.domain.protocols.parser import IDocumentParser
from docx2latex.domain.protocols.writer import ILatexWriter

__all__ = [
    "ConversionContext",
    "IDocumentParser",
    "IElementConverter",
    "ILatexWriter",
]
