"""
Coercers for BOM header fields.

This module applies ordered text rules and returns a normalized value plus a human-readable change log for each field, using shared rule sets and a common engine. It formats per-rule messages via a standardized template and only emits log entries when a change actually occurred.

Example Usage:
    # Preferred usage via package interface:
    # from src.coerce import interfaces as coerce
    # value, log = coerce.board_name("  Power   PCBA ")

    # Direct usage (internal scripts or unit tests only):
    from src.coerce import _header as header
    value, log = header.board_name("  Power   PCBA ")

Dependencies:
    - Python >= 3.10
    - Standard Library: typing
    - Internal: src.rules.coerce._common (Result, apply_coerce), src.rules.coerce._constants (field rule sets), src.models.interfaces (HeaderFields)

Notes:
    - Each function returns (value, change_log_messages).
    - Rule application order is deterministic and handled by the shared engine in _common.
    - Change logs are formatted consistently and produced only when input != output.
    - Intended for internal use behind the rules interfaces facade to preserve API boundaries.

License:
    - Internal Use Only
"""
__all__ = []  # Internal-only; not part of public API. Star import from this module gets nothing.

from src.coerce import _common as common
from src.coerce import _rules as rule


def model_number(str_in: str) -> common.Result:
    """
    Coerce/clean input string to model number format.
    
    Args:
        str_in (str): The string to coerce.

    Returns:
        Result: A coercion result object containing:
            - value_in (str): The original input string.
            - value_out (str): The normalized output string after applying rules.
            - logs (list[Log]): Structured records of each applied rule (before, after, description). Empty if no changes were made.
    """
    return common.apply_coerce(str_in, rule.MODEL_NUMBER)


def board_name(str_in: str) -> common.Result:
    """
    Coerce/clean input string to board name.

    Args:
        str_in (str): The string to coerce.

    Returns:
        Result: A coercion result object containing:
            - value_in (str): The original input string.
            - value_out (str): The normalized output string after applying rules.
            - logs (list[Log]): Structured records of each applied rule (before, after, description). Empty if no changes were made.
    """
    return common.apply_coerce(str_in, rule.BOARD_NAME)


def board_supplier(str_in: str) -> common.Result:
    """
    Coerce/clean input string to board supplier format.

    Args:
        str_in (str): The string to coerce.

    Returns:
        Result: A coercion result object containing:
            - value_in (str): The original input string.
            - value_out (str): The normalized output string after applying rules.
            - logs (list[Log]): Structured records of each applied rule (before, after, description). Empty if no changes were made.
    """
    return common.apply_coerce(str_in, rule.BOARD_SUPPLIER)


def build_stage(str_in: str) -> common.Result:
    """
    Coerce/clean input string to build stage format.

    Args:
        str_in (str): The string to coerce.

    Returns:
        Result: A coercion result object containing:
            - value_in (str): The original input string.
            - value_out (str): The normalized output string after applying rules.
            - logs (list[Log]): Structured records of each applied rule (before, after, description). Empty if no changes were made.
    """
    return common.apply_coerce(str_in, rule.BUILD_STAGE)


def bom_date(str_in: str) -> common.Result:
    """
    Coerce/clean input string to bom date format.

    Args:
        str_in (str): The string to coerce.

    Returns:
        Result: A coercion result object containing:
            - value_in (str): The original input string.
            - value_out (str): The normalized output string after applying rules.
            - logs (list[Log]): Structured records of each applied rule (before, after, description). Empty if no changes were made.
    """
    return common.apply_coerce(str_in, rule.BOM_DATE)


def material_cost(str_in: str) -> common.Result:
    """
    Coerce/clean input string to material cost format.

    Args:
        str_in (str): The string to coerce.

    Returns:
        Result: A coercion result object containing:
            - value_in (str): The original input string.
            - value_out (str): The normalized output string after applying rules.
            - logs (list[Log]): Structured records of each applied rule (before, after, description). Empty if no changes were made.
    """
    return common.apply_coerce(str_in, rule.MATERIAL_COST)


def overhead_cost(str_in: str) -> common.Result:
    """
    Coerce/clean input string to overhead cost format.

    Args:
        str_in (str): The string to coerce.

    Returns:
        Result: A coercion result object containing:
            - value_in (str): The original input string.
            - value_out (str): The normalized output string after applying rules.
            - logs (list[Log]): Structured records of each applied rule (before, after, description). Empty if no changes were made.
    """
    return common.apply_coerce(str_in, rule.OVERHEAD_COST)


def total_cost(str_in: str) -> common.Result:
    """
    Coerce/clean input string to total cost format.

    Args:
        str_in (str): The string to coerce.

    Returns:
        Result: A coercion result object containing:
            - value_in (str): The original input string.
            - value_out (str): The normalized output string after applying rules.
            - logs (list[Log]): Structured records of each applied rule (before, after, description). Empty if no changes were made.
    """
    return common.apply_coerce(str_in, rule.TOTAL_COST)
