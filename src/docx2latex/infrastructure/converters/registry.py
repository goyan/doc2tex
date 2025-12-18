"""
Converter registry - Factory pattern for element converters.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from docx2latex.domain.entities.elements import DocumentElement
from docx2latex.domain.protocols.converter import ConversionContext
from docx2latex.infrastructure.converters.base import BaseConverter
from docx2latex.shared.logging import get_logger
from docx2latex.shared.result import Err, Ok, Result

if TYPE_CHECKING:
    pass

logger = get_logger("registry")


class ConverterRegistry:
    """
    Registry of element converters.

    Manages available converters and routes elements to the
    appropriate converter based on element type.
    """

    def __init__(self) -> None:
        self._converters: list[BaseConverter] = []

    def register(self, converter: BaseConverter) -> None:
        """
        Register a converter.

        Args:
            converter: The converter to register
        """
        self._converters.append(converter)
        logger.debug(f"Registered converter for: {converter.element_type}")

    def get_converter(self, element: DocumentElement) -> BaseConverter | None:
        """
        Get the appropriate converter for an element.

        Args:
            element: The element to find a converter for

        Returns:
            The matching converter, or None if no converter found
        """
        for converter in self._converters:
            if converter.can_convert(element):
                return converter
        return None

    def convert(
        self, element: DocumentElement, context: ConversionContext
    ) -> Result[str, str]:
        """
        Convert an element using the appropriate converter.

        Args:
            element: The element to convert
            context: Conversion context

        Returns:
            Result containing LaTeX string or error message
        """
        converter = self.get_converter(element)
        if converter is None:
            logger.warning(f"No converter for element type: {element.element_type}")
            context.add_warning(f"Unsupported element: {element.element_type}")
            return Ok("")  # Return empty string for unsupported elements

        return converter.convert(element, context)

    def has_converter(self, element_type: str) -> bool:
        """Check if a converter exists for the given element type."""
        return any(c.element_type == element_type for c in self._converters)

    @property
    def supported_types(self) -> list[str]:
        """Get list of supported element types."""
        return [c.element_type for c in self._converters]


def create_default_registry() -> ConverterRegistry:
    """
    Create a registry with all default converters.

    Returns:
        Configured ConverterRegistry
    """
    from docx2latex.infrastructure.converters.image import ImageConverter
    from docx2latex.infrastructure.converters.list import ListConverter
    from docx2latex.infrastructure.converters.math import MathConverter
    from docx2latex.infrastructure.converters.paragraph import ParagraphConverter
    from docx2latex.infrastructure.converters.table import TableConverter

    registry = ConverterRegistry()

    # Register all converters
    registry.register(ParagraphConverter(registry))
    registry.register(MathConverter())
    registry.register(TableConverter(registry))
    registry.register(ListConverter(registry))
    registry.register(ImageConverter())

    return registry
