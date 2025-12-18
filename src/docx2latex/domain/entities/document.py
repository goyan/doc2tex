"""
Document entity - the aggregate root.

The Document is the main container for all document content.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, Any
from uuid import UUID, uuid4

from docx2latex.domain.entities.elements import (
    DocumentElement,
    Image,
    ListBlock,
    MathBlock,
    Paragraph,
    Table,
)
from docx2latex.domain.value_objects.layout import PageLayout

if TYPE_CHECKING:
    from collections.abc import Iterator


@dataclass
class DocumentMetadata:
    """
    Document metadata (core properties).

    Extracted from docProps/core.xml in the DOCX package.
    """

    title: str | None = None
    author: str | None = None
    subject: str | None = None
    keywords: list[str] = field(default_factory=list)
    description: str | None = None
    created: str | None = None  # ISO date string
    modified: str | None = None
    language: str | None = None
    revision: int | None = None

    def to_latex_metadata(self) -> dict[str, str]:
        """Convert to LaTeX document metadata commands."""
        result = {}
        if self.title:
            result["title"] = self.title
        if self.author:
            result["author"] = self.author
        if self.created:
            result["date"] = self.created
        return result


@dataclass
class DocumentSection:
    """
    A document section with its own layout.

    DOCX documents can have multiple sections with different
    page layouts, headers, and footers.
    """

    elements: list[Paragraph | Table | ListBlock | Image] = field(default_factory=list)
    layout: PageLayout = field(default_factory=PageLayout.default)
    header: list[Paragraph] = field(default_factory=list)
    footer: list[Paragraph] = field(default_factory=list)
    first_page_header: list[Paragraph] | None = None
    first_page_footer: list[Paragraph] | None = None
    id: UUID = field(default_factory=uuid4)

    def add_paragraph(self, paragraph: Paragraph) -> None:
        """Add a paragraph to the section."""
        self.elements.append(paragraph)

    def add_table(self, table: Table) -> None:
        """Add a table to the section."""
        self.elements.append(table)

    def add_list(self, list_block: ListBlock) -> None:
        """Add a list to the section."""
        self.elements.append(list_block)

    def add_image(self, image: Image) -> None:
        """Add an image to the section."""
        self.elements.append(image)


@dataclass
class Document:
    """
    The document aggregate root.

    Contains all document content, metadata, and embedded resources.
    This is the main object produced by the parser and consumed
    by the converter.
    """

    # Content organized by sections
    sections: list[DocumentSection] = field(default_factory=list)

    # Metadata
    metadata: DocumentMetadata = field(default_factory=DocumentMetadata)

    # Source file information
    source_path: Path | None = None

    # Embedded resources
    images: dict[str, Image] = field(default_factory=dict)  # rel_id -> Image
    styles: dict[str, Any] = field(default_factory=dict)  # style_id -> style info

    # Document-level settings
    default_font_size: float = 11.0  # points
    default_font_family: str = "Times New Roman"

    id: UUID = field(default_factory=uuid4)

    def __post_init__(self) -> None:
        """Ensure at least one section exists."""
        if not self.sections:
            self.sections.append(DocumentSection())

    @property
    def current_section(self) -> DocumentSection:
        """Get the current (last) section."""
        return self.sections[-1]

    def new_section(self, layout: PageLayout | None = None) -> DocumentSection:
        """Create a new section."""
        section = DocumentSection(layout=layout or PageLayout.default())
        self.sections.append(section)
        return section

    def add_paragraph(self, paragraph: Paragraph) -> None:
        """Add a paragraph to the current section."""
        self.current_section.add_paragraph(paragraph)

    def add_table(self, table: Table) -> None:
        """Add a table to the current section."""
        self.current_section.add_table(table)

    def add_list(self, list_block: ListBlock) -> None:
        """Add a list to the current section."""
        self.current_section.add_list(list_block)

    def register_image(self, rel_id: str, image: Image) -> None:
        """Register an embedded image."""
        self.images[rel_id] = image

    def get_image(self, rel_id: str) -> Image | None:
        """Get an image by relationship ID."""
        return self.images.get(rel_id)

    def iter_elements(self) -> Iterator[DocumentElement]:
        """Iterate over all elements in all sections."""
        for section in self.sections:
            yield from section.elements

    def iter_paragraphs(self) -> Iterator[Paragraph]:
        """Iterate over all paragraphs."""
        for element in self.iter_elements():
            if isinstance(element, Paragraph):
                yield element
            elif isinstance(element, Table):
                for row in element.rows:
                    for cell in row.cells:
                        yield from cell.paragraphs
            elif isinstance(element, ListBlock):
                for item in element.items:
                    yield from item.paragraphs

    def iter_math_blocks(self) -> Iterator[MathBlock]:
        """Iterate over all math blocks."""
        for paragraph in self.iter_paragraphs():
            for content in paragraph.content:
                if isinstance(content, MathBlock):
                    yield content

    def iter_tables(self) -> Iterator[Table]:
        """Iterate over all tables."""
        for element in self.iter_elements():
            if isinstance(element, Table):
                yield element

    def iter_images(self) -> Iterator[Image]:
        """Iterate over all images."""
        yield from self.images.values()

    @property
    def element_count(self) -> int:
        """Get total count of elements."""
        return sum(1 for _ in self.iter_elements())

    @property
    def paragraph_count(self) -> int:
        """Get total count of paragraphs."""
        return sum(1 for _ in self.iter_paragraphs())

    @property
    def math_count(self) -> int:
        """Get count of math blocks."""
        return sum(1 for _ in self.iter_math_blocks())

    @property
    def table_count(self) -> int:
        """Get count of tables."""
        return sum(1 for _ in self.iter_tables())

    @property
    def image_count(self) -> int:
        """Get count of images."""
        return len(self.images)

    @property
    def primary_layout(self) -> PageLayout:
        """Get the primary (first section) page layout."""
        if self.sections:
            return self.sections[0].layout
        return PageLayout.default()

    def summary(self) -> dict[str, Any]:
        """Get a summary of document contents."""
        return {
            "sections": len(self.sections),
            "paragraphs": self.paragraph_count,
            "tables": self.table_count,
            "images": self.image_count,
            "math_blocks": self.math_count,
            "title": self.metadata.title,
            "author": self.metadata.author,
        }

    def __str__(self) -> str:
        title = self.metadata.title or "Untitled"
        return f"Document('{title}', {self.paragraph_count} paragraphs)"

    def __repr__(self) -> str:
        return (
            f"Document(sections={len(self.sections)}, "
            f"paragraphs={self.paragraph_count}, "
            f"tables={self.table_count}, "
            f"images={self.image_count})"
        )
