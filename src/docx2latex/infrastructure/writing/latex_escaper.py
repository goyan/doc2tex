"""
LaTeX text escaping utilities.
"""

from __future__ import annotations

from docx2latex.shared.constants import LATEX_SPECIAL_CHARS


class LatexEscaper:
    """
    Utility class for escaping text for LaTeX.

    Handles special characters, Unicode, and various escaping contexts.
    """

    @staticmethod
    def escape_text(text: str) -> str:
        """
        Escape special characters for LaTeX text mode.

        Args:
            text: Plain text to escape

        Returns:
            LaTeX-safe text
        """
        result = []
        for char in text:
            if char in LATEX_SPECIAL_CHARS:
                result.append(LATEX_SPECIAL_CHARS[char])
            else:
                result.append(char)
        return "".join(result)

    @staticmethod
    def escape_math(text: str) -> str:
        """
        Escape text for LaTeX math mode.

        In math mode, different characters need escaping.

        Args:
            text: Text to escape for math

        Returns:
            Math-safe text
        """
        # In math mode, most special chars are fine
        # Only text needs \text{} wrapping
        return text

    @staticmethod
    def escape_url(url: str) -> str:
        """
        Escape URL for hyperref.

        Args:
            url: URL to escape

        Returns:
            Hyperref-safe URL
        """
        # Escape characters that break hyperref
        url = url.replace("%", r"\%")
        url = url.replace("#", r"\#")
        url = url.replace("&", r"\&")
        url = url.replace("_", r"\_")
        return url

    @staticmethod
    def escape_filename(filename: str) -> str:
        """
        Escape filename for includegraphics.

        Args:
            filename: Filename to escape

        Returns:
            Safe filename for LaTeX
        """
        # Convert backslashes to forward slashes
        filename = filename.replace("\\", "/")
        # Escape spaces
        if " " in filename:
            filename = f'"{filename}"'
        return filename

    @staticmethod
    def escape_label(label: str) -> str:
        """
        Create a valid LaTeX label from arbitrary text.

        Args:
            label: Text to convert to label

        Returns:
            Valid LaTeX label
        """
        # Replace invalid characters
        valid = []
        for char in label:
            if char.isalnum() or char in "-_:":
                valid.append(char)
            elif char in " ":
                valid.append("-")
        return "".join(valid)
