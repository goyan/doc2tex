"""
Custom exceptions for the docx2latex converter.

All exceptions inherit from Docx2LatexError for easy catching.
"""

from typing import Any


class Docx2LatexError(Exception):
    """Base exception for all docx2latex errors."""

    def __init__(self, message: str, details: dict[str, Any] | None = None) -> None:
        super().__init__(message)
        self.message = message
        self.details = details or {}

    def __str__(self) -> str:
        if self.details:
            detail_str = ", ".join(f"{k}={v}" for k, v in self.details.items())
            return f"{self.message} ({detail_str})"
        return self.message


class DocxParseError(Docx2LatexError):
    """Error parsing DOCX file structure."""

    def __init__(
        self,
        message: str,
        file_path: str | None = None,
        element: str | None = None,
    ) -> None:
        details = {}
        if file_path:
            details["file"] = file_path
        if element:
            details["element"] = element
        super().__init__(message, details)


class ConversionError(Docx2LatexError):
    """Error during element conversion."""

    def __init__(
        self,
        message: str,
        element_type: str | None = None,
        source: str | None = None,
    ) -> None:
        details = {}
        if element_type:
            details["type"] = element_type
        if source:
            details["source"] = source[:100] + "..." if len(source or "") > 100 else source
        super().__init__(message, details)


class MathConversionError(ConversionError):
    """Error converting math formulas."""

    def __init__(
        self,
        message: str,
        math_type: str | None = None,
        omml_snippet: str | None = None,
    ) -> None:
        super().__init__(message, element_type="math", source=omml_snippet)
        if math_type:
            self.details["math_type"] = math_type


class UnsupportedElementError(ConversionError):
    """Element type not supported for conversion."""

    def __init__(self, element_type: str, tag: str | None = None) -> None:
        message = f"Unsupported element type: {element_type}"
        super().__init__(message, element_type=element_type)
        if tag:
            self.details["tag"] = tag


class TemplateError(Docx2LatexError):
    """Error in LaTeX template processing."""

    def __init__(self, message: str, template_name: str | None = None) -> None:
        details = {}
        if template_name:
            details["template"] = template_name
        super().__init__(message, details)


class ImageProcessingError(Docx2LatexError):
    """Error processing images."""

    def __init__(
        self,
        message: str,
        image_path: str | None = None,
        format: str | None = None,  # noqa: A002
    ) -> None:
        details = {}
        if image_path:
            details["path"] = image_path
        if format:
            details["format"] = format
        super().__init__(message, details)


class StyleResolutionError(Docx2LatexError):
    """Error resolving document styles."""

    def __init__(self, message: str, style_id: str | None = None) -> None:
        details = {}
        if style_id:
            details["style_id"] = style_id
        super().__init__(message, details)
