"""
Result type for explicit error handling.

This module provides a Result monad for handling operations that can fail,
avoiding exceptions for control flow and making error handling explicit.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Callable, Generic, TypeVar, cast, overload

if TYPE_CHECKING:
    from collections.abc import Awaitable

T = TypeVar("T")
U = TypeVar("U")
E = TypeVar("E")
F = TypeVar("F")


@dataclass(frozen=True, slots=True)
class Ok(Generic[T]):
    """Represents a successful result containing a value."""

    value: T

    def is_ok(self) -> bool:
        return True

    def is_err(self) -> bool:
        return False

    def unwrap(self) -> T:
        """Return the contained value."""
        return self.value

    def unwrap_or(self, default: T) -> T:
        """Return the contained value (ignoring default)."""
        return self.value

    def unwrap_or_else(self, f: Callable[[object], T]) -> T:
        """Return the contained value (ignoring the function)."""
        return self.value

    def map(self, f: Callable[[T], U]) -> Ok[U]:
        """Apply a function to the contained value."""
        return Ok(f(self.value))

    def map_err(self, f: Callable[[object], F]) -> Ok[T]:
        """Return self unchanged (no error to map)."""
        return self

    def and_then(self, f: Callable[[T], Result[U, E]]) -> Result[U, E]:
        """Chain another operation that may fail."""
        return f(self.value)

    def or_else(self, f: Callable[[object], Result[T, F]]) -> Ok[T]:
        """Return self unchanged (no error to handle)."""
        return self


@dataclass(frozen=True, slots=True)
class Err(Generic[E]):
    """Represents a failed result containing an error."""

    error: E

    def is_ok(self) -> bool:
        return False

    def is_err(self) -> bool:
        return True

    def unwrap(self) -> T:
        """Raise an exception since there is no value."""
        raise ValueError(f"Called unwrap on Err: {self.error}")

    def unwrap_or(self, default: T) -> T:
        """Return the default value."""
        return default

    def unwrap_or_else(self, f: Callable[[E], T]) -> T:
        """Return the result of calling f with the error."""
        return f(self.error)

    def map(self, f: Callable[[object], U]) -> Err[E]:
        """Return self unchanged (no value to map)."""
        return self

    def map_err(self, f: Callable[[E], F]) -> Err[F]:
        """Apply a function to the contained error."""
        return Err(f(self.error))

    def and_then(self, f: Callable[[object], Result[U, E]]) -> Err[E]:
        """Return self unchanged (no value to chain)."""
        return self

    def or_else(self, f: Callable[[E], Result[T, F]]) -> Result[T, F]:
        """Handle the error with an alternative operation."""
        return f(self.error)


# Type alias for Result
Result = Ok[T] | Err[E]


def collect_results(results: list[Result[T, E]]) -> Result[list[T], E]:
    """
    Collect a list of Results into a Result of list.

    Returns Err with the first error encountered, or Ok with all values.
    """
    values: list[T] = []
    for result in results:
        match result:
            case Ok(value):
                values.append(value)
            case Err() as err:
                return err
    return Ok(values)


def try_catch(f: Callable[[], T], exception_type: type[Exception] = Exception) -> Result[T, str]:
    """
    Execute a function and catch exceptions, returning a Result.

    Use sparingly - prefer explicit Result returns where possible.
    """
    try:
        return Ok(f())
    except exception_type as e:
        return Err(str(e))
