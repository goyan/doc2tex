"""
LaTeX document writer.

Generates complete LaTeX documents from converted content.
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from jinja2 import Environment, PackageLoader, select_autoescape

from docx2latex.domain.protocols.converter import ConversionContext
from docx2latex.shared.constants import DEFAULT_DOCUMENT_CLASS, DEFAULT_FONT_SIZE
from docx2latex.shared.logging import get_logger
from docx2latex.shared.result import Err, Ok, Result

if TYPE_CHECKING:
    from docx2latex.domain.entities.document import Document

logger = get_logger("writer")


# Default packages always included
DEFAULT_PACKAGES = [
    ("inputenc", "utf8"),
    ("fontenc", "T1"),
    ("geometry", None),
    ("amsmath", None),
    ("amssymb", None),
    ("graphicx", None),
    ("hyperref", None),
]


class LatexWriter:
    """
    Writer for LaTeX documents.

    Uses Jinja2 templates for document structure and handles
    preamble generation based on required packages.
    """

    def __init__(
        self,
        document_class: str = DEFAULT_DOCUMENT_CLASS,
        font_size: int = DEFAULT_FONT_SIZE,
    ) -> None:
        self._document_class = document_class
        self._font_size = font_size

        # Initialize Jinja2 environment
        try:
            self._env = Environment(
                loader=PackageLoader("docx2latex.infrastructure.writing", "templates"),
                autoescape=select_autoescape(["tex"]),
                trim_blocks=True,
                lstrip_blocks=True,
            )
        except Exception:
            # Fallback if templates not found (e.g., during development)
            self._env = None

    def write(
        self,
        content: str,
        context: ConversionContext,
        output_path: Path,
    ) -> Result[Path, str]:
        """
        Write LaTeX content to file.

        Args:
            content: The LaTeX body content
            context: Conversion context (for preamble packages)
            output_path: Path for output file

        Returns:
            Result containing the output path or error
        """
        try:
            # Generate preamble
            preamble = self.generate_preamble(context)

            # Get document metadata
            metadata = {}
            if context.document:
                metadata = context.document.metadata.to_latex_metadata()

            # Check if CJK package is required
            has_cjk = any("{CJKutf8}" in pkg for pkg in context.required_packages)

            # Wrap in complete document
            document = self.wrap_document(content, preamble, metadata, has_cjk)

            # Write to file
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(document, encoding="utf-8")

            return Ok(output_path)

        except Exception as e:
            logger.exception("Failed to write LaTeX file")
            return Err(f"Write error: {e}")

    def generate_preamble(self, context: ConversionContext) -> str:
        """
        Generate LaTeX preamble based on required packages.

        Args:
            context: Conversion context with required packages

        Returns:
            LaTeX preamble string
        """
        lines = []

        # Document class
        class_options = [f"{self._font_size}pt", "a4paper"]

        # Add geometry from document layout if available
        if context.document:
            layout = context.document.primary_layout
            geometry_opts = layout.to_latex_geometry()
            if geometry_opts:
                class_options.append(geometry_opts)

        lines.append(f"\\documentclass[{', '.join(class_options[:2])}]{{{self._document_class}}}")
        lines.append("")

        # Encoding packages
        lines.append("% Encoding")
        lines.append("\\usepackage[utf8]{inputenc}")
        lines.append("\\usepackage[T1]{fontenc}")
        lines.append("")

        # Geometry if we have layout info
        if context.document:
            layout = context.document.primary_layout
            geometry_opts = layout.to_latex_geometry()
            if geometry_opts:
                lines.append("% Page layout")
                lines.append(f"\\usepackage[{geometry_opts}]{{geometry}}")
                lines.append("")

        # Math packages (always useful)
        lines.append("% Math packages")
        lines.append("\\usepackage{amsmath}")
        lines.append("\\usepackage{amssymb}")
        lines.append("\\usepackage{mathtools}")
        lines.append("")

        # Required packages from context
        if context.required_packages:
            lines.append("% Additional packages")
            for pkg_spec in sorted(context.required_packages):
                if pkg_spec.startswith("["):
                    # Package with options: [options]{package}
                    lines.append(f"\\usepackage{pkg_spec}")
                else:
                    # Package without options: {package}
                    lines.append(f"\\usepackage{pkg_spec}")
            lines.append("")

        # Hyperref setup (should be loaded last in most cases)
        lines.append("% Hyperref setup")
        lines.append("\\usepackage{hyperref}")
        lines.append("\\hypersetup{")
        lines.append("    colorlinks=true,")
        lines.append("    linkcolor=blue,")
        lines.append("    filecolor=magenta,")
        lines.append("    urlcolor=cyan,")
        lines.append("}")
        lines.append("")

        return "\n".join(lines)

    def wrap_document(
        self,
        content: str,
        preamble: str,
        metadata: dict[str, str] | None = None,
        has_cjk: bool = False,
    ) -> str:
        """
        Wrap content in a complete LaTeX document.

        Args:
            content: Document body content
            preamble: Preamble content
            metadata: Document metadata (title, author, date)
            has_cjk: Whether the document contains CJK characters

        Returns:
            Complete LaTeX document string
        """
        lines = [preamble]

        # Note: We don't add \title, \author, \date, or \maketitle
        # as these are typically managed manually in the final document

        # Begin document
        lines.append("\\begin{document}")
        lines.append("")

        # If CJK content, wrap in CJK environment
        # Note: 'gbsn' (AR PL SungtiL GB) is from the arphic package and supports
        # Chinese characters. Install with: tlmgr install arphic cjk cjk-fonts
        if has_cjk:
            lines.append("\\begin{CJK}{UTF8}{gbsn}")
            lines.append("")
            lines.append(content)
            lines.append("")
            lines.append("\\end{CJK}")
        else:
            # Add content
            lines.append(content)
        lines.append("")

        # End document
        lines.append("\\end{document}")

        return "\n".join(lines)

    def write_standalone_math(
        self,
        latex_math: str,
        output_path: Path,
    ) -> Result[Path, str]:
        """
        Write a standalone math document (useful for testing).

        Args:
            latex_math: LaTeX math content
            output_path: Output file path

        Returns:
            Result with output path or error
        """
        document = f"""\\documentclass[preview]{{standalone}}
\\usepackage{{amsmath}}
\\usepackage{{amssymb}}
\\usepackage{{mathtools}}

\\begin{{document}}
${latex_math}$
\\end{{document}}
"""
        try:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(document, encoding="utf-8")
            return Ok(output_path)
        except Exception as e:
            return Err(f"Failed to write: {e}")
