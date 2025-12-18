"""
Element converter protocol.

Defines the interface for converting document elements to LaTeX.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, Any, Generic, Protocol, TypeVar, runtime_checkable

if TYPE_CHECKING:
    from docx2latex.domain.entities.document import Document
    from docx2latex.domain.entities.elements import DocumentElement
    from docx2latex.shared.result import Result

T = TypeVar("T", bound="DocumentElement")


@dataclass
class ConversionContext:
    """
    Context passed to converters during conversion.

    Carries state and configuration needed by converters.
    """

    # Source document
    document: Document | None = None

    # Output configuration
    output_dir: Path | None = None
    image_dir: str = "images"

    # Conversion state
    in_math_mode: bool = False
    in_table: bool = False
    list_depth: int = 0
    current_section: int = 0

    # Accumulated preamble requirements
    required_packages: set[str] = field(default_factory=set)

    # Image counter for unique names
    image_counter: int = 0

    # Label tracking for cross-references
    labels: dict[str, str] = field(default_factory=dict)

    # Warnings accumulated during conversion
    warnings: list[str] = field(default_factory=list)

    # Custom options
    options: dict[str, Any] = field(default_factory=dict)

    def require_package(self, package: str, options: str | None = None) -> None:
        """Mark a package as required."""
        if options:
            self.required_packages.add(f"[{options}]{{{package}}}")
        else:
            self.required_packages.add(f"{{{package}}}")

    def add_warning(self, message: str) -> None:
        """Add a conversion warning."""
        self.warnings.append(message)

    def next_image_name(self, extension: str = "png") -> str:
        """Generate next unique image filename."""
        self.image_counter += 1
        return f"image_{self.image_counter:03d}.{extension}"

    def enter_math(self) -> ConversionContext:
        """Create context for math mode."""
        return ConversionContext(
            document=self.document,
            output_dir=self.output_dir,
            image_dir=self.image_dir,
            in_math_mode=True,
            in_table=self.in_table,
            list_depth=self.list_depth,
            current_section=self.current_section,
            required_packages=self.required_packages,
            image_counter=self.image_counter,
            labels=self.labels,
            warnings=self.warnings,
            options=self.options,
        )

    def enter_table(self) -> ConversionContext:
        """Create context for table."""
        return ConversionContext(
            document=self.document,
            output_dir=self.output_dir,
            image_dir=self.image_dir,
            in_math_mode=self.in_math_mode,
            in_table=True,
            list_depth=self.list_depth,
            current_section=self.current_section,
            required_packages=self.required_packages,
            image_counter=self.image_counter,
            labels=self.labels,
            warnings=self.warnings,
            options=self.options,
        )

    def enter_list(self) -> ConversionContext:
        """Create context for list (increases depth)."""
        return ConversionContext(
            document=self.document,
            output_dir=self.output_dir,
            image_dir=self.image_dir,
            in_math_mode=self.in_math_mode,
            in_table=self.in_table,
            list_depth=self.list_depth + 1,
            current_section=self.current_section,
            required_packages=self.required_packages,
            image_counter=self.image_counter,
            labels=self.labels,
            warnings=self.warnings,
            options=self.options,
        )


@runtime_checkable
class IElementConverter(Protocol, Generic[T]):
    """
    Protocol for element converters.

    Each converter handles a specific type of document element.
    """

    def can_convert(self, element: DocumentElement) -> bool:
        """
        Check if this converter can handle the given element.

        Args:
            element: The element to check

        Returns:
            True if this converter can handle the element
        """
        ...

    def convert(self, element: T, context: ConversionContext) -> Result[str, str]:
        """
        Convert an element to LaTeX.

        Args:
            element: The element to convert
            context: Conversion context with state and options

        Returns:
            Result containing LaTeX string or error message
        """
        ...
