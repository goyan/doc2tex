"""
Logging configuration for docx2latex.

Provides structured logging with rich output support.
"""

import logging
import sys
from typing import Any

from rich.console import Console
from rich.logging import RichHandler

# Global console instance for rich output
console = Console(stderr=True)


def setup_logging(
    level: int = logging.INFO,
    verbose: bool = False,
) -> logging.Logger:
    """
    Configure logging for the application.

    Args:
        level: The logging level (default: INFO)
        verbose: If True, sets DEBUG level and shows more details

    Returns:
        Configured logger instance
    """
    if verbose:
        level = logging.DEBUG

    # Configure root logger
    logging.basicConfig(
        level=level,
        format="%(message)s",
        datefmt="[%X]",
        handlers=[
            RichHandler(
                console=console,
                show_time=verbose,
                show_path=verbose,
                rich_tracebacks=True,
                tracebacks_show_locals=verbose,
            )
        ],
    )

    # Get our logger
    logger = logging.getLogger("docx2latex")
    logger.setLevel(level)

    return logger


def get_logger(name: str | None = None) -> logging.Logger:
    """Get a logger instance for the given name."""
    if name:
        return logging.getLogger(f"docx2latex.{name}")
    return logging.getLogger("docx2latex")


class ConversionProgress:
    """
    Track and report conversion progress.

    Provides a clean interface for reporting progress without
    coupling to any specific output mechanism.
    """

    def __init__(self, total_elements: int = 0, verbose: bool = False) -> None:
        self.total_elements = total_elements
        self.processed_elements = 0
        self.warnings: list[str] = []
        self.errors: list[str] = []
        self.verbose = verbose
        self._logger = get_logger("progress")

    def update(self, count: int = 1, message: str | None = None) -> None:
        """Update progress by count elements."""
        self.processed_elements += count
        if message and self.verbose:
            self._logger.debug(message)

    def add_warning(self, message: str, context: dict[str, Any] | None = None) -> None:
        """Record a warning during conversion."""
        full_message = message
        if context:
            full_message = f"{message} ({context})"
        self.warnings.append(full_message)
        self._logger.warning(full_message)

    def add_error(self, message: str, context: dict[str, Any] | None = None) -> None:
        """Record an error during conversion."""
        full_message = message
        if context:
            full_message = f"{message} ({context})"
        self.errors.append(full_message)
        self._logger.error(full_message)

    @property
    def progress_percent(self) -> float:
        """Return progress as percentage."""
        if self.total_elements == 0:
            return 0.0
        return (self.processed_elements / self.total_elements) * 100

    @property
    def has_warnings(self) -> bool:
        return len(self.warnings) > 0

    @property
    def has_errors(self) -> bool:
        return len(self.errors) > 0

    def summary(self) -> dict[str, Any]:
        """Return a summary of the conversion progress."""
        return {
            "total_elements": self.total_elements,
            "processed_elements": self.processed_elements,
            "warnings_count": len(self.warnings),
            "errors_count": len(self.errors),
            "warnings": self.warnings,
            "errors": self.errors,
        }
