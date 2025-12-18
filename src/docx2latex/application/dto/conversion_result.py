"""
Conversion result DTO.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class ConversionResult:
    """
    Result of a document conversion.

    Contains output paths, statistics, and any warnings/errors.
    """

    # Success/failure
    success: bool = True

    # Output files
    output_path: Path | None = None
    image_paths: list[Path] = field(default_factory=list)

    # Statistics
    paragraph_count: int = 0
    table_count: int = 0
    image_count: int = 0
    math_count: int = 0
    list_count: int = 0

    # Warnings and errors
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    # Timing (optional)
    parse_time_ms: float = 0
    convert_time_ms: float = 0
    write_time_ms: float = 0

    @property
    def total_time_ms(self) -> float:
        """Total conversion time."""
        return self.parse_time_ms + self.convert_time_ms + self.write_time_ms

    @property
    def has_warnings(self) -> bool:
        return len(self.warnings) > 0

    @property
    def has_errors(self) -> bool:
        return len(self.errors) > 0

    def summary(self) -> dict[str, Any]:
        """Get result summary as dictionary."""
        return {
            "success": self.success,
            "output": str(self.output_path) if self.output_path else None,
            "statistics": {
                "paragraphs": self.paragraph_count,
                "tables": self.table_count,
                "images": self.image_count,
                "math_blocks": self.math_count,
                "lists": self.list_count,
            },
            "warnings": len(self.warnings),
            "errors": len(self.errors),
            "time_ms": self.total_time_ms,
        }

    def __str__(self) -> str:
        if self.success:
            return f"Conversion successful: {self.output_path}"
        return f"Conversion failed: {self.errors[0] if self.errors else 'Unknown error'}"
