"""
Conversion options DTO.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class ConversionOptions:
    """
    Options for document conversion.

    Configures various aspects of the conversion process.
    """

    # Output configuration
    output_path: Path | None = None
    output_dir: Path | None = None
    image_dir: str = "images"

    # Document class
    document_class: str = "article"
    font_size: int = 11

    # Feature toggles
    extract_images: bool = True
    convert_math: bool = True
    use_booktabs: bool = True
    use_hyperref: bool = True

    # Math options
    display_math_style: str = "display"  # display, equation, align

    # Image options
    max_image_width: float = 1.0  # fraction of linewidth
    convert_emf: bool = True  # Convert EMF/WMF to PNG

    # Table options
    table_style: str = "booktabs"  # booktabs, standard, custom

    # Debug/verbose
    verbose: bool = False
    debug: bool = False

    # Custom packages to include
    extra_packages: list[str] = field(default_factory=list)

    def get_output_path(self, input_path: Path) -> Path:
        """
        Determine output path based on options and input.

        Args:
            input_path: Input DOCX file path

        Returns:
            Output LaTeX file path
        """
        if self.output_path:
            return self.output_path

        if self.output_dir:
            return self.output_dir / f"{input_path.stem}.tex"

        return input_path.with_suffix(".tex")

    def get_output_dir(self, input_path: Path) -> Path:
        """
        Determine output directory.

        Args:
            input_path: Input DOCX file path

        Returns:
            Output directory path
        """
        if self.output_dir:
            return self.output_dir

        output_path = self.get_output_path(input_path)
        return output_path.parent
