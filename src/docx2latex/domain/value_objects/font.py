"""
Font specification value object.

Handles font family mapping between Windows/Mac fonts and LaTeX.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto
from typing import Self

from docx2latex.domain.value_objects.dimension import Dimension


class FontFamily(Enum):
    """Generic font families."""

    SERIF = auto()
    SANS_SERIF = auto()
    MONOSPACE = auto()
    MATH = auto()


# Common font mappings to LaTeX font families
FONT_FAMILY_MAP: dict[str, FontFamily] = {
    # Serif fonts
    "times new roman": FontFamily.SERIF,
    "times": FontFamily.SERIF,
    "georgia": FontFamily.SERIF,
    "palatino": FontFamily.SERIF,
    "palatino linotype": FontFamily.SERIF,
    "book antiqua": FontFamily.SERIF,
    "garamond": FontFamily.SERIF,
    "cambria": FontFamily.SERIF,
    "century": FontFamily.SERIF,
    "century schoolbook": FontFamily.SERIF,
    # Sans-serif fonts
    "arial": FontFamily.SANS_SERIF,
    "helvetica": FontFamily.SANS_SERIF,
    "calibri": FontFamily.SANS_SERIF,
    "verdana": FontFamily.SANS_SERIF,
    "tahoma": FontFamily.SANS_SERIF,
    "trebuchet ms": FontFamily.SANS_SERIF,
    "segoe ui": FontFamily.SANS_SERIF,
    "open sans": FontFamily.SANS_SERIF,
    "roboto": FontFamily.SANS_SERIF,
    # Monospace fonts
    "courier new": FontFamily.MONOSPACE,
    "courier": FontFamily.MONOSPACE,
    "consolas": FontFamily.MONOSPACE,
    "monaco": FontFamily.MONOSPACE,
    "lucida console": FontFamily.MONOSPACE,
    "menlo": FontFamily.MONOSPACE,
    "source code pro": FontFamily.MONOSPACE,
    # Math fonts
    "cambria math": FontFamily.MATH,
    "symbol": FontFamily.MATH,
}


@dataclass(frozen=True, slots=True)
class FontSpec:
    """
    Immutable font specification.

    Encapsulates font family, size, and other properties.
    """

    family: str | None = None
    size: Dimension | None = None
    family_type: FontFamily = FontFamily.SERIF

    @classmethod
    def from_docx(
        cls,
        family: str | None = None,
        size_half_points: int | None = None,
    ) -> Self:
        """
        Create font spec from DOCX properties.

        Args:
            family: Font family name from DOCX
            size_half_points: Font size in half-points (DOCX native)

        Returns:
            FontSpec instance
        """
        family_type = FontFamily.SERIF
        if family:
            family_lower = family.lower()
            family_type = FONT_FAMILY_MAP.get(family_lower, FontFamily.SERIF)

        size = None
        if size_half_points is not None:
            size = Dimension.from_half_points(size_half_points)

        return cls(
            family=family,
            size=size,
            family_type=family_type,
        )

    def to_latex_family(self) -> str | None:
        """
        Get LaTeX font family command.

        Returns:
            LaTeX command like \\textrm, \\textsf, or \\texttt
        """
        match self.family_type:
            case FontFamily.SERIF:
                return None  # Default, no command needed
            case FontFamily.SANS_SERIF:
                return r"\sffamily"
            case FontFamily.MONOSPACE:
                return r"\ttfamily"
            case FontFamily.MATH:
                return None  # Handled separately

    def to_latex_size(self) -> str | None:
        """
        Get LaTeX font size command.

        Maps point sizes to LaTeX size commands.
        """
        if self.size is None:
            return None

        pt = self.size.to_pt()

        # Map to standard LaTeX sizes (based on 10pt document class)
        if pt <= 5:
            return r"\tiny"
        if pt <= 7:
            return r"\scriptsize"
        if pt <= 8:
            return r"\footnotesize"
        if pt <= 9:
            return r"\small"
        if pt <= 10:
            return r"\normalsize"
        if pt <= 12:
            return r"\large"
        if pt <= 14:
            return r"\Large"
        if pt <= 18:
            return r"\LARGE"
        if pt <= 24:
            return r"\huge"
        return r"\Huge"

    def to_latex_fontsize_cmd(self) -> str | None:
        """
        Get LaTeX \\fontsize command for exact sizes.

        Returns:
            \\fontsize{size}{baselineskip} command
        """
        if self.size is None:
            return None

        pt = self.size.to_pt()
        # Baseline skip is typically 1.2x font size
        baseline = pt * 1.2
        return rf"\fontsize{{{pt:.1f}pt}}{{{baseline:.1f}pt}}\selectfont"

    def is_math_font(self) -> bool:
        """Check if this is a math font."""
        return self.family_type == FontFamily.MATH

    def __str__(self) -> str:
        parts = []
        if self.family:
            parts.append(self.family)
        if self.size:
            parts.append(str(self.size))
        return " ".join(parts) if parts else "default"

    def __repr__(self) -> str:
        return f"FontSpec(family={self.family!r}, size={self.size}, type={self.family_type.name})"
