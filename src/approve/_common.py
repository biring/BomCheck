"""
Shared validation helpers for BOM cell checks.

This module exposes a single routine to validate a value against a compiled regex and raise user-friendly errors for the `rules.approve` package.

Example Usage:
    # Preferred usage via package interface:
    # Not exposed publicly; this is an internal module.

    # Direct usage (internal scripts or tests only):
    from src.rules.approve import _common as common
    common.approve_or_raise("X123", re.compile(r"^[A-Z][0-9]+$"), "Board", "Valid '{a}' is an uppercase letter followed by digits.")

Dependencies:
    - Python >= 3.9
    - Standard Library: re

Notes:
    - This module is intended for internal use by `rules.approve` validators.
    - All error messages and regex patterns come from `_constants`.
    - Designed to raise clear, consistent ValueError messages for user feedback.
    - Type safety guards handle non-regex inputs and invalid regex compilation.

License:
    - Internal Use Only
"""
__all__ = []  # Internal-only; not part of public API. Star import from this module gets nothing.

import re

from src.approve import _constants as constants

_DIGITS_OF_PRECISION = 6  # Number of decimal places to round to before comparison.

_EPSILON = 1e-6  # Acceptable tolerance for equality after rounding. This helps absorb tiny floating-point noise.


def approve_or_raise(value: str, pattern: re.Pattern, label: str, rule: str) -> None:
    """
    Validate that a BOM cell value matches a given regex pattern.

    This function ensures that the provided string strictly adheres to the expected format defined by the compiled regex pattern. If the value fails validation, a `ValueError` is raised with a descriptive message including the field label and rule guidance.

    Args:
        value (str): Candidate string to be validated.
        pattern (re.Pattern): Precompiled regex pattern used for validation.
        label (str): Human-readable field label for error reporting.
        rule (str): Rule description to append in case of validation failure.

    Returns:
        None: Validation succeeds silently if the input matches the pattern.

    Raises:
        ValueError: If the string does not conform to the regex pattern.
        RuntimeError: If the regex engine encounters an internal error.
        TypeError: If the provided pattern is not a compiled regex object.
    """
    try:
        # Validate the input value against the regex
        if not pattern.fullmatch(value):
            # Raise descriptive error if validation fails
            raise ValueError(
                constants.GENERIC_VALUE_ERROR_MSG.format(a=label, b=value)
                + rule.format(a=label)
            )
    except re.error as error:
        # Handle cases where regex object is corrupt or invalid
        raise RuntimeError(constants.ERR_INVALID_REGEX.format(a=label, b=value, c=error))
    except AttributeError:
        # Handle non-regex objects passed instead of precompiled pattern
        raise TypeError(constants.ERR_COMPILED_REGEX.format(a=label, b=type(pattern).__name__))


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
