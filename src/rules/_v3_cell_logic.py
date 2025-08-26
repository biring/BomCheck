"""
Validation functions for enforcing cross cell logic.

This module enforces relational (multi‑cell) constraints between fields in a single BOM `Row`—for example, ensuring `qty` is consistent with `item`, `designator`, `unit_price`, and `sub_total`. Each validator raises `ValueError` on failure and otherwise succeeds silently. If a base cell value fails its own primitive validation, the corresponding cross‑field check is skipped by design.

Example Usage:
    # Preferred usage via public package interface:
    # Not exposed publicly; this is an internal module.

    # Direct module usage (acceptable in unit tests or internal scripts only):
    import src.rules._v3_cell_logic as cl
    from src.models.interfaces import Row

    row = Row(item="2", qty="2", designator="C1,C2", unit_price="0.25", sub_total="0.50")
    cl.assert_subtotal_matches_product(row)

Dependencies:
    - Python >= 3.9
    - Standard Library: typing
    - Internal:
     - src.utils.parser  (string → int/float/empty parsing helpers)
     - src.models.interfaces.Row  (row data model)

Notes:
    - Fail‑fast: each rule raises `ValueError` with a clear message on violation.
    - Skip‑on‑invalid: if a field cannot be parsed by `src.utils.parser`, the rule is skipped.
    - Designator parsing uses raw comma split without trimming; upstream normalization is expected.
    - Monetary/product checks currently use exact float equality; provide normalized inputs to avoid rounding artifacts (e.g., "0.50" × "2" == "1.00").
    - Internal module: `__all__` is empty; these functions are not part of the public API. Prefer package‑level re‑exports if/when provided.

License:
 - Internal Use Only
"""

__all__ = []  # Internal-only; not part of public API

from src.models.interfaces import Row
import src.utils.parser as p


def assert_quantity_positive_when_item_positive(row: Row) -> None:
    """
    Ensure quantity is greater than zero when `item` is a positive integer.

    Validates `row.qty` only when `row.item` is a positive integer. If any base fields are invalid, the check is skipped.

    Args:
        row (Row): BOM row containing `item` and `qty` to validate.

    Returns:
        None: Succeeds silently if the rule is satisfied.

    Raises:
        ValueError: If `item >= 1` and `qty <= 0.0`.
    """
    # Validate cell value
    try:
        item = p.parse_to_integer(row.item)  # And item is an integer
        quantity = p.parse_to_float(row.qty)  # And qty is type float
    except ValueError:
        return  # Skip logic validation if cell validation fails

    # Rule: if item is >=1, quantity must be > 0
    if item >= 1 and quantity <= 0.0:
        raise ValueError(
            f"'{row.qty}' must be more than zero when item '{row.item}' is more than zero.")


def assert_quantity_zero_when_item_blank(row: Row) -> None:
    """
    Ensure quantity is zero when `item` is blank.

    Validates `row.qty` is zero, only when `row.item` is an empty string. If any base fields are invalid, the check is skipped.

    Args:
        row (Row): BOM row containing `item` and `qty` to validate.

    Returns:
        None: Succeeds silently if the rule is satisfied.

    Raises:
        ValueError: If `item` is blank and `qty != 0.0`.
    """
    # Validate cell value
    try:
        item = p.parse_to_empty_string(row.item)  # And item is empty
        qty = p.parse_to_float(row.qty)  # And qty is type float
    except ValueError:
        return  # Skip logic validation if cell validation fails

    # Rule: if item is blank, quantity must be exactly zero
    if item == "" and qty != 0.0:
        raise ValueError(f"'{row.qty}' must be zero when item '{row.item}' is blank.")


def assert_designator_required_for_positive_item_and_qty(row: Row) -> None:
    """
    Require a non-empty designator when item and quantity are positive integer.

    Validates that `row.designator` is non-empty when both `item >= 1` and `qty ≥ 1`. If any base fields are invalid, the check is skipped.

    Args:
        row (Row): BOM row containing `item`, `qty`, and `designator`.

    Returns:
        None: Succeeds silently if the rule is satisfied.

    Raises:
        ValueError: If `item > 0` and `qty ≥ 1.0` but `designator` is empty.
    """
    # Validate cell value
    try:
        item = p.parse_to_integer(row.item)  # And item is an integer
        qty = p.parse_to_integer(row.qty)  # And qty is an integer
    except ValueError:
        return  # Skip logic validation if cell validation fails

    # Rule: if item > 0 and quantity ≥ 1.0, designator must be present (non-empty)
    if item > 0 and qty >= 1:
        if row.designator == "":
            raise ValueError(f"'{row.designator}' must be listed when item '{row.item}' is "
                             f"more than zero and quantity '{row.qty}' is >= 1.0.")


def assert_designator_count_matches_quantity(row: Row) -> None:
    """
    Ensure the count of comma-separated designators equals the quantity when qty ≥ 1.

    Counts designators by splitting on commas (no trimming). If any base fields are invalid, the check is skipped.

    Args:
        row (Row): BOM row with `qty` and `designator`.

    Returns:
        None: Succeeds silently if the rule is satisfied.

    Raises:
        ValueError: If `qty ≥ 1` and the number of designators does not equal `qty`.
    """
    # Validate cell value
    try:
        qty = p.parse_to_integer(row.qty)
        designator_count = len([item for item in row.designator.split(",")])
    except ValueError:
        return  # Skip logic validation if cell validation fails

    # Rule: when quantity ≥ 1.0, designator count must equal quantity
    if qty >= 1.0:
        if qty != designator_count:
            raise ValueError(f"'{row.designator}' do not match qty '{row.qty}'.")


def assert_unit_price_positive_when_quantity_positive(row: Row):
    """
    Ensure unit price is greater than zero when quantity is greater than zero.

    Validates `row.unit_price` only when `row.qty > 0.0`. If any base fields are invalid, the check is skipped.

    Args:
        row (Row): BOM row with `qty` and `unit_price`.

    Returns:
        None: Succeeds silently if the rule is satisfied.

    Raises:
        ValueError: If `qty > 0.0` and `unit_price <= 0.0`.
    """
    # Validate cell value
    try:
        qty = p.parse_to_float(row.qty)
        unit_price = p.parse_to_float(row.unit_price)
    except ValueError:
        return  # Skip logic validation if cell validation fails

    # Rule: if quantity > 0, price per unit must be > 0
    if qty > 0.0 >= unit_price:
        raise ValueError(
            f"'{row.unit_price}' must be more than zero when quantity '{row.qty}' is more than zero.")


def assert_subtotal_zero_when_quantity_zero(row: Row):
    """
    Ensure subtotal is zero when quantity is zero.

    Validates `row.sub_total` only when `row.qty == 0.0`. If any base fields are invalid, the check is skipped.

    Args:
        row (Row): BOM row with `qty` and `sub_total`.

    Returns:
        None: Succeeds silently if the rule is satisfied.

    Raises:
        ValueError: If `qty == 0.0` and `sub_total != 0.0`.
    """
    # Validate cell value
    try:
        qty = p.parse_to_float(row.qty)
        subtotal = p.parse_to_float(row.sub_total)
    except ValueError:
        return  # Skip logic validation if cell validation fails

    # Rule: if quantity is exactly zero, subtotal must be exactly zero
    if qty == 0.0 and subtotal != 0.0:
        raise ValueError(f"'{row.sub_total}' must be zero when quantity '{row.qty}' is zero.")


def assert_subtotal_matches_product(row: Row) -> None:
    """
    Ensure that the subtotal matches the product of quantity and unit price.

    This function checks whether the `sub_total` value in a BOM row equals `qty * unit_price`. Check is skipped if the input values themselves are invalid.

    Args:
        row (Row): BOM row containing `qty`, `unit_price`, and `sub_total` string values to be validated.

    Returns:
        None: Succeeds silently if the rule is satisfied.

    Raises:
        ValueError: If `qty` is greater than zero and the subtotal does not equal `qty * unit_price`.
    """
    # Validate cell value
    try:
        qty = p.parse_to_float(row.qty)
        unit_price = p.parse_to_float(row.unit_price)
        sub_total = p.parse_to_float(row.sub_total)
    except ValueError:
        return  # Skip logic validation if cell validation fails

    if qty > 0.0 and unit_price > 0.0:
        # Subtotal must equal quantity * unit price
        # To account for floating point rounding error we use error range instead of absolute error
        if sub_total != round(qty * unit_price, 6) :
            raise ValueError(
                f"'{row.sub_total}' must equal quantity '{row.qty}' × unit price '{row.unit_price}'.")
