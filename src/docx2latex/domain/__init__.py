"""
Domain layer - Core business entities and value objects.

This layer has no external dependencies and defines the core
data structures and protocols used throughout the application.
"""

from docx2latex.domain.entities import (
    Document,
    DocumentElement,
    Hyperlink,
    Image,
    ListBlock,
    ListItem,
    MathBlock,
    Paragraph,
    Run,
    Table,
    TableCell,
    TableRow,
)
from docx2latex.domain.value_objects import (
    Alignment,
    BorderStyle,
    Color,
    Dimension,
    DimensionUnit,
    FontSpec,
    ListType,
    MathType,
    PageLayout,
    ParagraphStyle,
    TextStyle,
)

__all__ = [
    # Entities
    "Document",
    "DocumentElement",
    "Hyperlink",
    "Image",
    "ListBlock",
    "ListItem",
    "MathBlock",
    "Paragraph",
    "Run",
    "Table",
    "TableCell",
    "TableRow",
    # Value Objects
    "Alignment",
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
