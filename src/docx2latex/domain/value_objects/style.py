"""
Style value objects for text and paragraph formatting.

These immutable objects encapsulate styling information from DOCX
and provide LaTeX conversion methods.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Self

from docx2latex.domain.value_objects.color import Color
from docx2latex.domain.value_objects.dimension import Dimension
from docx2latex.domain.value_objects.font import FontSpec


class Alignment(Enum):
    """Text alignment options."""

    LEFT = auto()
    CENTER = auto()
    RIGHT = auto()
    JUSTIFY = auto()

    def to_latex(self) -> str:
        """Convert to LaTeX alignment command."""
        match self:
            case Alignment.LEFT:
                return r"\raggedright"
            case Alignment.CENTER:
                return r"\centering"
            case Alignment.RIGHT:
                return r"\raggedleft"
            case Alignment.JUSTIFY:
                return ""  # Default in LaTeX


class ListType(Enum):
    """List types."""

    BULLET = auto()
    NUMBERED = auto()
    LETTERED = auto()
    ROMAN = auto()

    def to_latex_env(self) -> str:
        """Get LaTeX environment name."""
        match self:
            case ListType.BULLET:
                return "itemize"
            case ListType.NUMBERED | ListType.LETTERED | ListType.ROMAN:
                return "enumerate"


class MathType(Enum):
    """Math block types."""

    INLINE = auto()  # Within text flow
    DISPLAY = auto()  # Centered on own line
    EQUATION = auto()  # Numbered equation


class UnderlineStyle(Enum):
    """Underline styles."""

    NONE = auto()
    SINGLE = auto()
    DOUBLE = auto()
    THICK = auto()
    DOTTED = auto()
    DASHED = auto()
    WAVE = auto()

    @classmethod
    def from_docx(cls, style: str | None) -> Self:
        """Parse DOCX underline style."""
        if style is None or style == "none":
            return cls.NONE

        style_map = {
            "single": cls.SINGLE,
            "double": cls.DOUBLE,
            "thick": cls.THICK,
            "dotted": cls.DOTTED,
            "dashed": cls.DASHED,
            "wave": cls.WAVE,
            "wavy": cls.WAVE,
        }
        return style_map.get(style.lower(), cls.SINGLE)


@dataclass(frozen=True, slots=True)
class TextStyle:
    """
    Immutable text style specification.

    Encapsulates character-level formatting.
    """

    bold: bool = False
    italic: bool = False
    underline: UnderlineStyle = UnderlineStyle.NONE
    strike: bool = False
    superscript: bool = False
    subscript: bool = False
    small_caps: bool = False
    all_caps: bool = False
    color: Color | None = None
    highlight: Color | None = None
    font: FontSpec | None = None

    def merge_with(self, other: TextStyle) -> TextStyle:
        """
        Merge this style with another, with other taking precedence.

        Used for style inheritance.
        """
        return TextStyle(
            bold=other.bold or self.bold,
            italic=other.italic or self.italic,
            underline=other.underline if other.underline != UnderlineStyle.NONE else self.underline,
            strike=other.strike or self.strike,
            superscript=other.superscript or self.superscript,
            subscript=other.subscript or self.subscript,
            small_caps=other.small_caps or self.small_caps,
            all_caps=other.all_caps or self.all_caps,
            color=other.color if other.color else self.color,
            highlight=other.highlight if other.highlight else self.highlight,
            font=other.font if other.font else self.font,
        )

    def has_formatting(self) -> bool:
        """Check if any formatting is applied."""
        return (
            self.bold
            or self.italic
            or self.underline != UnderlineStyle.NONE
            or self.strike
            or self.superscript
            or self.subscript
            or self.small_caps
            or self.all_caps
            or self.color is not None
            or self.highlight is not None
        )

    def wrap_latex(self, text: str) -> str:
        """
        Wrap text with appropriate LaTeX commands for this style.

        Args:
            text: The text to format

        Returns:
            LaTeX-formatted text
        """
        if not text:
            return text

        result = text

        # Apply text transformations first
        if self.all_caps:
            result = result.upper()

        # Build nested commands (innermost first)
        if self.subscript:
            result = rf"\textsubscript{{{result}}}"
        elif self.superscript:
            result = rf"\textsuperscript{{{result}}}"

        if self.small_caps:
            result = rf"\textsc{{{result}}}"

        if self.strike:
            result = rf"\sout{{{result}}}"

        if self.underline != UnderlineStyle.NONE:
            match self.underline:
                case UnderlineStyle.DOUBLE:
                    result = rf"\uuline{{{result}}}"
                case UnderlineStyle.WAVE:
                    result = rf"\uwave{{{result}}}"
                case _:
                    result = rf"\underline{{{result}}}"

        if self.italic:
            result = rf"\textit{{{result}}}"

        if self.bold:
            result = rf"\textbf{{{result}}}"

        # Color (outermost)
        if self.color and not self.color.is_black():
            hex_color = self.color.to_hex(include_hash=False).upper()
            result = rf"\textcolor[HTML]{{{hex_color}}}{{{result}}}"

        # Highlight
        if self.highlight:
            hex_color = self.highlight.to_hex(include_hash=False).upper()
            result = rf"\colorbox[HTML]{{{hex_color}}}{{{result}}}"

        return result

    @classmethod
    def empty(cls) -> Self:
        """Return empty (default) style."""
        return cls()


class BorderSide(Enum):
    """Border sides."""

    TOP = auto()
    BOTTOM = auto()
    LEFT = auto()
    RIGHT = auto()


@dataclass(frozen=True, slots=True)
class BorderStyle:
    """Border style specification."""

    width: Dimension = field(default_factory=Dimension.zero)
    color: Color | None = None
    style: str = "single"  # single, double, dashed, dotted, etc.

    def has_border(self) -> bool:
        """Check if border is visible."""
        return bool(self.width) and self.style != "none"

    def to_latex(self) -> str:
        """Convert to LaTeX border specification."""
        if not self.has_border():
            return ""

        # For booktabs, we use \toprule, \midrule, \bottomrule
        # For standard tables, we use \hline
        return r"\hline"


@dataclass(frozen=True, slots=True)
class ParagraphStyle:
    """
    Immutable paragraph style specification.

    Encapsulates paragraph-level formatting.
    """

    alignment: Alignment = Alignment.JUSTIFY
    line_spacing: float | None = None  # Multiple of normal (1.0, 1.5, 2.0)
    space_before: Dimension | None = None
    space_after: Dimension | None = None
    first_line_indent: Dimension | None = None
    left_indent: Dimension | None = None
    right_indent: Dimension | None = None
    keep_with_next: bool = False
    keep_together: bool = False
    page_break_before: bool = False
    style_name: str | None = None
    outline_level: int | None = None  # For headings (0-8)
    borders: dict[BorderSide, BorderStyle] = field(default_factory=dict)

    def is_heading(self) -> bool:
        """Check if this is a heading style."""
        if self.outline_level is not None:
            return True
        if self.style_name:
            name_lower = self.style_name.lower()
            return "heading" in name_lower or "titre" in name_lower
        return False

    def get_heading_level(self) -> int | None:
        """Get heading level (1-6 for LaTeX compatibility)."""
        if self.outline_level is not None:
            # DOCX uses 0-8, LaTeX uses 1-6 (section to subparagraph)
            return min(self.outline_level + 1, 6)

        if self.style_name:
            # Try to extract level from style name
            name_lower = self.style_name.lower()
            for i in range(1, 10):
                if f"heading {i}" in name_lower or f"titre {i}" in name_lower:
                    return min(i, 6)

        return None

    def to_latex_heading_cmd(self) -> str | None:
        """Get LaTeX heading command."""
        level = self.get_heading_level()
        if level is None:
            return None

        # Use starred versions to avoid automatic numbering
        commands = {
            1: r"\section*",
            2: r"\subsection*",
            3: r"\subsubsection*",
            4: r"\paragraph*",
            5: r"\subparagraph*",
            6: r"\subparagraph*",  # LaTeX only goes to 5 levels
        }
        return commands.get(level)

    def to_latex_spacing(self) -> str:
        """Generate LaTeX spacing commands."""
        parts = []

        if self.space_before:
            parts.append(rf"\vspace{{{self.space_before.to_latex_simple()}}}")

        if self.line_spacing and self.line_spacing != 1.0:
            if self.line_spacing == 1.5:
                parts.append(r"\onehalfspacing")
            elif self.line_spacing == 2.0:
                parts.append(r"\doublespacing")

        return "\n".join(parts)

    def merge_with(self, other: ParagraphStyle) -> ParagraphStyle:
        """Merge with another style, other taking precedence."""
        return ParagraphStyle(
            alignment=other.alignment if other.alignment != Alignment.JUSTIFY else self.alignment,
            line_spacing=other.line_spacing if other.line_spacing else self.line_spacing,
            space_before=other.space_before if other.space_before else self.space_before,
            space_after=other.space_after if other.space_after else self.space_after,
            first_line_indent=other.first_line_indent if other.first_line_indent else self.first_line_indent,
            left_indent=other.left_indent if other.left_indent else self.left_indent,
            right_indent=other.right_indent if other.right_indent else self.right_indent,
            keep_with_next=other.keep_with_next or self.keep_with_next,
            keep_together=other.keep_together or self.keep_together,
            page_break_before=other.page_break_before or self.page_break_before,
            style_name=other.style_name if other.style_name else self.style_name,
            outline_level=other.outline_level if other.outline_level is not None else self.outline_level,
            borders={**self.borders, **other.borders},
        )

    @classmethod
    def empty(cls) -> Self:
        """Return empty (default) style."""
        return cls()
