"""
Common helper utilities for review module.

This module centralizes shared functions used by `_header`, `_row`, and `_logic`, primarily to wrap validator calls and capture errors as strings.

Example Usage:
    # Preferred usage via an internal caller:
    # Not exposed publicly; this is an internal module.

    # Direct usage (internal tests only):
    import src.review._common as common
    msg = common.review_and_capture("ABC123", rule)

Dependencies:
    - Python >= 3.10
    - Standard Library: typing

Notes:
    - This module is intended strictly for internal use by other review helpers.
    - Functions here should remain minimal and generic, avoiding validator-specific logic.
    - Enables consistent error-message capturing across header, row, and logic modules.

License:
    - Internal Use Only
"""
__all__ = []  # Internal-only; not part of public API. Star import from this module gets nothing.

from typing import Callable


def review_and_capture(value: str, rule: Callable) -> str:
    """
    Apply a rule to the input string and capture any error message.

    Runs the provided validation function. If validation succeeds, returns an empty string. If the validator raises a ValueError, its message is returned.

    Args:
        value (str): The candidate input string to validate.
        rule (callable): A function that validates the input and raises ValueError on failure.

    Returns:
        str: Empty string if rule passes, otherwise the error message.
    """
    # Default: no error message
    msg = ""
    try:
        # Run rule (raises ValueError on failure)
        rule(value)
    except ValueError as err:
        # Capture error message instead of raising
        msg = str(err)

    return msg
