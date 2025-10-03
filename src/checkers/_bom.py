"""
Checker for Version 3 BOM objects.

Coordinates value-level and logic-level checks across complete BOMs (boards, headers, rows). Accumulates issues as ErrorMsg records via ErrorLog for uniform, printable diagnostics without direct I/O.

Example Usage:
    # Preferred usage via public package interface:
    # Not exposed publicly; this is an internal module.

    # Direct module usage (acceptable in unit tests or internal scripts only):
    from src.checkers import _bom as cb
    result_str = cb.check_v3_bom(...)
    print(result_str)

Dependencies:
    - Python >= 3.10
    - Standard Library: dataclasses
    - Internal:
        - src.models.interfaces (Bom, Board, Header, Row)
        - src.checkers._common (ErrorMsg, ErrorLog)

Notes:
    - Returns a diagnostics string; does not raise on validation errors.
    - Separates value checks and cross-field logic checks.
    - Designed for internal use only; not part of the public API.

License:
 - Internal Use Only
"""

__all__ = []  # Internal-only; not part of public API. Star import from this module gets nothing

from src.review import interfaces as review
from src.models import interfaces as model
from src.checkers import _common as common


def check_bom(bom: model.Bom) -> str:
    """
    Validate a Version 3 BOM and return a diagnostics string.

    Traverses boards, headers, and rows, running value-level and logic-level checks and accumulating issues in an ErrorLog with the format "{file}:{sheet}:{section}:{message}"

    Args:
        bom (model.Bom): Structured BOM with boards, header, and rows.

    Returns:
        str: Printable diagnostics summary from the ErrorLog.

    Raises:
        None: Validation routines only append to the ErrorLog and do not raise.
    """

    # Initialize diagnostics sink and set BOM file context
    errors = common.ErrorLog()
    errors.set_file_name(bom.file_name)

    for board in bom.boards:
        errors.set_sheet_name(board.sheet_name)

        # Validate each row: field-level first, then cross-field logic
        for idx, row in enumerate(board.rows, start=1):
            errors.set_section_name(model.Row.__name__ + ": " + str(idx))
            _check_row_value(errors, row)
            _check_row_logic(errors, row)

        # Validate header logic against rows, then header field values
        errors.set_section_name(model.Header.__name__)
        _check_header_logic(errors, board.header, board.rows)
        _check_header_value(errors, board.header)

    # Render accumulated issues to a single printable string
    return str(errors)


def _check_header_value(errors: common.ErrorLog, header: model.Header) -> None:
    """
    Run value-level validators on header fields.

    Invokes field-specific review functions and appends any ErrorMsg to the provided ErrorLog.

    Args:
        errors (common.ErrorLog): Collector for header validation issues.
        header (model.Header): Header instance with raw field values.

    Returns:
        None

    Raises:
        None
    """

    # Map each header field to its validator
    checks = [
        (review.model_number, header.model_no),
        (review.board_name, header.board_name),
        (review.board_supplier, header.manufacturer),
        (review.build_stage, header.build_stage),
        (review.bom_date, header.date),
        (review.material_cost, header.material_cost),
        (review.overhead_cost, header.overhead_cost),
        (review.total_cost, header.total_cost),
    ]

    # Run validator and append any resulting ErrorMsg
    for fn, val in checks:
        errors.append_error(fn(val))

    return


def _check_header_logic(errors: common.ErrorLog, header: model.Header, rows: tuple[model.Row, ...], ) -> None:
    """
    Run logic-level consistency checks for the header against row data.

    Evaluates derived calculations such as material and total cost and appends any issues to the ErrorLog.

    Args:
        errors (common.ErrorLog): Collector for logic errors.
        header (model.Header): Header subject to cross-field checks.
        rows (tuple[model.Row, ...]): Rows used for derived calculations.

    Returns:
        None

    Raises:
        None
    """
    errors.append_error(review.material_cost_calculation(rows, header))
    errors.append_error(review.total_cost_calculation(header))

    return


def _check_row_value(errors: common.ErrorLog, row: model.Row) -> None:
    """
    Run value-level validators on a single row.

    Applies per-field validators and appends any ErrorMsg to the ErrorLog.

    Args:
        errors (common.ErrorLog): Collector for row validation issues.
        row (model.Row): Row instance to validate at the field level.

    Returns:
        None

    Raises:
        None
    """

    # Map each row field to its validator
    checks = [
        (review.item, row.item),
        (review.component_type, row.component_type),
        (review.device_package, row.device_package),
        (review.description, row.description),
        (review.units, row.unit),
        (review.classification, row.classification),
        (review.mfg_name, row.manufacturer),
        (review.mfg_part_no, row.mfg_part_number),
        (review.ul_vde_number, row.ul_vde_number),
        (review.validated_at, row.validated_at),
        (review.quantity, row.qty),
        (review.designator, row.designator),
        (review.unit_price, row.unit_price),
        (review.sub_total, row.sub_total),
    ]

    # Validate a single field and append any error
    for fn, value in checks:
        errors.append_error(fn(value))

    return


def _check_row_logic(errors: common.ErrorLog, row: model.Row) -> None:
    """
    Run logic-level checks on a single row.

    Evaluates cross-field constraints (e.g., subtotal vs quantity × unit price) and appends issues to the ErrorLog.

    Args:
        errors (common.ErrorLog): Collector for logic errors.
        row (model.Row): Row instance to validate at the logic level.

    Returns:
        None

    Raises:
        None
    """

    # Apply row-level logic rules that combine multiple fields
    checks = [
        review.designator_required,
        review.designator_count,
        review.quantity_zero,
        review.unit_price_specified,
        review.subtotal_zero,
        review.sub_total_calculation,
    ]

    # Append any violation reported by the rule
    for fn in checks:
        errors.append_error(fn(row))

    return
