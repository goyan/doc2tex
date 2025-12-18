"""Shared kernel - constants, exceptions, and utilities."""

from docx2latex.shared.constants import (
    LATEX_SPECIAL_CHARS,
    OOXML_NS,
    SUPPORTED_IMAGE_FORMATS,
)
from docx2latex.shared.exceptions import (
    ConversionError,
    DocxParseError,
    Docx2LatexError,
    MathConversionError,
    UnsupportedElementError,
)
from docx2latex.shared.result import Err, Ok, Result

__all__ = [
    "LATEX_SPECIAL_CHARS",
    "OOXML_NS",
    "SUPPORTED_IMAGE_FORMATS",
    "ConversionError",
    "DocxParseError",
    "Docx2LatexError",
    "MathConversionError",
    "UnsupportedElementError",
    "Err",
    "Ok",
    "Result",
]
