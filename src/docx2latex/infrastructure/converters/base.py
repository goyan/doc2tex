"""
Base converter with template method pattern.

Provides common structure for all element converters.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Generic, TypeVar

from docx2latex.domain.entities.elements import DocumentElement
from docx2latex.domain.protocols.converter import ConversionContext, IElementConverter
from docx2latex.shared.logging import get_logger
from docx2latex.shared.result import Err, Ok, Result

if TYPE_CHECKING:
    pass

T = TypeVar("T", bound=DocumentElement)
logger = get_logger("converter")


class BaseConverter(ABC, Generic[T]):
    """
    Base class for element converters.

    Uses the Template Method pattern to provide a consistent
    conversion flow while allowing subclasses to customize steps.
    """

    @property
    @abstractmethod
    def element_type(self) -> str:
        """Return the type of element this converter handles."""
        ...

    def can_convert(self, element: DocumentElement) -> bool:
        """Check if this converter can handle the given element."""
        return element.element_type == self.element_type

    def convert(self, element: T, context: ConversionContext) -> Result[str, str]:
        """
        Convert an element to LaTeX using template method.

        This method orchestrates the conversion process:
        1. Pre-conversion hooks
        2. Main conversion
        3. Post-conversion processing

        Args:
            element: The element to convert
            context: Conversion context

        Returns:
            Result containing LaTeX string or error message
        """
        try:
            # Pre-conversion
            pre_result = self.pre_convert(element, context)
            if isinstance(pre_result, Err):
                return pre_result

            # Main conversion
            main_result = self.do_convert(element, context)
            if isinstance(main_result, Err):
                return main_result

            # Post-conversion
            post_result = self.post_convert(main_result.value, element, context)
            return post_result

        except Exception as e:
            logger.exception(f"Conversion error in {self.element_type}")
            return Err(f"Conversion failed: {e}")

    def pre_convert(self, element: T, context: ConversionContext) -> Result[None, str]:
        """
        Pre-conversion hook.

        Override to add setup logic before conversion.
        Default implementation does nothing.
        """
        return Ok(None)

    @abstractmethod
    def do_convert(self, element: T, context: ConversionContext) -> Result[str, str]:
        """
        Perform the main conversion.

        Subclasses must implement this method.
        """
        ...

    def post_convert(
        self, latex: str, element: T, context: ConversionContext
    ) -> Result[str, str]:
        """
        Post-conversion processing.

        Override to modify the LaTeX output after conversion.
        Default implementation returns the input unchanged.
        """
        return Ok(latex)
