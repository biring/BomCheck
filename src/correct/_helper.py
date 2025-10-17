"""
Shared helpers for BOM correction package.

Example Usage:
    # Preferred usage via package interface:
    # Not exposed publicly; this is an internal module.

    # Direct usage (internal scripts or unit tests only):
    import src.correct._common as common
    result = common.float_equal("1.3234", "1.32345")

Dependencies:
    - Python >= 3.9

Notes:
    - This module is intended for internal use by `src.correct` package.


License:
    - Internal Use Only
"""
__all__ = []  # Internal-only; not part of public API. Star import from this module gets nothing.

_DIGITS_OF_PRECISION = 6  # Number of decimal places to round to before comparison.

_EPSILON = 1e-6  # Acceptable tolerance for equality after rounding. This helps absorb tiny floating-point noise.


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
