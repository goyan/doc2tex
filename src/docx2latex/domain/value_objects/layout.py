"""
Page layout value object.

Handles document page setup and geometry.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto
from typing import Self

from docx2latex.domain.value_objects.dimension import Dimension


class PageSize(Enum):
    """Standard page sizes."""

    A4 = auto()
    A5 = auto()
    LETTER = auto()
    LEGAL = auto()
    CUSTOM = auto()

    def to_latex(self) -> str:
        """Get LaTeX paper size option."""
        match self:
            case PageSize.A4:
                return "a4paper"
            case PageSize.A5:
                return "a5paper"
            case PageSize.LETTER:
                return "letterpaper"
            case PageSize.LEGAL:
                return "legalpaper"
            case PageSize.CUSTOM:
                return ""


class PageOrientation(Enum):
    """Page orientation."""

    PORTRAIT = auto()
    LANDSCAPE = auto()

    def to_latex(self) -> str:
        """Get LaTeX orientation option."""
        match self:
            case PageOrientation.PORTRAIT:
                return "portrait"
            case PageOrientation.LANDSCAPE:
                return "landscape"


# Standard page dimensions (width x height in mm)
STANDARD_PAGE_SIZES: dict[PageSize, tuple[float, float]] = {
    PageSize.A4: (210, 297),
    PageSize.A5: (148, 210),
    PageSize.LETTER: (215.9, 279.4),
    PageSize.LEGAL: (215.9, 355.6),
}


@dataclass(frozen=True, slots=True)
class PageLayout:
    """
    Immutable page layout specification.

    Encapsulates page size, margins, and orientation.
    """

    page_size: PageSize = PageSize.A4
    orientation: PageOrientation = PageOrientation.PORTRAIT
    width: Dimension | None = None
    height: Dimension | None = None
    margin_top: Dimension | None = None
    margin_bottom: Dimension | None = None
    margin_left: Dimension | None = None
    margin_right: Dimension | None = None
    header_distance: Dimension | None = None
    footer_distance: Dimension | None = None
    gutter: Dimension | None = None

    @classmethod
    def from_docx_section(
        cls,
        width_twips: int | None = None,
        height_twips: int | None = None,
        margin_top_twips: int | None = None,
        margin_bottom_twips: int | None = None,
        margin_left_twips: int | None = None,
        margin_right_twips: int | None = None,
        header_twips: int | None = None,
        footer_twips: int | None = None,
        gutter_twips: int | None = None,
    ) -> Self:
        """Create page layout from DOCX section properties."""
        width = Dimension.from_twips(width_twips) if width_twips else None
        height = Dimension.from_twips(height_twips) if height_twips else None

        # Detect page size
        page_size = PageSize.A4
        orientation = PageOrientation.PORTRAIT

        if width and height:
            width_mm = width.to_mm()
            height_mm = height.to_mm()

            # Check if landscape
            if width_mm > height_mm:
                orientation = PageOrientation.LANDSCAPE
                width_mm, height_mm = height_mm, width_mm

            # Try to match standard sizes (with 5mm tolerance)
            for size, (std_w, std_h) in STANDARD_PAGE_SIZES.items():
                if abs(width_mm - std_w) < 5 and abs(height_mm - std_h) < 5:
                    page_size = size
                    break
            else:
                page_size = PageSize.CUSTOM

        return cls(
            page_size=page_size,
            orientation=orientation,
            width=width,
            height=height,
            margin_top=Dimension.from_twips(margin_top_twips) if margin_top_twips else None,
            margin_bottom=Dimension.from_twips(margin_bottom_twips) if margin_bottom_twips else None,
            margin_left=Dimension.from_twips(margin_left_twips) if margin_left_twips else None,
            margin_right=Dimension.from_twips(margin_right_twips) if margin_right_twips else None,
            header_distance=Dimension.from_twips(header_twips) if header_twips else None,
            footer_distance=Dimension.from_twips(footer_twips) if footer_twips else None,
            gutter=Dimension.from_twips(gutter_twips) if gutter_twips else None,
        )

    def to_latex_geometry(self) -> str:
        """
        Generate LaTeX geometry package options.

        Returns:
            String for \\usepackage[options]{geometry}
        """
        options = []

        # Paper size
        if self.page_size != PageSize.CUSTOM:
            options.append(self.page_size.to_latex())
        elif self.width and self.height:
            options.append(f"paperwidth={self.width.to_latex_simple()}")
            options.append(f"paperheight={self.height.to_latex_simple()}")

        # Orientation
        if self.orientation == PageOrientation.LANDSCAPE:
            options.append("landscape")

        # Margins
        if self.margin_top:
            options.append(f"top={self.margin_top.to_latex_simple()}")
        if self.margin_bottom:
            options.append(f"bottom={self.margin_bottom.to_latex_simple()}")
        if self.margin_left:
            options.append(f"left={self.margin_left.to_latex_simple()}")
        if self.margin_right:
            options.append(f"right={self.margin_right.to_latex_simple()}")

        # Header/footer
        if self.header_distance:
            options.append(f"headheight={self.header_distance.to_latex_simple()}")
        if self.footer_distance:
            options.append(f"footskip={self.footer_distance.to_latex_simple()}")

        return ", ".join(options)

    @classmethod
    def default(cls) -> Self:
        """Return default A4 layout with standard margins."""
        return cls(
            page_size=PageSize.A4,
            orientation=PageOrientation.PORTRAIT,
            margin_top=Dimension.cm(2.5),
            margin_bottom=Dimension.cm(2.5),
            margin_left=Dimension.cm(2.5),
            margin_right=Dimension.cm(2.5),
        )

    def __str__(self) -> str:
        return f"{self.page_size.name} {self.orientation.name}"
