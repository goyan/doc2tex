"""
Color value object for handling colors.

Supports RGB, hex, and named colors with LaTeX output.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Self


@dataclass(frozen=True, slots=True)
class Color:
    """
    Immutable color value.

    Stores color as RGB components (0-255).
    """

    red: int
    green: int
    blue: int

    def __post_init__(self) -> None:
        """Validate RGB values are in valid range."""
        for name, value in [("red", self.red), ("green", self.green), ("blue", self.blue)]:
            if not 0 <= value <= 255:
                raise ValueError(f"{name} must be between 0 and 255, got {value}")

    @classmethod
    def from_hex(cls, hex_color: str) -> Self:
        """
        Create color from hex string.

        Args:
            hex_color: Hex color string (with or without #, 3 or 6 digits)

        Returns:
            Color instance
        """
        hex_color = hex_color.lstrip("#")

        # Handle 3-digit hex
        if len(hex_color) == 3:
            hex_color = "".join(c * 2 for c in hex_color)

        if len(hex_color) != 6:
            raise ValueError(f"Invalid hex color: {hex_color}")

        return cls(
            red=int(hex_color[0:2], 16),
            green=int(hex_color[2:4], 16),
            blue=int(hex_color[4:6], 16),
        )

    @classmethod
    def from_rgb(cls, red: int, green: int, blue: int) -> Self:
        """Create color from RGB values (0-255)."""
        return cls(red=red, green=green, blue=blue)

    @classmethod
    def from_docx_color(cls, color_str: str | None) -> Self | None:
        """
        Parse color from DOCX format.

        DOCX uses various formats: 'auto', hex without #, theme colors, etc.
        """
        if color_str is None or color_str.lower() in ("auto", "none", ""):
            return None

        # Handle hex format (DOCX uses uppercase without #)
        if len(color_str) == 6:
            try:
                return cls.from_hex(color_str)
            except ValueError:
                return None

        return None

    @classmethod
    def black(cls) -> Self:
        """Return black color."""
        return cls(0, 0, 0)

    @classmethod
    def white(cls) -> Self:
        """Return white color."""
        return cls(255, 255, 255)

    @classmethod
    def red_color(cls) -> Self:
        """Return red color."""
        return cls(255, 0, 0)

    @classmethod
    def blue_color(cls) -> Self:
        """Return blue color."""
        return cls(0, 0, 255)

    def to_hex(self, include_hash: bool = True) -> str:
        """Convert to hex string."""
        hex_str = f"{self.red:02x}{self.green:02x}{self.blue:02x}"
        return f"#{hex_str}" if include_hash else hex_str

    def to_latex_xcolor(self) -> str:
        """
        Convert to xcolor package format.

        Returns a color definition usable with xcolor package.
        """
        # Return HTML format for xcolor
        return f"HTML:{self.to_hex(include_hash=False).upper()}"

    def to_latex_rgb(self) -> str:
        """Convert to LaTeX RGB format (0-1 scale)."""
        return f"{self.red/255:.3f},{self.green/255:.3f},{self.blue/255:.3f}"

    def is_black(self) -> bool:
        """Check if color is black."""
        return self.red == 0 and self.green == 0 and self.blue == 0

    def is_white(self) -> bool:
        """Check if color is white."""
        return self.red == 255 and self.green == 255 and self.blue == 255

    @property
    def luminance(self) -> float:
        """Calculate relative luminance (0-1)."""
        # Using sRGB luminance formula
        return 0.2126 * (self.red / 255) + 0.7152 * (self.green / 255) + 0.0722 * (self.blue / 255)

    def is_dark(self) -> bool:
        """Check if color is considered dark."""
        return self.luminance < 0.5

    def __str__(self) -> str:
        return self.to_hex()

    def __repr__(self) -> str:
        return f"Color({self.red}, {self.green}, {self.blue})"
