"""
BOM-level coercion coordinator for Version 3 BOM objects.

This module orchestrates coercion across the full BOM hierarchy (boards, headers, and rows).  It delegates value-level normalization to `_header` and `_row` modules and consolidates their transformation logs into a single contextual report.

Example Usage:
    # Preferred usage via package interface:
    from src.coerce import interfaces as coerce
    clean_bom, log = coerce.bom(raw_bom)

    # Direct internal usage (unit tests or internal scripts only):
    from src.coerce import _bom as cb
    result_bom, result_log = cb.coerce_bom(raw_bom)
    print(result_log)

Dependencies:
    - Python >= 3.10
    - Standard Library: dataclasses
    - Internal: src.models.interfaces, src.coerce._common, src.coerce._header, src.coerce._row

Notes:
    - This module centralizes BOM-wide coercion while maintaining separation between field-level and cross-field logic checks.
    - `CoerceLog` accumulates contextual entries (file, sheet, section) to support traceable, human-readable audit logs.
    - Intended for internal use; external callers should use the public façade via `src.coerce.interfaces`.

License:
    - Internal Use Only
"""
__all__ = []  # Internal-only; not part of public API. Star import from this module gets nothing.

from src.models import interfaces as mdl
from src.coerce import _common as cc
from src.coerce import _header as hc
from src.coerce import _row as rc


def coerce_bom(bom: mdl.Bom) -> tuple[mdl.Bom, tuple[str, ...]]:
    """
    Apply BOM-wide coercion to all boards, headers, and rows.

    Traverses the entire BOM hierarchy, applying field-level coercion via
    `_header` and `_row` modules. Accumulates a context-aware change log
    for every modified value.

    Args:
        bom (mdl.Bom): Input BOM object containing boards, headers, and rows.

    Returns:
        tuple[mdl.Bom, tuple[str, ...]]:
            - The coerced BOM object with normalized field values.
            - A tuple of formatted log strings describing every change.

    Raises:
        ValueError: If a header or row mapping fails during object reconstruction.
    """

    # Initialize contextual log (file, sheet, section tracking)
    coerce_log = cc.CoerceLog()
    coerce_log.set_file_name(bom.file_name)

    coerced_boards: list[mdl.Board] = []

    # Iterate through each board in the BOM
    for board in bom.boards:
        # Set sheet context for current board
        coerce_log.set_sheet_name(board.sheet_name)

        # Coerce all rows within current board
        coerced_rows: list[mdl.Row] = []
        for idx, raw_row in enumerate(board.rows, start=1):
            coerce_log.set_section_name(mdl.Row.__name__ + ": " + str(idx))
            coerced_row = _coerce_row(coerce_log, raw_row)
            coerced_rows.append(coerced_row)

        # Coerce header fields for the current board
        coerce_log.set_section_name(mdl.Header.__name__)
        coerced_header = _coerce_header(coerce_log, board.header)

        ## Reconstruct the Board object with coerced fields
        board: mdl.Board = mdl.Board(header=coerced_header, rows=tuple(coerced_rows), sheet_name=board.sheet_name)
        coerced_boards.append(board)

    # Collect all coerced boards and reconstruct final BOM
    coerced_bom: mdl.Bom = mdl.Bom(boards=tuple(coerced_boards), file_name=bom.file_name)

    # Extract full log snapshot for external reporting
    log = cc.CoerceLog.snapshot(coerce_log)

    return coerced_bom, log


def _coerce_header(coerce_log: cc.CoerceLog, header: mdl.Header) -> mdl.Header:
    """
    Coerce and normalize all header fields.

    Invokes field-specific coercers for each header attribute and appends
    all resulting change log messages to the shared coercion log.

    Args:
        coerce_log (cc.CoerceLog): Shared log collector for contextual tracking.
        header (mdl.Header): Input header object with raw field values.

    Returns:
        mdl.Header: New header instance with normalized field values.

    Raises:
        ValueError: If field mapping fails during header reconstruction.
    """
    field_map = {}

    # Define ordered header coercion sequence (function, value, attribute)
    cases = [
        (hc.model_number, header.model_no, mdl.HeaderFields.MODEL_NUMBER),
        (hc.board_name, header.board_name, mdl.HeaderFields.BOARD_NAME),
        (hc.board_supplier, header.manufacturer, mdl.HeaderFields.BOARD_SUPPLIER),
        (hc.build_stage, header.build_stage, mdl.HeaderFields.BUILD_STAGE),
        (hc.bom_date, header.date, mdl.HeaderFields.BOM_DATE),
        (hc.material_cost, header.material_cost, mdl.HeaderFields.MATERIAL_COST),
        (hc.overhead_cost, header.overhead_cost, mdl.HeaderFields.OVERHEAD_COST),
        (hc.total_cost, header.total_cost, mdl.HeaderFields.TOTAL_COST),
    ]

    # Apply coercion for each field and collect logs
    for fn, val, attr in cases:
        result = fn(val)
        attr_name = mdl.Header.get_attr_name_by_label(attr)
        attr_value = result.value_out
        field_map[attr_name] = attr_value

        # Record each formatted message in the shared coercion log
        result_logs = result.format_to_change_log()
        for result_log in result_logs:
            coerce_log.add(result_log)

    # Rebuild header object with coerced values
    try:
        return mdl.Header(**field_map)
    except Exception as e:
        # Raise detailed error if any field mapping fails
        raise ValueError(
            f"Header coercion failed: invalid field mapping. Keys processed: {field_map.keys()}."
        ) from e


def _coerce_row(coerce_log: cc.CoerceLog, row: mdl.Row) -> mdl.Row:
    """
    Coerce and normalize all row-level fields.

    Invokes field-specific coercers for each BOM row attribute and logs
    any transformations that result in a changed value.

    Args:
        coerce_log (cc.CoerceLog): Shared log collector for contextual tracking.
        row (mdl.Row): Input row object with raw field values.

    Returns:
        mdl.Row: New row instance with normalized field values.

    Raises:
        ValueError: If field mapping fails during row reconstruction.
    """

    field_map = {}

    # Define ordered row coercion sequence (function, value, attribute)
    cases = [
        (rc.item, row.item, mdl.RowFields.ITEM),
        (rc.component_type, row.component_type, mdl.RowFields.COMPONENT),
        (rc.device_package, row.device_package, mdl.RowFields.PACKAGE),
        (rc.description, row.description, mdl.RowFields.DESCRIPTION),
        (rc.units, row.unit, mdl.RowFields.UNITS),
        (rc.classification, row.classification, mdl.RowFields.CLASSIFICATION),
        (rc.manufacturer, row.manufacturer, mdl.RowFields.MANUFACTURER),
        (rc.mfg_part_number, row.mfg_part_number, mdl.RowFields.MFG_PART_NO),
        (rc.ul_vde_number, row.ul_vde_number, mdl.RowFields.UL_VDE_NUMBER),
        (rc.validated_at, row.validated_at, mdl.RowFields.VALIDATED_AT),
        (rc.quantity, row.qty, mdl.RowFields.QTY),
        (rc.designator, row.designator, mdl.RowFields.DESIGNATOR),
        (rc.unit_price, row.unit_price, mdl.RowFields.UNIT_PRICE),
        (rc.sub_total, row.sub_total, mdl.RowFields.SUB_TOTAL),
    ]

    # Apply coercion for each field and collect logs
    for fn, val, attr in cases:
        result = fn(val)
        attr_name = mdl.Row.get_attr_name_by_label(attr)
        attr_value = result.value_out
        field_map[attr_name] = attr_value

        # Append each formatted message to the shared coercion log
        result_logs = result.format_to_change_log()
        for result_log in result_logs:
            coerce_log.add(result_log)

    # Rebuild the row object with coerced values
    try:
        return mdl.Row(**field_map)
    except Exception as e:
        raise ValueError(
            # Raise detailed error if mapping fails
            f"Row coercion failed: invalid field mapping. Keys processed: {field_map.keys()}."
        ) from e
