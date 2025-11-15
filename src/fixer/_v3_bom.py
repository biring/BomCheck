"""
Fixer for Version 3 Bill of Materials (BOM) Excel sheets.

This module applies both manual and automatic field corrections across the BOM hierarchy — boards, headers, and rows — using rule functions from `src.correction.interfaces`. It rebuilds the BOM with corrected dataclass instances and aggregates contextual change logs (file → sheet → section) for audit traceability.

Example Usage:
    # Preferred usage via package interface:
    from src.fixer import interfaces as fix
    fixed_bom, log = fix.bom(raw_bom)

    # Direct internal usage (unit tests or internal scripts only):
    from src.fixer import _v3_bom as v3
    fixed_bom, log = v3.fix_v3_bom(raw_bom)

Dependencies:
    - Python >= 3.10
    - Standard Library: dataclasses
    - Internal Packages: src.models, src.correction, src.fixer._types

Notes:
    - Designed exclusively for structured Version 3 BOMs with valid model hierarchy.
    - ChangeLog accumulates human-readable audit messages, grouped by contextual scope.
    - Manual fixers rely on user-provided corrections; auto fixers apply deterministic rules.
    - External callers should invoke through `src.fixer.interfaces` to preserve API boundaries.

License:
    - Internal Use Only
"""
__all__ = []  # Internal-only; not part of public API. Star import from this module gets nothing.

from dataclasses import replace

from src.models.interfaces import Row, Header, Board, Bom, RowFields, HeaderFields
from src.correction import interfaces as correct

from src.common import ChangeLog


def fix_v3_bom(bom: Bom) -> tuple[Bom, tuple[str, ...]]:
    """
    Apply manual and automatic field corrections across all boards, headers, and rows in a Version 3 BOM.

    Traverses every `Board` in the provided `Bom`, invokes field-level fixers for each `Row` and `Header`, and rebuilds corrected dataclass instances. Collects a contextual `ChangeLog` keyed by file, sheet, and section for full audit traceability.

    Args:
        bom (Bom): Input BOM object containing nested boards, headers, and rows to fix.

    Returns:
        tuple[Bom, tuple[str, ...]]: A tuple containing the corrected BOM and a tuple of formatted log entries (one per detected or applied change).

    Raises:
        ValueError: If reconstruction of any row, header, or board fails due to invalid mappings.
    """
    # Initialize contextual change log scoped by file → sheet → section
    change_log = ChangeLog()
    change_log.set_module_name("fixer")
    change_log.set_file_name(bom.file_name)

    fixed_boards: list[Board] = []

    # --- For each board in the BOM ---
    for board in bom.boards:
        # Set current sheet context for accurate log grouping
        change_log.set_sheet_name(board.sheet_name)

        # --- Fix rows ---
        fixed_rows: list[Row] = []
        for idx, raw_row in enumerate(board.rows, start=1):
            change_log.set_section_name(Row.__name__ + ": " + str(idx))

            # Apply manual fixers first (user-dependent), then automatic fixers
            fixed_row_manual = _fix_row_manual(change_log, raw_row)
            fixed_row_auto = _fix_row_auto(change_log, fixed_row_manual)
            fixed_rows.append(fixed_row_auto)

        # --- Fix header ---
        change_log.set_section_name(Header.__name__)

        # Apply manual header fixes before auto-calculated fields like cost
        fixed_header_manual = _fix_header_manual(change_log, board.header)
        fixed_board_manual: Board = Board(header=fixed_header_manual, rows=tuple(fixed_rows),
                                          sheet_name=board.sheet_name)
        fixed_header_auto = _fix_header_auto(change_log, fixed_board_manual)
        fixed_board_auto: Board = Board(header=fixed_header_auto, rows=tuple(fixed_rows), sheet_name=board.sheet_name)
        fixed_boards.append(fixed_board_auto)

    # Collect all cleaned boards and reconstruct final BOM
    fixed_bom: Bom = Bom(boards=tuple(fixed_boards), file_name=bom.file_name)

    # Extract full log snapshot for external reporting
    frozen_change_log = change_log.render()

    return fixed_bom, frozen_change_log


def _fix_header_manual(change_log: ChangeLog, header: Header) -> Header:
    """
    Apply manual header corrections in a defined order and append any resulting messages to the change-log.

    Args:
        change_log (ChangeLog): Context-aware collector for change messages.
        header (Header): Header instance to correct.

    Returns:
        Header: A new header with manual fixes applied.

    Raises:
        ValueError: If corrected values cannot be mapped back to header fields.
    """
    # Define ordered header cleaning sequence (function, label)
    cases = [
        (correct.model_number, HeaderFields.MODEL_NUMBER),
        (correct.board_name, HeaderFields.BOARD_NAME),
        (correct.board_supplier, HeaderFields.BOARD_SUPPLIER),
        (correct.build_stage, HeaderFields.BUILD_STAGE),
        (correct.bom_date, HeaderFields.BOM_DATE),
        (correct.overhead_cost, HeaderFields.OVERHEAD_COST),
    ]

    attr_name = None

    # Apply fix for each field and collect logs
    for fn, label in cases:
        try:
            attr_name = Header.get_attr_name_by_label(label)
            original_value = getattr(header, attr_name)
            result_value, result_log = fn(header)

            if result_value != original_value:
                header = replace(header, **{attr_name: result_value})
            change_log.add_entry(result_log)
        except Exception as e:
            raise ValueError(
                f"{type(header).__name__} correction failed on '{attr_name}'. Latest partial row:\n{header!r}"
            ) from e
    return header


def _fix_header_auto(change_log: ChangeLog, board: Board) -> Header:
    """
    Apply automatic header corrections (e.g., computed costs) based on board context and append messages to the change-log.

    Args:
        change_log (ChangeLog): Context-aware collector for change messages.
        board (Board): Board providing header and row context for computed fields.

    Returns:
        Header: A new header with automatic fixes applied.

    Raises:
        ValueError: If corrected values cannot be mapped back to header fields.
    """
    header = board.header
    attr_name = None

    # 1. Fix material cost math
    try:
        label = HeaderFields.MATERIAL_COST
        attr_name = Header.get_attr_name_by_label(label)
        original_value = getattr(header, attr_name)
        result_value, result_log = correct.material_cost(board)

        if result_value != original_value:
            header = replace(header, **{attr_name: result_value})
        change_log.add_entry(result_log)
    except Exception as e:
        raise ValueError(
            f"{type(header).__name__} correction failed on '{attr_name}'. Latest partial row:\n{header!r}"
        ) from e

    # 2. Fix total cost math
    try:
        label = HeaderFields.TOTAL_COST
        attr_name = Header.get_attr_name_by_label(label)
        original_value = getattr(header, attr_name)
        result_value, result_log = correct.total_cost(header)

        if result_value != original_value:
            header = replace(header, **{attr_name: result_value})
        change_log.add_entry(result_log)
    except Exception as e:
        raise ValueError(
            f"{type(header).__name__} correction failed on '{attr_name}'. Latest partial row:\n{header!r}"
        ) from e
    return header


def _fix_row_manual(change_log: ChangeLog, row: Row) -> Row:
    """
    Apply manual row corrections in a defined order and append messages for any detected or applied changes.

    Args:
        change_log (ChangeLog): Context-aware collector for change messages.
        row (Row): Row instance to correct.

    Returns:
        Row: A new row with manual fixes applied.

    Raises:
        ValueError: If corrected values cannot be mapped back to row fields.
    """
    # Define ordered header cleaning sequence (function, label)
    cases = [
        (correct.item, RowFields.ITEM),
        (correct.component_type, RowFields.COMPONENT),
        (correct.device_package, RowFields.PACKAGE),
        (correct.description, RowFields.DESCRIPTION),
        (correct.unit, RowFields.UNITS),
        (correct.classification, RowFields.CLASSIFICATION),
        (correct.manufacturer, RowFields.MANUFACTURER),
        (correct.mfg_part_number, RowFields.MFG_PART_NO),
        (correct.ul_vde_number, RowFields.UL_VDE_NUMBER),
        (correct.validated_at, RowFields.VALIDATED_AT),
        (correct.qty, RowFields.QTY),
        (correct.designator, RowFields.DESIGNATOR),
        (correct.unit_price, RowFields.UNIT_PRICE),
    ]

    attr_name = None

    # Apply fix for each field and collect logs
    for fn, label in cases:
        try:
            attr_name = Row.get_attr_name_by_label(label)
            original_value = getattr(row, attr_name)
            result_value, result_log = fn(row)

            if result_value != original_value:
                row = replace(row, **{attr_name: result_value})
            change_log.add_entry(result_log)
        except Exception as e:
            raise ValueError(
                f"{type(row).__name__} correction failed on '{attr_name}'. Latest partial row:\n{row!r}"
            ) from e
    return row


def _fix_row_auto(change_log: ChangeLog, row: Row) -> Row:
    """
    Apply automatic row corrections (e.g., lookups, expansions, and computed totals) and append messages to the change-log.

    Args:
        change_log (ChangeLog): Context-aware collector for change messages.
        row (Row): Row instance to correct.

    Returns:
        Row: A new row with automatic fixes applied.

    Raises:
        ValueError: If corrected values cannot be mapped back to row fields.
    """
    # Define ordered header cleaning sequence (function, value, attribute)
    cases = [
        (correct.component_type_lookup, RowFields.COMPONENT),
        (correct.expand_designators, RowFields.DESIGNATOR),
        (correct.sub_total, RowFields.SUB_TOTAL),
    ]

    attr_name = None

    # Apply fix for each field and collect logs
    for fn, label in cases:
        try:
            attr_name = Row.get_attr_name_by_label(label)
            original_value = getattr(row, attr_name)
            result_value, result_log = fn(row)

            if result_value != original_value:
                row = replace(row, **{attr_name: result_value})
            change_log.add_entry(result_log)
        except Exception as e:
            raise ValueError(
                f"{type(row).__name__} correction failed on '{attr_name}'. Latest partial row:\n{row!r}"
            ) from e
    return row
