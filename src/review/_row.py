"""
Review helpers for collecting validation error messages from BOM row fields.

This module wraps row validators from `src.approve` so they return string messages instead of raising exceptions. This is intended for use in review/reporting workflows where errors must be collected and displayed without interrupting execution.

Example Usage:
    # Preferred usage via public package interface:
    from src.review import interfaces as review
    msg = review.item("14")  # "" if valid, else error message

    # Direct module usage (internal scripts or tests only):
    from src.review import _row as review
    msg = review.item("A23")

Dependencies:
    - Python >= 3.10
    - Standard Library: typing
    - External Packages: None

Notes:
    - Each function mirrors a validator in `approve.row` but returns a string instead of raising ValueError.
    - Designed to support batch review and reporting pipelines.
    - Functions return `""` on success or the captured error message on failure.
    - This module is internal; no public API is exported.

License:
    - Internal Use Only
"""
__all__ = []  # Internal-only; not part of public API. Star import from this module gets nothing.

from src.approve import interfaces as approve

from src.review import _common as common


def item(value: str) -> str:
    """
    Validate a item string.

    Args:
        value (str): The item string to review.

    Returns:
        str: Empty string if valid, otherwise a descriptive error message.
    """
    return common.review_and_capture(value, approve.item)


def component_type(value: str) -> str:
    """
    Validate a component type string.

    Args:
        value (str): The component type string to review.

    Returns:
        str: Empty string if valid, otherwise a descriptive error message.
    """
    return common.review_and_capture(value, approve.component_type)


def device_package(value: str) -> str:
    """
    Validate a device package string.

    Args:
        value (str): The device package string to review.

    Returns:
        str: Empty string if valid, otherwise a descriptive error message.
    """
    return common.review_and_capture(value, approve.device_package)


def description(value: str) -> str:
    """
    Validate a description string.

    Args:
        value (str): The description string to review.

    Returns:
        str: Empty string if valid, otherwise a descriptive error message.
    """
    return common.review_and_capture(value, approve.description)


def units(value: str) -> str:
    """
    Validate a units string.

    Args:
        value (str): The units string to review.

    Returns:
        str: Empty string if valid, otherwise a descriptive error message.
    """
    return common.review_and_capture(value, approve.units)


def classification(value: str) -> str:
    """
    Validate a classification string.

    Args:
        value (str): The classification string to review.

    Returns:
        str: Empty string if valid, otherwise a descriptive error message.
    """
    return common.review_and_capture(value, approve.classification)


def mfg_name(value: str) -> str:
    """
    Validate a manufacturer name string.

    Args:
        value (str): The manufacturer name to review.

    Returns:
        str: Empty string if valid, otherwise a descriptive error message.
    """
    return common.review_and_capture(value, approve.mfg_name)


def mfg_part_no(value: str) -> str:
    """
    Validate a manufacturer part number string.

    Args:
        value (str): The manufacturer part number to review.

    Returns:
        str: Empty string if valid, otherwise a descriptive error message.
    """
    return common.review_and_capture(value, approve.mfg_part_no)


def ul_vde_number(value: str) -> str:
    """
    Validate a UL/VDE number string.

    Args:
        value (str): The UL/VDE number to review.

    Returns:
        str: Empty string if valid, otherwise a descriptive error message.
    """
    return common.review_and_capture(value, approve.ul_vde_number)


def validated_at(value: str) -> str:
    """
    Validate a validated-at string.

    Args:
        value (str): The validated-at string to review.

    Returns:
        str: Empty string if valid, otherwise a descriptive error message.
    """
    return common.review_and_capture(value, approve.validated_at)


def quantity(value: str) -> str:
    """
    Validate a quantity string.

    Args:
        value (str): The quantity string to review.

    Returns:
        str: Empty string if valid, otherwise a descriptive error message.
    """
    return common.review_and_capture(value, approve.quantity)


def designator(value: str) -> str:
    """
    Validate a designator string.

    Args:
        value (str): The designator string to review.

    Returns:
        str: Empty string if valid, otherwise a descriptive error message.
    """
    return common.review_and_capture(value, approve.designator)


def unit_price(value: str) -> str:
    """
    Validate a unit price string.

    Args:
        value (str): The unit price string to review.

    Returns:
        str: Empty string if valid, otherwise a descriptive error message.
    """
    return common.review_and_capture(value, approve.unit_price)


def sub_total(value: str) -> str:
    """
    Validate a sub-total string.

    Args:
        value (str): The sub-total string to review.

    Returns:
        str: Empty string if valid, otherwise a descriptive error message.
    """
    return common.review_and_capture(value, approve.sub_total)
