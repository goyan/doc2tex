"""
Value Objects - Immutable objects defined by their attributes.

Value objects have no identity and are compared by their values.
They are immutable and can be freely shared.
"""

from docx2latex.domain.value_objects.color import Color
from docx2latex.domain.value_objects.dimension import Dimension, DimensionUnit
from docx2latex.domain.value_objects.font import FontSpec
from docx2latex.domain.value_objects.layout import PageLayout
from docx2latex.domain.value_objects.style import (
    Alignment,
    BorderSide,
    BorderStyle,
    ListType,
    MathType,
    ParagraphStyle,
    TextStyle,
)

__all__ = [
    "Alignment",
    "BorderSide",
    "BorderStyle",
    "Color",
    "Dimension",
    "DimensionUnit",
    "FontSpec",
    "ListType",
    "MathType",
    "PageLayout",
    "ParagraphStyle",
    "TextStyle",
]
