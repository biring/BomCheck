"""
Checker for Version 3 BOM objects.

This module coordinates value-level and logic-level checks across complete BOMs, including boards, headers, and row entries. It aggregates check errors into structured `ErrorMsg` records with full context (file, sheet, location, field) and provides both programmatic and printable outputs.

Example Usage:
    # Preferred usage via public package interface:
    # Not exposed publicly; this is an internal module.

    # Direct module usage (acceptable in unit tests or internal scripts only):
    import src.checkers._v3_bom as cb
    result_str = cb.check_v3_bom(...)
    print(result_str)

Dependencies:
    - Python >= 3.9
    - Standard Library: dataclasses
    - Internal:
        - src.models.interfaces (Bom, Board, Header, Row)
        - src.utils.parser (string parsing helpers)
        - src.rules.interfaces (value and logic)

Design Notes & Assumptions:
    - Fail-fast philosophy: individual cell checks raise `ValueError` directly.
    - Errors are collected into `ErrorMsg` dataclass instances for uniform reporting.
    - Explicit separation between value-level and logic-level checks for clarity and maintainability.
    - This is an internal module; external consumers should not import directly.

License:
 - Internal Use Only
"""

__all__ = []  # Internal-only; not part of public API. Star import from this module gets nothing*

from dataclasses import dataclass
from src.models.interfaces import Bom, Board, Header, Row, HeaderFields, RowFields
import src.utils as utils
import src.rules.interfaces as rules


# Frozen dataclass ensures immutability for reliable error reporting
@dataclass(frozen=True)
class ErrorMsg:
    """
    Represents a single checker error with full contextual details.

    Each error message captures the file name, sheet name, location (e.g., header or row number), the specific field where the error occurred, and a descriptive error message. This helps in pinpointing the exact location and cause of check failures in BOM parsing.

    Args:
        file_name (str): Name of the BOM file being checked.
        sheet_name (str): Name of the worksheet within the file.
        location (str): Section of the sheet where the error occurred (e.g., "Header" or row number).
        field_name (str): Specific field in the section that failed check.
        message (str): Human-readable error message describing the failure.

    Returns:
        ErrorMsg: A frozen dataclass instance containing full error context.
    """
    file_name: str
    sheet_name: str
    location: str
    field_name: str
    message: str

    def to_string(self) -> str:
        """
        Convert the error message into a standardized printable string.

        Format:
            <file_name> | <sheet_name> | <section> | <field>: <message>

        Returns:
            str: A single-line string suitable for console logs or reports.
        """
        return f"{self.file_name} | {self.sheet_name} | {self.location} | {self.field_name} {self.message}"


def check_v3_bom(bom: Bom) -> str:
    """
    Check a Version 3 BOM and return a printable summary of all errors.

    This function coordinates checks across all boards in the BOM. It collects structured `ErrorMsg` instances and returns them as a single string, with each error on its own line.

    Args:
        bom (Bom): A BOM object containing file name, board headers, and rows.

    Returns:
        str: A newline-separated string where each line represents a checking error.
    """
    errors = _check_boards(bom.file_name, bom.boards)

    # Convert all ErrorMsg objects to their string form
    error_str = "\n".join(error.to_string() for error in errors)

    return error_str


def _check_bom(bom: Bom) -> list[ErrorMsg]:
    """
    Check a Version 3 BOM.

    This internal helper runs all board-level checks for the given BOM and returns a structured list of `ErrorMsg` objects instead of rendering them to strings.

    Args:
        bom (Bom): A BOM object containing file name, board headers, and rows.

    Returns:
        list[ErrorMsg]: A list of checking errors, where each entry contains contextual details (file, sheet, section, field, and message).
    """
    return _check_boards(bom.file_name, bom.boards)


def _check_boards(file_name: str, boards: list[Board]) -> list[ErrorMsg]:
    """
    Check all boards within a BOM.

    Iterates through each board in the BOM and performs header-level and row-level checks. Aggregates all detected errors into a flat list of `ErrorMsg` objects.

    Args:
        file_name (str): The name of the BOM file being checked.
        boards (list[Board]): A collection of board objects to check, each containing a header and a list of rows.

    Returns:
        list[ErrorMsg]: A list of checking errors, each with full context (file name, sheet name, section, field, and descriptive message).
    """

    errors: list[ErrorMsg] = []

    # Iterate through each board and check both header and rows
    for board in boards:
        sheet_name = board.sheet_name

        # Check header fields (model number, board name, costs, etc.)
        errors += _check_header(file_name, sheet_name, board.header)

        # Check row-level values and logic (items, qty, subtotal, etc.)
        errors += _check_rows(file_name, sheet_name, board.rows)

    return errors


def _check_header(file_name: str, sheet_name: str, header: Header) -> list[ErrorMsg]:
    """
    Check a single board's header section and return structured errors.

    Runs field-level assertions (value and format checks) for the BOM header and aggregates any failures into `ErrorMsg` instances. This function is internal and does not raise; downstream callers can render or otherwise process the returned errors.

    Args:
        file_name (str): Name of the BOM file being checked.
        sheet_name (str): Name of the worksheet (board) whose header is checked.
        header (Header): Header record containing metadata and roll-up cost fields.

    Returns:
        list[ErrorMsg]: Zero or more checking errors with full context (file, sheet, section, field, and a descriptive message).

    Raises:
        None: Exceptions from checks are caught and converted into `ErrorMsg`.
    """

    errors: list[ErrorMsg] = []

    # Helper to normalize exceptions from checks into uniform ErrorMsg records.
    def _add_error(field: str, msg: Exception) -> None:
        errors.append(ErrorMsg(file_name, sheet_name, "Header", field, str(msg)))

    try:
        rules.assert_model_number(header.model_no)
    except Exception as exc:
        _add_error(HeaderFields.MODEL_NUMBER, exc)

    try:
        rules.assert_board_name(header.board_name)
    except Exception as exc:
        _add_error(HeaderFields.BOARD_NAME, exc)

    try:
        utils.parse_to_non_empty_string(header.manufacturer)
    except Exception as exc:
        _add_error(HeaderFields.BOARD_SUPPLIER, exc)

    try:
        rules.assert_build_stage(header.build_stage)
    except Exception as exc:
        _add_error(HeaderFields.BUILD_STAGE, exc)

    try:
        rules.assert_date_format(header.date)
    except Exception as exc:
        _add_error(HeaderFields.BOM_DATE, exc)

    try:
        rules.assert_price(header.material_cost)
    except Exception as exc:
        _add_error(HeaderFields.MATERIAL_COST, exc)

    try:
        rules.assert_price(header.overhead_cost)
    except Exception as exc:
        _add_error(HeaderFields.OVERHEAD_COST, exc)

    try:
        rules.assert_price(header.total_cost)
    except Exception as exc:
        _add_error(HeaderFields.TOTAL_COST, exc)

    return errors


def _check_rows(file_name: str, sheet_name: str, rows: list[Row]) -> list[ErrorMsg]:
    """
    Check all row entries in a given board sheet.

    Iterates through each row of the BOM, running both value-level and logic-level checks. Value-level checks verify that individual fields are non-empty and properly formatted (e.g., description, qty, prices). Logic-level checks ensure consistency across fields (e.g., subtotal matches qty × unit price).

    Args:
        file_name (str): The name of the BOM file being checked.
        sheet_name (str): The worksheet name where the rows are located.
        rows (list[Row]): A list of row records representing BOM line items.

    Returns:
        list[ErrorMsg]: A list of structured checking errors. Each entry contains the file name, sheet name, row number, field name, and a descriptive message.
    """
    errors: list[ErrorMsg] = []

    # Enumerate rows starting at 1 to match human-readable line numbers
    for (row_index, row) in enumerate(rows, start=1):
        # Run value-level checks (format, non-empty, numeric checks)
        errors += _check_row_cell_value(file_name, sheet_name, str(row_index), row)

        # Run logic-level checks (cross-field consistency checks)
        errors += _check_row_cell_logic(file_name, sheet_name, str(row_index), row)

    return errors


def _check_row_cell_value(file_name: str, sheet_name: str, index: str, row: Row) -> list[ErrorMsg]:
    """
    Check value-level fields for a single BOM row and return structured errors.

    Performs per-field value checks (presence, formatting, numeric constraints) for the given row. This function does not raise; it converts any check exceptions into `ErrorMsg` records with full context for later rendering or programmatic handling.

    Args:
        file_name (str): Name of the BOM file being checked.
        sheet_name (str): Name of the worksheet containing the row.
        index (str): Human-readable row/line identifier (e.g., "1", "2").
        row (Row): The BOM row record to check (item, description, qty, prices, etc.).

    Returns:
        list[ErrorMsg]: Zero or more checking errors, each including file, sheet, section (row number), field name, and a descriptive message.

    Raises:
        None: All exceptions from underlying checks are caught and converted to `ErrorMsg`.
    """
    errors: list[ErrorMsg] = []

    # Helper to normalize exceptions from checks into uniform ErrorMsg records.
    def _add_error(field: str, msg: Exception) -> None:
        errors.append(ErrorMsg(file_name, sheet_name, index, field, str(msg)))

    try:
        rules.assert_item(row.item)
    except Exception as exc:
        _add_error(RowFields.ITEM, exc)

    try:
        utils.parse_to_non_empty_string(row.description)
    except Exception as exc:
        _add_error(RowFields.DESCRIPTION, exc)

    try:
        rules.assert_classification(row.classification)
    except Exception as exc:
        _add_error(RowFields.CLASSIFICATION, exc)

    try:
        utils.parse_to_non_empty_string(row.manufacturer)
    except Exception as exc:
        _add_error(RowFields.MANUFACTURER, exc)

    try:
        utils.parse_to_non_empty_string(row.mfg_part_number)
    except Exception as exc:
        _add_error(RowFields.MFG_PART_NO, exc)

    try:
        rules.assert_qty(row.qty)
    except Exception as exc:
        _add_error(RowFields.QTY, exc)

    try:
        rules.assert_price(row.unit_price)
    except Exception as exc:
        _add_error(RowFields.UNIT_PRICE, exc)

    try:
        rules.assert_price(row.sub_total)
    except Exception as exc:
        _add_error(RowFields.SUB_TOTAL, exc)

    return errors


def _check_row_cell_logic(file_name: str, sheet_name: str, index: str, row: Row) -> list[ErrorMsg]:
    """
    Check cross-field logic for a single BOM row and return structured errors.

    Runs relationship/consistency checks that span multiple fields within a row. Examples include: quantity rules conditioned on item presence, designator count matching quantity, positive unit price when quantity is positive, and subtotal consistency with qty × unit price. This function converts any check exceptions into `ErrorMsg` records and does not raise.

    Args:
        file_name (str): Name of the BOM file being checked.
        sheet_name (str): Name of the worksheet containing the row.
        index (str): Human-readable row/line identifier (e.g., "1", "2").
        row (Row): The BOM row record being checked.

    Returns:
        list[ErrorMsg]: Zero or more logic-level check errors, each including file, sheet, section (row number), field name, and a descriptive message.

    Raises:
        None: All exceptions from underlying checks are caught and converted to `ErrorMsg`.
    """
    errors: list[ErrorMsg] = []

    # Helper: normalize exceptions from logic checks into uniform ErrorMsg objects
    def _add_error(field: str, msg: Exception) -> None:
        errors.append(ErrorMsg(file_name, sheet_name, index, field, str(msg)))

    try:
        rules.assert_quantity_zero_when_item_blank(row)
    except Exception as exc:
        _add_error(RowFields.QTY, exc)

    try:
        rules.assert_quantity_positive_when_item_positive(row)
    except Exception as exc:
        _add_error(RowFields.QTY, exc)

    try:
        rules.assert_designator_count_matches_quantity(row)
    except Exception as exc:
        _add_error(RowFields.DESIGNATOR, exc)

    try:
        rules.assert_designator_required_for_positive_item_and_qty(row)
    except Exception as exc:
        _add_error(RowFields.DESIGNATOR, exc)

    try:
        rules.assert_unit_price_positive_when_quantity_positive(row)
    except Exception as exc:
        _add_error(RowFields.UNIT_PRICE, exc)

    try:
        rules.assert_subtotal_zero_when_quantity_zero(row)
    except Exception as exc:
        _add_error(RowFields.SUB_TOTAL, exc)

    try:
        rules.assert_subtotal_matches_product(row)
    except Exception as exc:
        _add_error(RowFields.SUB_TOTAL, exc)

    return errors
