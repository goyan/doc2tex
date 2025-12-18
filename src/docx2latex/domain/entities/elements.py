"""
Document element entities.

These are the core building blocks of a document structure.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Self
from uuid import UUID, uuid4

from docx2latex.domain.value_objects.dimension import Dimension
from docx2latex.domain.value_objects.style import (
    Alignment,
    ListType,
    MathType,
    ParagraphStyle,
    TextStyle,
)

if TYPE_CHECKING:
    from collections.abc import Iterator


class DocumentElement(ABC):
    """
    Abstract base class for all document elements.

    Provides common interface for traversal and identification.
    """

    @property
    @abstractmethod
    def element_type(self) -> str:
        """Return the element type identifier."""
        ...

    @abstractmethod
    def children(self) -> Iterator[DocumentElement]:
        """Iterate over child elements."""
        ...

    def accept(self, visitor: Any) -> Any:
        """Accept a visitor (Visitor pattern)."""
        method_name = f"visit_{self.element_type}"
        method = getattr(visitor, method_name, visitor.visit_default)
        return method(self)


@dataclass
class Run(DocumentElement):
    """
    A run of text with consistent formatting.

    A paragraph consists of one or more runs, each with
    potentially different text styling.
    """

    text: str
    style: TextStyle = field(default_factory=TextStyle.empty)
    id: UUID = field(default_factory=uuid4)

    @property
    def element_type(self) -> str:
        return "run"

    def children(self) -> Iterator[DocumentElement]:
        return iter([])

    def is_empty(self) -> bool:
        """Check if run has no visible content."""
        return not self.text or self.text.isspace()

    def __str__(self) -> str:
        return self.text


@dataclass
class Hyperlink(DocumentElement):
    """
    A hyperlink element containing runs.

    Can link to external URLs or internal bookmarks.
    """

    url: str
    runs: list[Run] = field(default_factory=list)
    tooltip: str | None = None
    bookmark: str | None = None  # Internal bookmark reference
    id: UUID = field(default_factory=uuid4)

    @property
    def element_type(self) -> str:
        return "hyperlink"

    def children(self) -> Iterator[DocumentElement]:
        return iter(self.runs)

    @property
    def text(self) -> str:
        """Get combined text of all runs."""
        return "".join(run.text for run in self.runs)

    def is_internal(self) -> bool:
        """Check if this links to internal bookmark."""
        return self.bookmark is not None


@dataclass
class MathBlock(DocumentElement):
    """
    A mathematical formula.

    Contains the original OMML XML and converted LaTeX.
    """

    omml_xml: str  # Original Office Math ML
    latex: str = ""  # Converted LaTeX (filled during conversion)
    math_type: MathType = MathType.INLINE
    id: UUID = field(default_factory=uuid4)

    @property
    def element_type(self) -> str:
        return "math"

    def children(self) -> Iterator[DocumentElement]:
        return iter([])

    def is_display(self) -> bool:
        """Check if this is a display (block) equation."""
        return self.math_type in (MathType.DISPLAY, MathType.EQUATION)


@dataclass
class Paragraph(DocumentElement):
    """
    A paragraph element containing runs, math, and hyperlinks.

    The fundamental text container in a document.
    """

    # Content can be runs, math blocks, or hyperlinks
    content: list[Run | MathBlock | Hyperlink] = field(default_factory=list)
    style: ParagraphStyle = field(default_factory=ParagraphStyle.empty)
    id: UUID = field(default_factory=uuid4)

    @property
    def element_type(self) -> str:
        return "paragraph"

    def children(self) -> Iterator[DocumentElement]:
        return iter(self.content)

    @property
    def text(self) -> str:
        """Get plain text content."""
        parts = []
        for item in self.content:
            if isinstance(item, Run):
                parts.append(item.text)
            elif isinstance(item, Hyperlink):
                parts.append(item.text)
            elif isinstance(item, MathBlock):
                parts.append(f"[MATH:{item.latex or 'unconverted'}]")
        return "".join(parts)

    def is_empty(self) -> bool:
        """Check if paragraph has no visible content."""
        return all(
            isinstance(item, Run) and item.is_empty()
            for item in self.content
        )

    def is_heading(self) -> bool:
        """Check if this paragraph is a heading."""
        return self.style.is_heading()

    def get_heading_level(self) -> int | None:
        """Get heading level if this is a heading."""
        return self.style.get_heading_level()

    def has_math(self) -> bool:
        """Check if paragraph contains math."""
        return any(isinstance(item, MathBlock) for item in self.content)

    def add_run(self, text: str, style: TextStyle | None = None) -> Run:
        """Add a text run to the paragraph."""
        run = Run(text=text, style=style or TextStyle.empty())
        self.content.append(run)
        return run

    def add_math(self, omml_xml: str, math_type: MathType = MathType.INLINE) -> MathBlock:
        """Add a math block to the paragraph."""
        math = MathBlock(omml_xml=omml_xml, math_type=math_type)
        self.content.append(math)
        return math


@dataclass
class TableCell(DocumentElement):
    """
    A table cell containing paragraphs.

    Can span multiple rows or columns.
    """

    paragraphs: list[Paragraph] = field(default_factory=list)
    row_span: int = 1
    col_span: int = 1
    width: Dimension | None = None
    alignment: Alignment = Alignment.LEFT
    vertical_alignment: str = "top"  # top, center, bottom
    is_header: bool = False
    id: UUID = field(default_factory=uuid4)

    @property
    def element_type(self) -> str:
        return "table_cell"

    def children(self) -> Iterator[DocumentElement]:
        return iter(self.paragraphs)

    @property
    def text(self) -> str:
        """Get plain text content."""
        return "\n".join(p.text for p in self.paragraphs)

    def is_empty(self) -> bool:
        """Check if cell has no content."""
        return all(p.is_empty() for p in self.paragraphs)

    def is_merged(self) -> bool:
        """Check if this cell spans multiple rows or columns."""
        return self.row_span > 1 or self.col_span > 1


@dataclass
class TableRow(DocumentElement):
    """
    A table row containing cells.
    """

    cells: list[TableCell] = field(default_factory=list)
    height: Dimension | None = None
    is_header: bool = False
    id: UUID = field(default_factory=uuid4)

    @property
    def element_type(self) -> str:
        return "table_row"

    def children(self) -> Iterator[DocumentElement]:
        return iter(self.cells)

    @property
    def cell_count(self) -> int:
        """Get logical cell count (accounting for spans)."""
        return sum(cell.col_span for cell in self.cells)


@dataclass
class Table(DocumentElement):
    """
    A table element containing rows.
    """

    rows: list[TableRow] = field(default_factory=list)
    column_widths: list[Dimension] = field(default_factory=list)
    alignment: Alignment = Alignment.CENTER
    caption: str | None = None
    label: str | None = None  # For cross-references
    has_header_row: bool = False
    id: UUID = field(default_factory=uuid4)

    @property
    def element_type(self) -> str:
        return "table"

    def children(self) -> Iterator[DocumentElement]:
        return iter(self.rows)

    @property
    def row_count(self) -> int:
        return len(self.rows)

    @property
    def column_count(self) -> int:
        """Get number of columns."""
        if self.column_widths:
            return len(self.column_widths)
        if self.rows:
            return max(row.cell_count for row in self.rows)
        return 0

    def get_header_rows(self) -> list[TableRow]:
        """Get rows marked as header."""
        return [row for row in self.rows if row.is_header]


@dataclass
class ListItem(DocumentElement):
    """
    A list item containing paragraphs.

    Can be nested (contain sub-lists).
    """

    paragraphs: list[Paragraph] = field(default_factory=list)
    sub_items: list[ListItem] = field(default_factory=list)
    level: int = 0
    number: int | str | None = None  # For numbered lists
    id: UUID = field(default_factory=uuid4)

    @property
    def element_type(self) -> str:
        return "list_item"

    def children(self) -> Iterator[DocumentElement]:
        yield from self.paragraphs
        yield from self.sub_items

    @property
    def text(self) -> str:
        """Get plain text content."""
        return "\n".join(p.text for p in self.paragraphs)

    def has_sub_items(self) -> bool:
        return len(self.sub_items) > 0


@dataclass
class ListBlock(DocumentElement):
    """
    A list (bulleted or numbered) containing items.
    """

    items: list[ListItem] = field(default_factory=list)
    list_type: ListType = ListType.BULLET
    start_number: int = 1
    level: int = 0
    id: UUID = field(default_factory=uuid4)

    @property
    def element_type(self) -> str:
        return "list"

    def children(self) -> Iterator[DocumentElement]:
        return iter(self.items)

    def is_numbered(self) -> bool:
        return self.list_type != ListType.BULLET


@dataclass
class Image(DocumentElement):
    """
    An image element.

    Contains reference to image data and sizing information.
    """

    # Image identification
    rel_id: str  # Relationship ID in DOCX
    filename: str = ""
    content_type: str = ""

    # Sizing
    width: Dimension | None = None
    height: Dimension | None = None

    # Layout
    inline: bool = True  # vs floating
    alignment: Alignment = Alignment.CENTER

    # Caption and labeling
    caption: str | None = None
    alt_text: str | None = None
    label: str | None = None  # For cross-references

    # Raw data (filled during parsing)
    data: bytes = field(default=b"", repr=False)

    id: UUID = field(default_factory=uuid4)

    @property
    def element_type(self) -> str:
        return "image"

    def children(self) -> Iterator[DocumentElement]:
        return iter([])

    @property
    def extension(self) -> str:
        """Get file extension."""
        if "." in self.filename:
            return self.filename.rsplit(".", 1)[-1].lower()
        # Guess from content type
        type_map = {
            "image/png": "png",
            "image/jpeg": "jpg",
            "image/gif": "gif",
            "image/svg+xml": "svg",
            "image/x-emf": "emf",
            "image/x-wmf": "wmf",
        }
        return type_map.get(self.content_type, "png")

    def needs_conversion(self) -> bool:
        """Check if image format needs conversion for LaTeX."""
        return self.extension in ("emf", "wmf", "gif")

    @property
    def aspect_ratio(self) -> float | None:
        """Get aspect ratio (width/height)."""
        if self.width and self.height:
            w = self.width.to_pt()
            h = self.height.to_pt()
            if h > 0:
                return w / h
        return None
