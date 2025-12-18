"""
Math conversion module - OMML to LaTeX.

This is the critical module for high-quality math conversion.
"""

from docx2latex.infrastructure.converters.math.converter import MathConverter
from docx2latex.infrastructure.converters.math.omml_parser import OmmlParser
from docx2latex.infrastructure.converters.math.symbols import SymbolMapper

__all__ = [
    "MathConverter",
    "OmmlParser",
    "SymbolMapper",
]
