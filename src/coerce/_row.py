"""
Coercers for BOM row fields using shared regex-based rule sets.

This module defines per-field coercion functions that normalize BOM row text values (e.g., designator, component type, manufacturer, unit price) through ordered regex rules. Each function applies a deterministic rule sequence and returns the cleaned value along with a tuple of human-readable log messages.

Example Usage:
    # Preferred usage via package interface:
    from src.coerce import interfaces as coerce
    value, log = coerce.designator(" R1, r2,  r3, ")
    print(value)  # "R1,R2,R3"

    # Direct internal access (for tests or internal scripts only):
    from src.coerce import _row
    value, log = _row.price(" 1.23\n")
    print(value)  # "1.23"

Dependencies:
    - Python >= 3.10
    - Standard Library: typing
    - Internal: src.coerce._helper (apply_rule), src.coerce._rules (field rule sets), src.models.interfaces (RowFields)

Notes:
    - Only effective substitutions are logged, producing traceable and deterministic output.
    - Rule application order is deterministic and handled by the shared engine in _helper.
    - Intended for internal use behind the rules interfaces facade to preserve API boundaries.

License:
    - Internal Use Only
"""
__all__ = []  # Internal-only; not part of public API. Star import from this module gets nothing.

from src.models import interfaces as mdl
from . import _helper as helper
from . import _rules as rule


def item(str_in: str) -> tuple[str, tuple[str, ...]]:
    """
    Coerce item string.

    Args:
        str_in (str): Raw item string.

    Returns:
        tuple[str, tuple[str, ...]]: (coerced value, change log)
    """
    result = helper.apply_rule(str_in, rule.ITEM, mdl.RowFields.ITEM)

    return result.coerced_value, result.render_changes()


def component_type(str_in: str) -> tuple[str, tuple[str, ...]]:
    """
    Coerce component type string.

    Args:
        str_in (str): Raw component-type string.

    Returns:
        tuple[str, tuple[str, ...]]: (coerced value, change log)
    """
    result = helper.apply_rule(str_in, rule.COMPONENT_TYPE, mdl.RowFields.COMPONENT)

    return result.coerced_value, result.render_changes()


def device_package(str_in: str) -> tuple[str, tuple[str, ...]]:
    """
    Coerce package footprint string.

    Args:
        str_in (str): Raw package string.

    Returns:
        tuple[str, tuple[str, ...]]: (coerced value, change log)
    """
    result = helper.apply_rule(str_in, rule.DEVICE_PACKAGE, mdl.RowFields.PACKAGE)

    return result.coerced_value, result.render_changes()


def description(str_in: str) -> tuple[str, tuple[str, ...]]:
    """
    Coerce description string.

    Args:
        str_in (str): Raw description string.

    Returns:
        tuple[str, tuple[str, ...]]: (coerced value, change log)
    """
    result = helper.apply_rule(str_in, rule.DESCRIPTION, mdl.RowFields.DESCRIPTION)

    return result.coerced_value, result.render_changes()


def units(str_in: str) -> tuple[str, tuple[str, ...]]:
    """
    Coerce units string.

    Args:
        str_in (str): Raw units string.

    Returns:
        tuple[str, tuple[str, ...]]: (coerced value, change log)
    """
    result = helper.apply_rule(str_in, rule.UNITS, mdl.RowFields.UNITS)

    return result.coerced_value, result.render_changes()


def classification(str_in: str) -> tuple[str, tuple[str, ...]]:
    """
    Coerce classification string.

    Args:
        str_in (str): Raw classification string.

    Returns:
        tuple[str, tuple[str, ...]]: (coerced value, change log)
    """
    result = helper.apply_rule(str_in, rule.CLASSIFICATION, mdl.RowFields.CLASSIFICATION)

    return result.coerced_value, result.render_changes()


def manufacturer(str_in: str) -> tuple[str, tuple[str, ...]]:
    """
    Coerce manufacturer name string.

    Args:
        str_in (str): Raw manufacturer name string.

    Returns:
        tuple[str, tuple[str, ...]]: (coerced value, change log)
    """
    result = helper.apply_rule(str_in, rule.MANUFACTURER, mdl.RowFields.MANUFACTURER)

    return result.coerced_value, result.render_changes()


def mfg_part_number(str_in: str) -> tuple[str, tuple[str, ...]]:
    """
    Coerce manufacturer part numbers string.

    Args:
        str_in (str): Raw manufacturer part number string.

    Returns:
        tuple[str, tuple[str, ...]]: (coerced value, change log)
    """
    result = helper.apply_rule(str_in, rule.MFG_PART_NUMBER, mdl.RowFields.MFG_PART_NO)
    return result.coerced_value, result.render_changes()


def ul_vde_number(str_in: str) -> tuple[str, tuple[str, ...]]:
    """
    Coerce UL/VDE numbers string.

    Args:
        str_in (str): Raw UL/VDE number string.

    Returns:
        tuple[str, tuple[str, ...]]: (coerced value, change log)
    """
    result = helper.apply_rule(str_in, rule.UL_VDE_NUMBER, mdl.RowFields.UL_VDE_NUMBER)

    return result.coerced_value, result.render_changes()


def validated_at(str_in: str) -> tuple[str, tuple[str, ...]]:
    """
    Coerce validation at string.

    Args:
        str_in (str): Raw validation at string.

    Returns:
        tuple[str, tuple[str, ...]]: (coerced value, change log)
    """
    result = helper.apply_rule(str_in, rule.VALIDATED_AT, mdl.RowFields.VALIDATED_AT)
    return result.coerced_value, result.render_changes()


def quantity(str_in: str) -> tuple[str, tuple[str, ...]]:
    """
    Coerce quantity string.

    Args:
        str_in (str): Raw quantity string.

    Returns:
        tuple[str, tuple[str, ...]]: (coerced value, change log)
    """
    result = helper.apply_rule(str_in, rule.QTY, mdl.RowFields.QTY)

    return result.coerced_value, result.render_changes()


def designator(str_in: str) -> tuple[str, tuple[str, ...]]:
    """
    Coerce designator string.

    Args:
        str_in (str): Raw designator string.

    Returns:
        tuple[str, tuple[str, ...]]: (coerced value, change log)
    """
    result = helper.apply_rule(str_in, rule.DESIGNATOR, mdl.RowFields.DESIGNATOR)

    return result.coerced_value, result.render_changes()


def unit_price(str_in: str) -> tuple[str, tuple[str, ...]]:
    """
    Coerce unit price string.

    Args:
        str_in (str): Raw unit price string.

    Returns:
        tuple[str, tuple[str, ...]]: (coerced value, change log)
    """
    result = helper.apply_rule(str_in, rule.UNIT_PRICE, mdl.RowFields.UNIT_PRICE)

    return result.coerced_value, result.render_changes()


def sub_total(str_in: str) -> tuple[str, tuple[str, ...]]:
    """
    Coerce sub-total string.

    Args:
        str_in (str): Raw sub-total string.

    Returns:
        tuple[str, tuple[str, ...]]: (coerced value, change log)
    """
    result = helper.apply_rule(str_in, rule.SUB_TOTAL, mdl.RowFields.SUB_TOTAL)

    return result.coerced_value, result.render_changes()
