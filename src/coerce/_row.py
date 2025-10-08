"""
Coercers for BOM row fields.

This module applies ordered text rules and returns a normalized value plus a human-readable change log for each field, using shared rule sets and a common engine. It formats per-rule messages via a standardized template and only emits log entries when a change actually occurred.

Example Usage:
    # Preferred usage via package interface:
    from src.coerce import interfaces as coerce
    result = coerce.designator(" R1, r2,  r3,")

    # Direct usage (internal scripts or unit tests only):
    from src.coerce import _row as row
    result = row.designator(" R1, r2,  r3,")

Dependencies:
    - Python >= 3.10
    - Standard Library: typing
    - Internal: src.rules.coerce._common (Result, apply_coerce), src.rules.coerce._constants (field rule sets), src.models.interfaces (HeaderFields)

Notes:
    - Rule application order is deterministic and handled by the shared engine in _common.
    - Intended for internal use behind the rules interfaces facade to preserve API boundaries.

License:
    - Internal Use Only
"""
__all__ = []  # Internal-only; not part of public API. Star import from this module gets nothing.

from src.models import interfaces as mdl
from src.coerce import _common as common
from src.coerce import _rules as rule


def item(str_in: str) -> common.Result:
    """
    Coerce/clean input string to item format.

    Args:
        str_in (str): The string to coerce.

    Returns:
        Result: A coercion result object containing:
            - value_in (str): The original input string.
            - value_out (str): The normalized output string after applying rules.
            - logs (list[Log]): Structured records of each applied rule (before, after, description). Empty if no changes were made.
    """
    return common.apply_coerce(str_in, rule.ITEM, mdl.RowFields.ITEM)


def component_type(str_in: str) -> common.Result:
    """
    Coerce/clean input string to item format.

    Args:
        str_in (str): The string to coerce.

    Returns:
        Result: A coercion result object containing:
            - value_in (str): The original input string.
            - value_out (str): The normalized output string after applying rules.
            - logs (list[Log]): Structured records of each applied rule (before, after, description). Empty if no changes were made.
    """
    return common.apply_coerce(str_in, rule.COMPONENT_TYPE, mdl.RowFields.COMPONENT)


def device_package(str_in: str) -> common.Result:
    """
    Coerce/clean input string to item format.

    Args:
        str_in (str): The string to coerce.

    Returns:
        Result: A coercion result object containing:
            - value_in (str): The original input string.
            - value_out (str): The normalized output string after applying rules.
            - logs (list[Log]): Structured records of each applied rule (before, after, description). Empty if no changes were made.
    """
    return common.apply_coerce(str_in, rule.DEVICE_PACKAGE, mdl.RowFields.PACKAGE)


def description(str_in: str) -> common.Result:
    """
    Coerce/clean input string to item format.

    Args:
        str_in (str): The string to coerce.

    Returns:
        Result: A coercion result object containing:
            - value_in (str): The original input string.
            - value_out (str): The normalized output string after applying rules.
            - logs (list[Log]): Structured records of each applied rule (before, after, description). Empty if no changes were made.
    """
    return common.apply_coerce(str_in, rule.DESCRIPTION, mdl.RowFields.DESCRIPTION)


def units(str_in: str) -> common.Result:
    """
    Coerce/clean input string to item format.

    Args:
        str_in (str): The string to coerce.

    Returns:
        Result: A coercion result object containing:
            - value_in (str): The original input string.
            - value_out (str): The normalized output string after applying rules.
            - logs (list[Log]): Structured records of each applied rule (before, after, description). Empty if no changes were made.
    """
    return common.apply_coerce(str_in, rule.UNITS, mdl.RowFields.UNITS)


def classification(str_in: str) -> common.Result:
    """
    Coerce/clean input string to item format.

    Args:
        str_in (str): The string to coerce.

    Returns:
        Result: A coercion result object containing:
            - value_in (str): The original input string.
            - value_out (str): The normalized output string after applying rules.
            - logs (list[Log]): Structured records of each applied rule (before, after, description). Empty if no changes were made.
    """
    return common.apply_coerce(str_in, rule.CLASSIFICATION, mdl.RowFields.CLASSIFICATION)


def manufacturer(str_in: str) -> common.Result:
    """
    Coerce/clean input string to item format.

    Args:
        str_in (str): The string to coerce.

    Returns:
        Result: A coercion result object containing:
            - value_in (str): The original input string.
            - value_out (str): The normalized output string after applying rules.
            - logs (list[Log]): Structured records of each applied rule (before, after, description). Empty if no changes were made.
    """
    return common.apply_coerce(str_in, rule.MANUFACTURER, mdl.RowFields.MANUFACTURER)


def mfg_part_number(str_in: str) -> common.Result:
    """
    Coerce/clean input string to item format.

    Args:
        str_in (str): The string to coerce.

    Returns:
        Result: A coercion result object containing:
            - value_in (str): The original input string.
            - value_out (str): The normalized output string after applying rules.
            - logs (list[Log]): Structured records of each applied rule (before, after, description). Empty if no changes were made.
    """
    return common.apply_coerce(str_in, rule.MFG_PART_NUMBER, mdl.RowFields.MFG_PART_NO)


def ul_vde_number(str_in: str) -> common.Result:
    """
    Coerce/clean input string to item format.

    Args:
        str_in (str): The string to coerce.

    Returns:
        Result: A coercion result object containing:
            - value_in (str): The original input string.
            - value_out (str): The normalized output string after applying rules.
            - logs (list[Log]): Structured records of each applied rule (before, after, description). Empty if no changes were made.
    """
    return common.apply_coerce(str_in, rule.UL_VDE_NUMBER, mdl.RowFields.UL_VDE_NUMBER)


def validated_at(str_in: str) -> common.Result:
    """
    Coerce/clean input string to item format.

    Args:
        str_in (str): The string to coerce.

    Returns:
        Result: A coercion result object containing:
            - value_in (str): The original input string.
            - value_out (str): The normalized output string after applying rules.
            - logs (list[Log]): Structured records of each applied rule (before, after, description). Empty if no changes were made.
    """
    return common.apply_coerce(str_in, rule.VALIDATED_AT, mdl.RowFields.VALIDATED_AT)


def quantity(str_in: str) -> common.Result:
    """
    Coerce/clean input string to item format.

    Args:
        str_in (str): The string to coerce.

    Returns:
        Result: A coercion result object containing:
            - value_in (str): The original input string.
            - value_out (str): The normalized output string after applying rules.
            - logs (list[Log]): Structured records of each applied rule (before, after, description). Empty if no changes were made.
    """
    return common.apply_coerce(str_in, rule.QTY, mdl.RowFields.QTY)


def designator(str_in: str) -> common.Result:
    """
    Coerce/clean input string to item format.

    Args:
        str_in (str): The string to coerce.

    Returns:
        Result: A coercion result object containing:
            - value_in (str): The original input string.
            - value_out (str): The normalized output string after applying rules.
            - logs (list[Log]): Structured records of each applied rule (before, after, description). Empty if no changes were made.
    """
    return common.apply_coerce(str_in, rule.DESIGNATOR, mdl.RowFields.DESIGNATOR)


def unit_price(str_in: str) -> common.Result:
    """
    Coerce/clean input string to item format.

    Args:
        str_in (str): The string to coerce.

    Returns:
        Result: A coercion result object containing:
            - value_in (str): The original input string.
            - value_out (str): The normalized output string after applying rules.
            - logs (list[Log]): Structured records of each applied rule (before, after, description). Empty if no changes were made.
    """
    return common.apply_coerce(str_in, rule.UNIT_PRICE, mdl.RowFields.UNIT_PRICE)


def sub_total(str_in: str) -> common.Result:
    """
    Coerce/clean input string to item format.

    Args:
        str_in (str): The string to coerce.

    Returns:
        Result: A coercion result object containing:
            - value_in (str): The original input string.
            - value_out (str): The normalized output string after applying rules.
            - logs (list[Log]): Structured records of each applied rule (before, after, description). Empty if no changes were made.
    """
    return common.apply_coerce(str_in, rule.SUB_TOTAL, mdl.RowFields.SUB_TOTAL)
