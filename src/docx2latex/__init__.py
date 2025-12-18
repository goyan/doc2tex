"""
DOCX to LaTeX Converter.

A high-quality converter for Microsoft Word documents to LaTeX format.
Supports math formulas, tables, images, lists, and layout preservation.
"""

__version__ = "1.0.0"
__author__ = "docx2latex"

from docx2latex.application.services.conversion_service import ConversionService
from docx2latex.presentation.cli import main

__all__ = ["ConversionService", "main", "__version__"]
