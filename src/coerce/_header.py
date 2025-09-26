"""
Coercers for BOM header fields.

This module applies ordered text rules and returns a normalized value plus a human-readable change log for each field, using shared rule sets and a common engine. It formats per-rule messages via a standardized template and only emits log entries when a change actually occurred.

Example Usage:
    # Preferred usage via package interface:
    # from src.rules import interfaces as rules
    # value, log = rules.coerce.board_name("  Power   PCBA ")

    # Direct usage (internal scripts or unit tests only):
    from src.rules.coerce import _header as header
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

from src.models import interfaces as models
from src.coerce import _common as common
from src.coerce import _constants as constant

COERCE_MSG = "'{a}' changed from '{b}' to '{c}'. {d}"


def _change_log(field: str, result: common.Result) -> tuple[str, ...]:
    change_log: list[str] = []
    # Optional guard; keeps log empty if no effective change
    if result.value_in != result.value_out:
        for entry in result.logs:
            change_log.append(
                COERCE_MSG.format(a=field, b=entry.before, c=entry.after, d=entry.description)
            )
    return tuple(change_log)


def model_number(str_in: str) -> tuple[str, tuple[str, ...]]:
    """
    Coerce/clean input string to model number format.
    
    Args:
        str_in (str): The string to coerce.

    Returns:
        tuple[str, tuple[str, ...]]: (coerced_value, change_log_messages)
    """
    result = common.apply_coerce(str_in, constant.MODEL_NUMBER)
    change_log = _change_log(models.HeaderFields.MODEL_NUMBER, result)
    return result.value_out, change_log


def board_name(str_in: str) -> tuple[str, tuple[str, ...]]:
    """
    Coerce/clean input string to board name.

    Args:
        str_in (str): The string to coerce.

    Returns:
        tuple[str, tuple[str, ...]]: (coerced_value, change_log_messages)
    """
    result = common.apply_coerce(str_in, constant.BOARD_NAME)
    change_log = _change_log(models.HeaderFields.BOARD_NAME, result)
    return result.value_out, change_log


def board_supplier(str_in: str) -> tuple[str, tuple[str, ...]]:
    """
    Coerce/clean input string to board supplier format.

    Args:
        str_in (str): The string to coerce.

    Returns:
        tuple[str, tuple[str, ...]]: (coerced_value, change_log_messages)
    """
    result = common.apply_coerce(str_in, constant.BOARD_SUPPLIER)
    change_log = _change_log(models.HeaderFields.BOARD_SUPPLIER, result)
    return result.value_out, change_log


def build_stage(str_in: str) -> tuple[str, tuple[str, ...]]:
    """
    Coerce/clean input string to build stage format.

    Args:
        str_in (str): The string to coerce.

    Returns:
        tuple[str, tuple[str, ...]]: (coerced_value, change_log_messages)
    """
    result = common.apply_coerce(str_in, constant.BUILD_STAGE)
    change_log = _change_log(models.HeaderFields.BUILD_STAGE, result)
    return result.value_out, change_log


def bom_date(str_in: str) -> tuple[str, tuple[str, ...]]:
    """
    Coerce/clean input string to bom date format.

    Args:
        str_in (str): The string to coerce.

    Returns:
        tuple[str, tuple[str, ...]]: (coerced_value, change_log_messages)
    """
    result = common.apply_coerce(str_in, constant.BOM_DATE)
    change_log = _change_log(models.HeaderFields.BOM_DATE, result)
    return result.value_out, change_log


def material_cost(str_in: str) -> tuple[str, tuple[str, ...]]:
    """
    Coerce/clean input string to material cost format.

    Args:
        str_in (str): The string to coerce.

    Returns:
        tuple[str, tuple[str, ...]]: (coerced_value, change_log_messages)
    """
    result = common.apply_coerce(str_in, constant.MATERIAL_COST)
    change_log = _change_log(models.HeaderFields.MATERIAL_COST, result)
    return result.value_out, change_log


def overhead_cost(str_in: str) -> tuple[str, tuple[str, ...]]:
    """
    Coerce/clean input string to overhead cost format.

    Args:
        str_in (str): The string to coerce.

    Returns:
        tuple[str, tuple[str, ...]]: (coerced_value, change_log_messages)
    """
    result = common.apply_coerce(str_in, constant.OVERHEAD_COST)
    change_log = _change_log(models.HeaderFields.OVERHEAD_COST, result)
    return result.value_out, change_log


def total_cost(str_in: str) -> tuple[str, tuple[str, ...]]:
    """
    Coerce/clean input string to total cost format.

    Args:
        str_in (str): The string to coerce.

    Returns:
        tuple[str, tuple[str, ...]]: (coerced_value, change_log_messages)
    """
    result = common.apply_coerce(str_in, constant.TOTAL_COST)
    change_log = _change_log(models.HeaderFields.TOTAL_COST, result)
    return result.value_out, change_log
