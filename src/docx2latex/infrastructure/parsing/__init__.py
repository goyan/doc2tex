"""
DOCX parsing infrastructure.

Handles extraction and parsing of DOCX files into domain entities.
"""

from docx2latex.infrastructure.parsing.docx_parser import DocxParser
from docx2latex.infrastructure.parsing.style_resolver import StyleResolver
from docx2latex.infrastructure.parsing.xml_namespaces import NS, nsmap, qn

__all__ = [
    "DocxParser",
    "NS",
    "StyleResolver",
    "nsmap",
    "qn",
]
