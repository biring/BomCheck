"""
Shared helpers for BOM correction flows.

This module provides:
 - floats_equal: compare two floats using fixed precision and epsilon tolerance
 - generate_log_entry: build a one-line change log when a value changes
 - prompt_until_valid: standard CLI loop that shows info on first failure, warns on each invalid entry, and reprompts

Example Usage:
    # Preferred usage via package interface:
    # Not exposed publicly; this is an internal module.

    # Direct usage (internal scripts or unit tests only):
    import src.correct._common as common
    result = common.float_equals("1.3234", "1.32345")

Dependencies:
    - Python >= 3.10
    - Standard Library: typing
    - Project: src.cli.interfaces (for user prompts and messaging)

Notes:
    - Internal-only utilities; keep prompting, messaging, and tolerance settings centralized for consistent UX across correctors.
    - Pure logic aside from CLI calls in prompt_until_valid; floats_equal parameters (_DIGITS_OF_PRECISION, _EPSILON) define comparison strictness.

License:
    - Internal Use Only
"""

__all__ = []  # Internal-only; not part of public API. Star import from this module gets nothing.

from typing import Callable
from src.cli import interfaces as cli

_DIGITS_OF_PRECISION = 6  # Number of decimal places to round to before comparison.
_EPSILON = 1e-6  # Acceptable tolerance for equality after rounding. This helps absorb tiny floating-point noise.

TEMPLATE_CORRECTION_MSG = "'{field}' changed from '{before}' to '{after}'. {reason}"
TEMPLATE_CORRECTION_PROMPT = "Enter correct value for '{field}': "


def floats_equal(value_a: float, value_b: float) -> bool:
    """
    Compare two floating-point numbers for approximate equality.

    This function first rounds both numbers to a fixed number of decimal places (set by `_DIGITS_OF_PRECISION`). It then checks whether the absolute difference between the rounded values is smaller than a tolerance (`_EPSILON`).

    Args:
        value_a (float): The first value to compare.
        value_b (float): The second value to compare.

    Returns:
        bool: True if the two numbers are considered equal within the specified precision and tolerance, False otherwise.

    Raises:
        None

    Notes:
        - Use this helper instead of `==` when dealing with floats, since binary floating-point arithmetic can introduce very small errors.
        - Adjust `_DIGITS_OF_PRECISION` if you need more or fewer decimal places (e.g., 4 for four-decimal precision).
        - Adjust `_EPSILON` if you want stricter or looser tolerance.
    """
    # Round both numbers to the configured precision
    rounded_a = round(value_a, _DIGITS_OF_PRECISION)
    rounded_b = round(value_b, _DIGITS_OF_PRECISION)

    # Compute the absolute difference
    difference = abs(rounded_a - rounded_b)

    # Return True if within tolerance, False otherwise
    return difference < _EPSILON


def generate_log_entry(field: str, before: str, after: str, reason: str) -> str:
    """
    Build a one-line change log entry when a value changes; return empty string otherwise.

    Args:
        field (str): Field label being updated.
        before (str): Original value.
        after (str): New value.
        reason (str): Short rationale for the change.

    Returns:
        str: Formatted log entry if 'after' != 'before'; otherwise "".

    Raises:
        None
    """
    msg = ""

    # create log entry only when value changes
    if after != before:
        msg = TEMPLATE_CORRECTION_MSG.format(
            field=field,
            before=before,
            after=after,
            reason=reason
        )

    return msg


def prompt_until_valid(data: str, fn: Callable, value: str, field: str) -> str:
    """
    Prompt the user until the validator returns no error message; return the accepted value.

    Shows an optional context/info message once when the initial value is invalid, then loops: displays the validator's message as a warning, prompts the user, and re-validates. The validator 'fn' must accept a single string and return "" on success or an error message on failure.

    Args:
        data (str): Contextual info to display once when the first validation fails (e.g., sample or guidance).
        fn (Callable): Validator: (candidate: str) -> str; return "" if valid, else a human-readable error.
        value (str): Initial candidate value.
        field (str): Field label to use in the prompt.

    Returns:
        str: The first candidate that passes validation.

    Raises:
        None
    """
    value_out = value

    # Validate the initial value; if invalid, show context once to help the user correct it
    msg = fn(value_out)

    if msg:
        cli.show_info(data)

    # Loop until the validator returns "", prompting with a stable, field-specific message
    while msg:
        cli.show_warning(msg)
        # Keep the prompt template centralized to preserve consistent UX across fields
        prompt = TEMPLATE_CORRECTION_PROMPT.format(field=field)
        value_out = cli.prompt_for_string_value(prompt)
        msg = fn(value_out)

    return value_out
