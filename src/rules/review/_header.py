"""
Review helpers for capturing validation error messages from BOM header fields.

This module wraps header validators from `approve.header` so they return string messages instead of raising exceptions. This is intended for use in review/reporting workflows where errors must be collected and displayed
without interrupting execution.

Example Usage:
    # Preferred usage via public interface:
    from src.rules import interfaces as review
    msg = review.model_number("ABC123")  # "" if valid, error message if invalid

    # Direct module usage (internal only):
    from src.rules.review  import header as review
    msg = review.model_number("ABC123")

Dependencies:
    - Python >= 3.10
    - Standard Library: typing

Notes:
    - Each function mirrors a validator in `approve.header` but returns a string instead of raising ValueError.
    - Designed to support batch review and reporting pipelines.
    - Functions return `""` on success or the captured error message on failure.
    - This module is internal; no public API is exported.

License:
    - Internal Use Only
"""
__all__ = []  # Internal-only; not part of public API. Star import from this module gets nothing.

# noinspection PyProtectedMember
from src.approve import _header as approve  # Direct internal import — acceptable within package


def _review_and_capture(value: str, rule: callable) -> str:
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


def model_number(value: str) -> str:
    """
    Validate a model number string.

    Args:
        value (str): The candidate model number.

    Returns:
        str: Empty string if valid, otherwise a descriptive error message.
    """
    return _review_and_capture(value, approve.model_number)


def board_name(value: str) -> str:
    """
    Validate a board name string.

    Args:
        value (str): The candidate board name.

    Returns:
        str: Empty string if valid, otherwise a descriptive error message.
    """
    return _review_and_capture(value, approve.board_name)


def board_supplier(value: str) -> str:
    """
    Validate a board supplier string.

    Args:
        value (str): The candidate board supplier.

    Returns:
        str: Empty string if valid, otherwise a descriptive error message.
    """
    return _review_and_capture(value, approve.board_supplier)


def build_stage(value: str) -> str:
    """
    Validate a build stage string.

    Args:
        value (str): The candidate build stage.

    Returns:
        str: Empty string if valid, otherwise a descriptive error message.
    """
    return _review_and_capture(value, approve.build_stage)


def bom_date(value: str) -> str:
    """
    Validate a BOM date string.

    Args:
        value (str): The candidate BOM date.

    Returns:
        str: Empty string if valid, otherwise a descriptive error message.
    """
    return _review_and_capture(value, approve.bom_date)


def material_cost(value: str) -> str:
    """
    Validate a material cost string.

    Args:
        value (str): The candidate material cost.

    Returns:
        str: Empty string if valid, otherwise a descriptive error message.
    """
    return _review_and_capture(value, approve.material_cost)


def overhead_cost(value: str) -> str:
    """
    Validate an overhead cost string.

    Args:
        value (str): The candidate overhead cost.

    Returns:
        str: Empty string if valid, otherwise a descriptive error message.
    """
    return _review_and_capture(value, approve.overhead_cost)


def total_cost(value: str) -> str:
    """
    Validate a total cost string.

    Args:
        value (str): The candidate total cost.

    Returns:
        str: Empty string if valid, otherwise a descriptive error message.
    """
    return _review_and_capture(value, approve.total_cost)
