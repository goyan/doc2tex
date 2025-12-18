"""
Table converter.

Converts Table entities to LaTeX tables.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from docx2latex.domain.entities.elements import DocumentElement, Table, TableCell
from docx2latex.domain.protocols.converter import ConversionContext
from docx2latex.domain.value_objects.style import Alignment
from docx2latex.infrastructure.converters.base import BaseConverter
from docx2latex.shared.logging import get_logger
from docx2latex.shared.result import Ok, Result

if TYPE_CHECKING:
    from docx2latex.infrastructure.converters.registry import ConverterRegistry

logger = get_logger("table")


class TableConverter(BaseConverter[Table]):
    """
    Converter for tables.

    Supports merged cells, borders, and various column alignments.
    Uses booktabs for professional-looking tables.
    """

    def __init__(self, registry: ConverterRegistry | None = None) -> None:
        self._registry = registry

    @property
    def element_type(self) -> str:
        return "table"

    def can_convert(self, element: DocumentElement) -> bool:
        return isinstance(element, Table)

    def do_convert(
        self, element: Table, context: ConversionContext
    ) -> Result[str, str]:
        """
        Convert a table to LaTeX.

        Args:
            element: Table to convert
            context: Conversion context

        Returns:
            Result containing LaTeX table string
        """
        context.require_package("booktabs")
        context.require_package("array")
        context.require_package("multirow")

        table_context = context.enter_table()

        # Determine column specification
        col_spec = self._get_column_spec(element)

        lines = []

        # Begin table environment
        if element.caption:
            lines.append("\\begin{table}[htbp]")
            lines.append("\\centering")

        lines.append(f"\\begin{{tabular}}{{{col_spec}}}")
        lines.append("\\toprule")

        # Process rows
        header_done = False
        for row_idx, row in enumerate(element.rows):
            row_cells = []

            for cell in row.cells:
                cell_content = self._convert_cell(cell, table_context)

                # Handle column span
                if cell.col_span > 1:
                    align = self._get_cell_align(cell)
                    cell_content = f"\\multicolumn{{{cell.col_span}}}{{{align}}}{{{cell_content}}}"

                # Handle row span (multirow)
                if cell.row_span > 1:
                    context.require_package("multirow")
                    cell_content = f"\\multirow{{{cell.row_span}}}{{*}}{{{cell_content}}}"

                row_cells.append(cell_content)

            row_line = " & ".join(row_cells) + " \\\\"
            lines.append(row_line)

            # Add midrule after header
            if row.is_header and not header_done:
                lines.append("\\midrule")
                header_done = True
            elif row_idx == 0 and element.has_header_row:
                lines.append("\\midrule")
                header_done = True

        lines.append("\\bottomrule")
        lines.append("\\end{tabular}")

        # Caption and label
        if element.caption:
            lines.append(f"\\caption{{{element.caption}}}")
            if element.label:
                lines.append(f"\\label{{{element.label}}}")
            lines.append("\\end{table}")

        return Ok("\n".join(lines))

    def _get_column_spec(self, table: Table) -> str:
        """Generate LaTeX column specification."""
        num_cols = table.column_count
        if num_cols == 0:
            return "l"

        # Check if we have column widths
        if table.column_widths:
            # Use p{width} for columns with specified widths
            specs = []
            total_width = sum(w.to_pt() for w in table.column_widths)

            for width in table.column_widths:
                # Convert to fraction of line width
                fraction = width.to_pt() / total_width if total_width > 0 else 1 / num_cols
                specs.append(f"p{{{fraction:.2f}\\linewidth}}")

            return "".join(specs)

        # Default: left-aligned columns
        return "l" * num_cols

    def _get_cell_align(self, cell: TableCell) -> str:
        """Get alignment character for a cell."""
        align_map = {
            Alignment.LEFT: "l",
            Alignment.CENTER: "c",
            Alignment.RIGHT: "r",
            Alignment.JUSTIFY: "l",
        }
        return align_map.get(cell.alignment, "l")

    def _convert_cell(self, cell: TableCell, context: ConversionContext) -> str:
        """Convert cell content to LaTeX."""
        if not cell.paragraphs:
            return ""

        # Convert paragraphs
        parts = []
        for para in cell.paragraphs:
            if self._registry:
                result = self._registry.convert(para, context)
                if isinstance(result, Ok):
                    content = result.value.strip()
                    if content:
                        parts.append(content)
            else:
                parts.append(para.text)

        # Join multiple paragraphs with line breaks
        if len(parts) > 1:
            return " \\newline ".join(parts)
        elif parts:
            return parts[0]
        return ""
