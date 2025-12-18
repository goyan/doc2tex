"""
Dimension value object for handling measurements.

Handles conversions between different units (EMU, twips, points, cm, inches).
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto
from typing import Self

from docx2latex.shared.constants import (
    EMU_PER_CM,
    EMU_PER_INCH,
    EMU_PER_PT,
    TWIPS_PER_INCH,
    TWIPS_PER_PT,
)


class DimensionUnit(Enum):
    """Supported dimension units."""

    PT = auto()  # Points (1/72 inch)
    CM = auto()  # Centimeters
    MM = auto()  # Millimeters
    INCH = auto()  # Inches
    EMU = auto()  # English Metric Units (OOXML native)
    TWIPS = auto()  # Twentieth of a point
    PERCENT = auto()  # Percentage (relative)


@dataclass(frozen=True, slots=True)
class Dimension:
    """
    Immutable dimension value with unit.

    Provides conversion between different units commonly used
    in DOCX files and LaTeX output.
    """

    value: float
    unit: DimensionUnit

    @classmethod
    def from_emu(cls, emu: int) -> Self:
        """Create dimension from EMU (English Metric Units)."""
        return cls(value=float(emu), unit=DimensionUnit.EMU)

    @classmethod
    def from_twips(cls, twips: int) -> Self:
        """Create dimension from twips (twentieth of a point)."""
        return cls(value=float(twips), unit=DimensionUnit.TWIPS)

    @classmethod
    def from_half_points(cls, half_points: int) -> Self:
        """Create dimension from half-points (used for font sizes)."""
        return cls(value=half_points / 2.0, unit=DimensionUnit.PT)

    @classmethod
    def from_eighths_of_point(cls, eighths: int) -> Self:
        """Create dimension from eighths of a point (used for spacing)."""
        return cls(value=eighths / 8.0, unit=DimensionUnit.PT)

    @classmethod
    def pt(cls, value: float) -> Self:
        """Create dimension in points."""
        return cls(value=value, unit=DimensionUnit.PT)

    @classmethod
    def cm(cls, value: float) -> Self:
        """Create dimension in centimeters."""
        return cls(value=value, unit=DimensionUnit.CM)

    @classmethod
    def mm(cls, value: float) -> Self:
        """Create dimension in millimeters."""
        return cls(value=value, unit=DimensionUnit.MM)

    @classmethod
    def inch(cls, value: float) -> Self:
        """Create dimension in inches."""
        return cls(value=value, unit=DimensionUnit.INCH)

    @classmethod
    def percent(cls, value: float) -> Self:
        """Create dimension as percentage."""
        return cls(value=value, unit=DimensionUnit.PERCENT)

    @classmethod
    def zero(cls) -> Self:
        """Create zero dimension."""
        return cls(value=0.0, unit=DimensionUnit.PT)

    def to_pt(self) -> float:
        """Convert to points."""
        match self.unit:
            case DimensionUnit.PT:
                return self.value
            case DimensionUnit.CM:
                return self.value * 72 / 2.54
            case DimensionUnit.MM:
                return self.value * 72 / 25.4
            case DimensionUnit.INCH:
                return self.value * 72
            case DimensionUnit.EMU:
                return self.value / EMU_PER_PT
            case DimensionUnit.TWIPS:
                return self.value / TWIPS_PER_PT
            case DimensionUnit.PERCENT:
                raise ValueError("Cannot convert percentage to absolute unit")

    def to_cm(self) -> float:
        """Convert to centimeters."""
        match self.unit:
            case DimensionUnit.CM:
                return self.value
            case DimensionUnit.EMU:
                return self.value / EMU_PER_CM
            case DimensionUnit.PERCENT:
                raise ValueError("Cannot convert percentage to absolute unit")
            case _:
                return self.to_pt() * 2.54 / 72

    def to_mm(self) -> float:
        """Convert to millimeters."""
        return self.to_cm() * 10

    def to_inch(self) -> float:
        """Convert to inches."""
        match self.unit:
            case DimensionUnit.INCH:
                return self.value
            case DimensionUnit.EMU:
                return self.value / EMU_PER_INCH
            case DimensionUnit.TWIPS:
                return self.value / TWIPS_PER_INCH
            case DimensionUnit.PERCENT:
                raise ValueError("Cannot convert percentage to absolute unit")
            case _:
                return self.to_pt() / 72

    def to_latex(self, preferred_unit: DimensionUnit | None = None) -> str:
        """
        Convert to LaTeX dimension string.

        Args:
            preferred_unit: Preferred output unit (default: pt for small, cm for large)

        Returns:
            LaTeX-compatible dimension string (e.g., "12pt", "2.5cm")
        """
        if self.unit == DimensionUnit.PERCENT:
            return f"{self.value:.1f}\\%"

        # Auto-select unit based on magnitude
        if preferred_unit is None:
            pt_value = self.to_pt()
            if pt_value > 72:  # More than 1 inch
                preferred_unit = DimensionUnit.CM
            else:
                preferred_unit = DimensionUnit.PT

        match preferred_unit:
            case DimensionUnit.PT:
                return f"{self.to_pt():.2f}pt".rstrip("0").rstrip(".")  + "pt" if self.to_pt() != int(self.to_pt()) else f"{int(self.to_pt())}pt"
            case DimensionUnit.CM:
                cm_val = self.to_cm()
                if cm_val == int(cm_val):
                    return f"{int(cm_val)}cm"
                return f"{cm_val:.2f}cm".rstrip("0").rstrip(".")  + "cm"
            case DimensionUnit.MM:
                mm_val = self.to_mm()
                if mm_val == int(mm_val):
                    return f"{int(mm_val)}mm"
                return f"{mm_val:.1f}mm"
            case DimensionUnit.INCH:
                return f"{self.to_inch():.2f}in".rstrip("0").rstrip(".")  + "in"
            case _:
                return f"{self.to_pt():.2f}pt"

    def to_latex_simple(self) -> str:
        """Convert to simple LaTeX dimension string."""
        if self.unit == DimensionUnit.PERCENT:
            return f"{self.value / 100:.2f}\\textwidth"

        pt_val = self.to_pt()
        if abs(pt_val - round(pt_val)) < 0.01:
            return f"{int(round(pt_val))}pt"
        return f"{pt_val:.1f}pt"

    def __add__(self, other: Dimension) -> Dimension:
        """Add two dimensions (converts to points)."""
        return Dimension(self.to_pt() + other.to_pt(), DimensionUnit.PT)

    def __sub__(self, other: Dimension) -> Dimension:
        """Subtract two dimensions (converts to points)."""
        return Dimension(self.to_pt() - other.to_pt(), DimensionUnit.PT)

    def __mul__(self, scalar: float) -> Dimension:
        """Multiply dimension by scalar."""
        return Dimension(self.value * scalar, self.unit)

    def __truediv__(self, scalar: float) -> Dimension:
        """Divide dimension by scalar."""
        return Dimension(self.value / scalar, self.unit)

    def __bool__(self) -> bool:
        """Return True if dimension is non-zero."""
        return self.value != 0

    def __str__(self) -> str:
        return self.to_latex_simple()

    def __repr__(self) -> str:
        return f"Dimension({self.value}, {self.unit.name})"
