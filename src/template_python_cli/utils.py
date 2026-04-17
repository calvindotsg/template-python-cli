from __future__ import annotations


class InputError(Exception):
    """Raised for user-facing invalid-input conditions; CLI maps to exit code 2."""


def error_message(err: BaseException) -> str:
    """Return a printable message: str(err) if present, else the exception class name."""
    msg = str(err)
    return msg if msg else type(err).__name__
