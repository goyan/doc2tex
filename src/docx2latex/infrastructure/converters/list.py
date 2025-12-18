"""
List converter.

Converts ListBlock entities to LaTeX lists.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from docx2latex.domain.entities.elements import DocumentElement, ListBlock, ListItem
from docx2latex.domain.protocols.converter import ConversionContext
from docx2latex.domain.value_objects.style import ListType
from docx2latex.infrastructure.converters.base import BaseConverter
from docx2latex.shared.logging import get_logger
from docx2latex.shared.result import Ok, Result

if TYPE_CHECKING:
    from docx2latex.infrastructure.converters.registry import ConverterRegistry

logger = get_logger("list")


class ListConverter(BaseConverter[ListBlock]):
    """
    Converter for lists.

    Supports bulleted and numbered lists with nesting.
    """

    def __init__(self, registry: ConverterRegistry | None = None) -> None:
        self._registry = registry

    @property
    def element_type(self) -> str:
        return "list"

    def can_convert(self, element: DocumentElement) -> bool:
        return isinstance(element, ListBlock)

    def do_convert(
        self, element: ListBlock, context: ConversionContext
    ) -> Result[str, str]:
        """
        Convert a list to LaTeX.

        Args:
            element: ListBlock to convert
            context: Conversion context

        Returns:
            Result containing LaTeX list string
        """
        context.require_package("enumitem")

        list_context = context.enter_list()
        return Ok(self._convert_list_block(element, list_context))

    def _convert_list_block(
        self, list_block: ListBlock, context: ConversionContext
    ) -> str:
        """Convert a list block and its items."""
        # Skip empty lists (no items)
        if not list_block.items:
            return ""

        # Choose environment based on list type
        env = list_block.list_type.to_latex_env()

        lines = []

        # Begin environment with optional start number
        if list_block.list_type != ListType.BULLET and list_block.start_number != 1:
            lines.append(f"\\begin{{{env}}}[start={list_block.start_number}]")
        else:
            lines.append(f"\\begin{{{env}}}")

        # Convert items
        for item in list_block.items:
            item_content = self._convert_list_item(item, context)
            lines.append(f"\\item {item_content}")

        lines.append(f"\\end{{{env}}}")

        return "\n".join(lines)

    def _convert_list_item(
        self, item: ListItem, context: ConversionContext
    ) -> str:
        """Convert a list item."""
        parts = []

        # Convert paragraphs in the item
        for para in item.paragraphs:
            if self._registry:
                result = self._registry.convert(para, context)
                if isinstance(result, Ok):
                    content = result.value.strip()
                    if content:
                        parts.append(content)
            else:
                parts.append(para.text)

        content = " ".join(parts)

        # Handle nested sub-items
        if item.sub_items:
            # Create nested list for sub-items
            sub_list = ListBlock(
                items=item.sub_items,
                list_type=ListType.BULLET,  # Sub-lists default to bullet
                level=item.level + 1,
            )
            nested = self._convert_list_block(sub_list, context.enter_list())
            content += "\n" + nested

        return content
