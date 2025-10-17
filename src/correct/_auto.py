"""
Autocorrection helpers for BOM numeric and reference fields.

Provides pure functions that compute corrected values from existing fields and return both the corrected string and a one-line change log suitable for audit trails. Parsing is delegated to shared utilities.

Example Usage:
    # Preferred usage via package interface:
    # Not exposed publicly; this is an internal module.

    # Direct internal access (for tests or internal scripts only):
    import src.correct._auto as auto
    value, log = auto.material_cost(header, rows)

Dependencies:
    - Python >= 3.10
    - Standard Library: re
    - Project Modules: src.models.interfaces, src.utils.parse_to_float, src.approve._common.floats_equal

Notes:
    - Empty change_log indicates no correction was applied
    - Internal-only module; API may change without notice

License:
    - Internal Use Only
"""
__all__ = []  # Internal-only; not part of public API. Star import from this module gets nothing.

import re
from src.models import interfaces as mdl
from src.utils import parse_to_float

# TODO : Reorganize to one shared folder for all rules or make math a utility
from . import _helper as helper

# Strict range pattern: no spaces around the dash, same alpha prefix on both sides
DESIGNATOR_RANGE_RE = re.compile(r"^([A-Za-z]+)(\d+)-\1(\d+)$")

TEMPLATE_AUTOCORRECT_MSG = "'{field}' changed from '{before}' to '{after}'. {reason}"

LOG_DESIGNATOR_EXPAND = "Designator range expanded to remove '-' dash."
LOG_SUBTOTAL_CHANGE = "Sub-total set to the product of Quantity and Designator."
LOG_MATERIAL_COST_CHANGE = "Material cost set to the sum of sub totals."
LOG_TOTAL_COST_CHANGE = "Total cost set to the product of material and overhead cost."

ERR_FLOAT_PARSE = "{field} value '{value}' is not a valid floating point number: {reason}"


def expand_designators(str_in: str) -> tuple[str, str]:
    """
    Expands designator ranges within the sting.

    This function processes a string containing comma-separated reference designators and expands any ranges written in the form "PrefixStart-PrefixEnd". Each expanded value is preserved with its original prefix, while non-range values remain unchanged. The result is returned as a comma-separated string. For example if input is "R1, R3-R6, R12, R45-R43" output will be "R1,R3,R4,R5,R6,R12,R45,R44,R43"

    Notes:
        - The input must be a valid string; no NaN or non-string checks are performed.
        - Ranges must not contain spaces around the dash (e.g., "R3-R6" is valid, "R3 - R6" is not).
        - Both sides of the range must share the same alphabetic prefix.
        - Descending ranges (e.g., "R6-R3") are supported and expanded in reverse order.

    Args:
        str_in (str): designator string, possibly with ranges.

    Returns:
        tuple[str, str]: Range expanded designator string, change log string.
    """

    change_log = ""

    parts = [p.strip() for p in str_in.split(",") if p.strip()]
    expanded_designators: list[str] = []

    for part in parts:
        # Match "PREFIX<start>-PREFIX<end>" with same alpha prefix
        m = DESIGNATOR_RANGE_RE.fullmatch(part)
        if m:
            prefix, start_str, end_str = m.groups()
            start_idx, end_idx = int(start_str), int(end_str)
            # Support both ascending and descending ranges
            step = 1 if end_idx >= start_idx else -1
            expanded_designators.extend(f"{prefix}{i}" for i in range(start_idx, end_idx + step, step))
        else:
            expanded_designators.append(part)

    str_out = ",".join(expanded_designators)

    # Emit audit message only when the output differs
    if str_out != str_in:
        change_log = TEMPLATE_AUTOCORRECT_MSG.format(
            field=mdl.RowFields.DESIGNATOR,
            before=str_in,
            after=str_out,
            reason=LOG_DESIGNATOR_EXPAND)

    return str_out, change_log


def material_cost(header: mdl.Header, rows: tuple[mdl.Row, ...]) -> tuple[str, str]:
    """
    Autocorrect the material cost to sum of the sub-total.

    Base fields of sub-total and material cost must be float parse compatible.

    Args:
        header (mdl.Hoard): Bom header containing the material cost to autocorrect.
        rows (tuple[mdl.Row, ...]): list of BOM row containing the sub-total used to calculate the correct material cost.

    Returns:
     tuple[str, str]: correct material cost string, change log string.

    Raises:
        ValueError: If base fields cannot be parsed as float.
    """
    str_out = header.material_cost
    change_log = ""
    material_cost_out = 0

    # Get float values for base fields
    for row in rows:
        try:
            sub_total_in = parse_to_float(row.sub_total)
            material_cost_out += sub_total_in
        except ValueError as err:
            raise ValueError(ERR_FLOAT_PARSE.format(
                field=mdl.RowFields.SUB_TOTAL,
                value=row.sub_total,
                reason=err)
            )

    try:
        material_cost_in = parse_to_float(header.material_cost)
    except ValueError as err:
        raise ValueError(ERR_FLOAT_PARSE.format(
            field=mdl.HeaderFields.MATERIAL_COST,
            value=header.material_cost,
            reason=err)
        )

    # Compare with tolerance to avoid float noise
    if not helper.floats_equal(material_cost_in, material_cost_out):
        str_out = str(material_cost_out)
        change_log = TEMPLATE_AUTOCORRECT_MSG.format(
            field=mdl.HeaderFields.MATERIAL_COST,
            before=material_cost_in,
            after=material_cost_out,
            reason=LOG_MATERIAL_COST_CHANGE
        )

    return str_out, change_log


def sub_total(row: mdl.Row) -> tuple[str, str]:
    """
    Autocorrect the sub-total to the product of quantity and unit price.

    Base fields of quantity, unit price and sub-total must be float parse compatible.

    Args:
        row (Row): BOM row containing the sub-total to autocorrect.

    Returns:
     tuple[str, str]: correct sub-total string, change log string.

    Raises:
        ValueError: If base fields cannot be parsed as float.
    """
    str_out = row.sub_total
    change_log = ""

    # Get float values for base fields
    try:
        qty_in = parse_to_float(row.qty)
    except ValueError as err:
        raise ValueError(ERR_FLOAT_PARSE.format(
            field=mdl.RowFields.QTY,
            value=row.qty,
            reason=err)
        )

    try:
        unit_price_in = parse_to_float(row.unit_price)
    except ValueError as err:
        raise ValueError(ERR_FLOAT_PARSE.format(
            field=mdl.RowFields.UNIT_PRICE,
            value=row.unit_price,
            reason=err)
        )
    try:
        sub_total_in = parse_to_float(row.sub_total)
    except ValueError as err:
        raise ValueError(ERR_FLOAT_PARSE.format(
            field=mdl.RowFields.SUB_TOTAL,
            value=row.sub_total,
            reason=err)
        )

    sub_total_out = round(qty_in * unit_price_in, 6)

    # Compare with tolerance to avoid float noise
    if not helper.floats_equal(sub_total_in, sub_total_out):
        str_out = str(sub_total_out)
        change_log = TEMPLATE_AUTOCORRECT_MSG.format(
            field=mdl.RowFields.SUB_TOTAL,
            before=sub_total_in,
            after=sub_total_out,
            reason=LOG_SUBTOTAL_CHANGE
        )

    return str_out, change_log


def total_cost(header: mdl.Header) -> tuple[str, str]:
    """
    Autocorrect the total cost to the product of material cost and overhead cost.

    Base fields of material overhead and total cost must be float parse compatible.

    Args:
        header (Header): BOM header containing the total cost to autocorrect.

    Returns:
        tuple[str, str]: correct total cost string, change log string.

    Raises:
        ValueError: If base fields cannot be parsed as float.
    """
    str_out = header.total_cost
    change_log = ""

    # Get float values for base fields
    try:
        material_cost_in = parse_to_float(header.material_cost)
    except ValueError as err:
        raise ValueError(ERR_FLOAT_PARSE.format(
            field=mdl.HeaderFields.MATERIAL_COST,
            value=header.material_cost,
            reason=err)
        )

    try:
        overhead_cost_in = parse_to_float(header.overhead_cost)
    except ValueError as err:
        raise ValueError(ERR_FLOAT_PARSE.format(
            field=mdl.HeaderFields.MATERIAL_COST,
            value=header.material_cost,
            reason=err)
        )
    try:
        total_cost_in = parse_to_float(header.total_cost)
    except ValueError as err:
        raise ValueError(ERR_FLOAT_PARSE.format(
            field=mdl.HeaderFields.MATERIAL_COST,
            value=header.material_cost,
            reason=err)
        )

    total_cost_out = round(material_cost_in + overhead_cost_in, 6)

    # Compare with tolerance to avoid float noise
    if not helper.floats_equal(total_cost_in, total_cost_out):
        str_out = str(total_cost_out)
        change_log = TEMPLATE_AUTOCORRECT_MSG.format(
            field=mdl.HeaderFields.TOTAL_COST,
            before=total_cost_in,
            after=total_cost_out,
            reason=LOG_SUBTOTAL_CHANGE
        )

    return str_out, change_log
