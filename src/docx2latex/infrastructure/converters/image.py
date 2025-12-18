"""
Image converter.

Converts Image entities to LaTeX figures.
"""

from __future__ import annotations

from pathlib import Path

from docx2latex.domain.entities.elements import DocumentElement, Image
from docx2latex.domain.protocols.converter import ConversionContext
from docx2latex.domain.value_objects.style import Alignment
from docx2latex.infrastructure.converters.base import BaseConverter
from docx2latex.shared.logging import get_logger
from docx2latex.shared.result import Ok, Result

logger = get_logger("image")


class ImageConverter(BaseConverter[Image]):
    """
    Converter for images.

    Exports images to files and generates LaTeX includegraphics.
    """

    @property
    def element_type(self) -> str:
        return "image"

    def can_convert(self, element: DocumentElement) -> bool:
        return isinstance(element, Image)

    def pre_convert(
        self, element: Image, context: ConversionContext
    ) -> Result[None, str]:
        """Export image to file before conversion."""
        if not element.data:
            return Ok(None)

        if context.output_dir is None:
            return Ok(None)

        # Create image directory
        image_dir = context.output_dir / context.image_dir
        image_dir.mkdir(parents=True, exist_ok=True)

        # Determine filename
        if element.filename:
            filename = element.filename
        else:
            filename = context.next_image_name(element.extension)

        # Write image file
        image_path = image_dir / filename
        try:
            image_path.write_bytes(element.data)
            # Store path for conversion
            element.filename = str(Path(context.image_dir) / filename)
        except Exception as e:
            logger.warning(f"Failed to write image: {e}")
            context.add_warning(f"Failed to export image: {e}")

        return Ok(None)

    def do_convert(
        self, element: Image, context: ConversionContext
    ) -> Result[str, str]:
        """
        Convert an image to LaTeX.

        Args:
            element: Image to convert
            context: Conversion context

        Returns:
            Result containing LaTeX figure/includegraphics string
        """
        context.require_package("graphicx")

        if not element.filename:
            return Ok(f"% Missing image: {element.rel_id}")

        # Build includegraphics options
        options = []

        if element.width:
            # Use width
            width_str = element.width.to_latex_simple()
            options.append(f"width={width_str}")
        elif element.height:
            # Use height
            height_str = element.height.to_latex_simple()
            options.append(f"height={height_str}")
        else:
            # Default: max width of line width
            options.append("width=\\linewidth")
            options.append("keepaspectratio")

        options_str = ",".join(options)

        # Clean filename for LaTeX (no special chars)
        filename = element.filename.replace("\\", "/")

        # Build the command
        includegraphics = f"\\includegraphics[{options_str}]{{{filename}}}"

        # If we have a caption, wrap in figure environment
        if element.caption:
            context.require_package("caption")

            align = ""
            if element.alignment == Alignment.CENTER:
                align = "\\centering\n"

            lines = [
                "\\begin{figure}[htbp]",
                align + includegraphics,
            ]

            lines.append(f"\\caption{{{element.caption}}}")

            if element.label:
                lines.append(f"\\label{{{element.label}}}")

            lines.append("\\end{figure}")

            return Ok("\n".join(lines))

        # No caption: just include the image
        if element.inline:
            return Ok(includegraphics)

        # Non-inline without caption: center it
        return Ok(f"\\begin{{center}}\n{includegraphics}\n\\end{{center}}")
