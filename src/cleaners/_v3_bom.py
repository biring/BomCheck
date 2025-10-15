"""
Cleaner for Version 3 Bill of Materials (BOM) Excel sheets.

This module orchestrates field-level coercion across the BOM hierarchy (boards, headers, and rows). It rebuilds the BOM with normalized values and accumulates a contextual change log (file → sheet → section) for traceable audit output.

Example Usage:
    # Preferred usage via package interface:
    from src.cleaners import interfaces as clean
    clean_bom, log = clean.bom(raw_bom)

    # Direct internal usage (unit tests or internal scripts only):
    from src.cleaners import _v3_bom as _v3
    result_bom, result_log = _v3.clean_v3_bom(raw_bom)

Dependencies:
    - Python >= 3.10
    - Standard Library: dataclasses
    - Internal Packages: src.models, src.coerce, src.cleaners._types

Notes:
    - Designed for structured Version 3 BOMs only; assumes valid model hierarchy.
    - `ChangeLog` records all coercion steps with contextual grouping.
    - Intended for internal use; external callers should use `src.cleaners.interfaces`.

License:
    - Internal Use Only
"""
__all__ = []  # Internal-only; not part of public API. Star import from this module gets nothing.

from src.models import interfaces as mdl
from src.coerce import interfaces as coerce

from . import _types as types


def clean_v3_bom(bom: mdl.Bom) -> tuple[mdl.Bom, tuple[str, ...]]:
    """
    Clean a Version 3 BOM by coercing all board headers and rows and collecting a change log.

    Traverses each board in the BOM, normalizes row fields and header fields using the `src.coerce.interfaces` functions, and rebuilds the BOM with coerced values. A contextual change log (file → sheet → section) is returned for auditability.

    Args:
        bom (mdl.Bom): Input BOM containing boards, headers, and rows to be coerced.

    Returns:
        tuple[mdl.Bom, tuple[str, ...]]: A 2-tuple of (coerced_bom, change_log_messages).

    Raises:
        ValueError: If reconstruction of any board, header, or row fails due to an invalid field mapping.
    """
    # Initialize contextual log (file, sheet, section tracking)
    change_log = types.ChangeLog()
    change_log.set_file_name(bom.file_name)

    clean_boards: list[mdl.Board] = []

    # Iterate through each board in the BOM
    for board in bom.boards:
        # Set sheet context for current board
        change_log.set_sheet_name(board.sheet_name)

        # Coerce all rows within current board
        clean_rows: list[mdl.Row] = []
        for idx, raw_row in enumerate(board.rows, start=1):
            change_log.set_section_name(mdl.Row.__name__ + ": " + str(idx))
            clean_row = _clean_row(change_log, raw_row)
            clean_rows.append(clean_row)

        # Coerce header fields for the current board
        change_log.set_section_name(mdl.Header.__name__)
        clean_header = _clean_header(change_log, board.header)

        ## Reconstruct the Board object with coerced fields
        board: mdl.Board = mdl.Board(header=clean_header, rows=tuple(clean_rows), sheet_name=board.sheet_name)
        clean_boards.append(board)

    # Collect all cleaned boards and reconstruct final BOM
    clean_bom: mdl.Bom = mdl.Bom(boards=tuple(clean_boards), file_name=bom.file_name)

    # Extract full log snapshot for external reporting
    frozen_change_log = change_log.to_frozen_list()

    return clean_bom, frozen_change_log


def _clean_header(change_log: types.ChangeLog, header: mdl.Header) -> mdl.Header:
    """
    Coerce and normalize all row fields and append emitted messages to the shared log.

    Applies field-specific coercers in a defined order, maps label-based fields to dataclass attributes, and rebuilds a normalized `mdl.Row`.

    Args:
        change_log (types.ChangeLog): Shared context-aware change log collector.
        row (mdl.Row): Raw row instance.

    Returns:
        mdl.Row: New row with normalized values.

    Raises:
        ValueError: If any coerced values cannot be mapped back to `mdl.Row` fields during reconstruction.
    """
    field_map = {}

    # Define ordered header cleaning sequence (function, value, attribute)
    cases = [
        (coerce.model_number, header.model_no, mdl.HeaderFields.MODEL_NUMBER),
        (coerce.board_name, header.board_name, mdl.HeaderFields.BOARD_NAME),
        (coerce.board_supplier, header.manufacturer, mdl.HeaderFields.BOARD_SUPPLIER),
        (coerce.build_stage, header.build_stage, mdl.HeaderFields.BUILD_STAGE),
        (coerce.bom_date, header.date, mdl.HeaderFields.BOM_DATE),
        (coerce.material_cost, header.material_cost, mdl.HeaderFields.MATERIAL_COST),
        (coerce.overhead_cost, header.overhead_cost, mdl.HeaderFields.OVERHEAD_COST),
        (coerce.total_cost, header.total_cost, mdl.HeaderFields.TOTAL_COST),
    ]

    # Apply coercion for each field and collect logs
    for fn, val, attr in cases:
        result_value, result_logs = fn(val)
        attr_name = mdl.Header.get_attr_name_by_label(attr)
        attr_value = result_value
        field_map[attr_name] = attr_value

        # Record each formatted message in the shared coercion log
        for result_log in result_logs:
            change_log.add_entry(result_log)

    # Rebuild header object with coerced values
    try:
        return mdl.Header(**field_map)
    except Exception as e:
        # Raise detailed error if any field mapping fails
        raise ValueError(
            f"Header coercion failed: invalid field mapping. Keys processed: {field_map.keys()}."
        ) from e


def _clean_row(change_log: types.ChangeLog, row: mdl.Row) -> mdl.Row:
    """
    Clean (coerce and normalize) all row-level fields.

    Invokes field-specific coercers for each BOM row attribute and logs
    any transformations that result_value in a changed value.

    Args:
        change_log (help.CleanLog): Shared log collector for contextual tracking.
        row (mdl.Row): Input row object with raw field values.

    Returns:
        mdl.Row: New row instance with normalized field values.

    Raises:
        ValueError: If field mapping fails during row reconstruction.
    """

    field_map = {}

    # Define ordered row coercion sequence (function, value, attribute)
    cases = [
        (coerce.item, row.item, mdl.RowFields.ITEM),
        (coerce.component_type, row.component_type, mdl.RowFields.COMPONENT),
        (coerce.device_package, row.device_package, mdl.RowFields.PACKAGE),
        (coerce.description, row.description, mdl.RowFields.DESCRIPTION),
        (coerce.units, row.unit, mdl.RowFields.UNITS),
        (coerce.classification, row.classification, mdl.RowFields.CLASSIFICATION),
        (coerce.manufacturer, row.manufacturer, mdl.RowFields.MANUFACTURER),
        (coerce.mfg_part_number, row.mfg_part_number, mdl.RowFields.MFG_PART_NO),
        (coerce.ul_vde_number, row.ul_vde_number, mdl.RowFields.UL_VDE_NUMBER),
        (coerce.validated_at, row.validated_at, mdl.RowFields.VALIDATED_AT),
        (coerce.quantity, row.qty, mdl.RowFields.QTY),
        (coerce.designator, row.designator, mdl.RowFields.DESIGNATOR),
        (coerce.unit_price, row.unit_price, mdl.RowFields.UNIT_PRICE),
        (coerce.sub_total, row.sub_total, mdl.RowFields.SUB_TOTAL),
    ]

    # Apply coercion for each field and collect logs
    for fn, val, attr in cases:
        result_value, result_logs = fn(val)
        attr_name = mdl.Row.get_attr_name_by_label(attr)
        attr_value = result_value
        field_map[attr_name] = attr_value

        # Append each formatted message to the shared coercion log
        for result_log in result_logs:
            change_log.add_entry(result_log)

    # Rebuild the row object with coerced values
    try:
        return mdl.Row(**field_map)
    except Exception as e:
        raise ValueError(
            # Raise detailed error if mapping fails
            f"Row coercion failed: invalid field mapping. Keys processed: {field_map.keys()}."
        ) from e
