"""
Raw data model for the version 3 BOM template.

This module defines structured Python dataclasses that mirror the layout of version 3 excel based Bill of Materials (BOM) files. It captures metadata, board-level information, and individual rows exactly as they appear in the source, with all fields represented as plain strings.

These models serve as the initial parsed representation created by BOM parsers before any standardization, normalization, or mapping to canonical models.

Main capabilities:
     - Encodes board-level BOM metadata (model number, revision, supplier, cost breakdown)
     - Encodes component-level BOM rows (reference, part number, quantity, price)
     - Supports multiple board BOMs within a single file

Example Usage:
    # Preferred usage via public package interface:
    # Not exposed publicly; this is an internal module.

    # Direct module usage (acceptable in unit tests or internal scripts only):
    from src.models import _v3_raw as models
    board = models.Board(header=header, rows=tuple(rows), sheet_name="Sheet1")

Dependencies:
     - Python >= 3.10
     - Standard Library: dataclasses

Notes:
     - All fields are strings to simplify parsing and tolerate missing values.
     - This model reflects raw BOM data; downstream processing should not modify it.
     - Used primarily by `v3_bom_parser` to convert Excel sheets to structured form.

License:
     - Internal Use Only
"""

__all__ = []  # Internal-only; not part of public API. Star import from this module gets nothing

from dataclasses import dataclass

# noinspection PyProtectedMember
from . import _v3_fields as fields  # Direct internal import acceptable in internal modules

_ERR_INVALID_HEADER_LABEL: str = "Unknown header label: {a}"
_ERR_INVALID_ROW_LABEL: str = "Unknown row label: {a}"


@dataclass(frozen=True)
class Row:
    """
    Represents a single row in the BOM table.

    All fields are strings and default to the empty string ("") to simplify parsing and ensure consistent handling of missing or blank values.

    Attributes:
        item (str): Line item number.
        component_type (str): Component type description.
        device_package (str): Package type of the component (e.g., 0402, SOT-23).
        description (str): Part description.
        unit (str): Unit of measure (e.g., pcs).
        classification (str): Part classification (A, B, C).
        manufacturer (str): Manufacturer name.
        mfg_part_number (str): Manufacturer's part number.
        ul_vde_number (str): UL/VDE safety certification number.
        validated_at (str): Build where the part was validated.
        qty (str): Quantity per board.
        designator (str): Component reference designator (e.g., R1, C2).
        unit_price (str): Unit price in RMB (with VAT).
        sub_total (str): Extended cost (qty × unit price), in RMB (with VAT).
    """
    item: str = ""
    component_type: str = ""
    device_package: str = ""
    description: str = ""
    unit: str = ""
    classification: str = ""
    manufacturer: str = ""
    mfg_part_number: str = ""
    ul_vde_number: str = ""
    validated_at: str = ""
    qty: str = ""
    designator: str = ""
    unit_price: str = ""
    sub_total: str = ""

    def __str__(self) -> str:
        """
        Return a human-readable multiline string representation of the row. Shows all fields as key=value, one per line.
        """
        lines = []
        for excel_label, model_field in fields.ROW_TO_ATTR_MAP.items():
            value = getattr(self, model_field, "")
            lines.append(f"{excel_label}={value}")
        return "\n".join(lines)

    @classmethod
    def get_labels(cls) -> tuple[str, ...]:
        """
        Returns the Excel labels recognized for Row objects.

        Returns:
            tuple[str, ...]: Immutable sequence of header labels.
        """
        return tuple(fields.ROW_TO_ATTR_MAP.keys())

    @classmethod
    def get_v3_template_labels(cls) -> tuple[str, ...]:
        """
        Return the row Excel labels used to identify an Excel sheet as a Version 3 BOM template.

        Returns:
            tuple[str, ...]: Immutable sequence of row identifier labels.
        """
        return tuple(fields.REQ_V3_ROW_IDENTIFIERS)

    @staticmethod
    def get_attr_name_by_label(excel_label: str) -> str:
        """
        Retrieve the attribute name using its Excel label.

        Args:
            excel_label (str): Excel label.

        Returns:
            str: The corresponding attribute name.

        Raises:
            KeyError: If the label is not recognized for Row.
        """
        attr_name = fields.ROW_TO_ATTR_MAP.get(excel_label)
        if attr_name is None:
            raise KeyError(_ERR_INVALID_ROW_LABEL.format(a=excel_label))
        return attr_name


@dataclass(frozen=True)
class Header:
    """
    Represents the header of a single board BOM.

    All fields are plain strings with default values of "" to simplify normalization and tolerate missing values.

    Attributes:
        model_no (str): Product model number.
        board_name (str): Board name (e.g., MAIN-PCB-A).
        manufacturer (str): Board supplier or manufacturer.
        build_stage (str): Stage of the build (e.g., EB0, MP).
        date (str): BOM creation or release date.
        material_cost (str): Raw material cost.
        overhead_cost (str): Overhead, logistics, or handling cost.
        total_cost (str): Total combined cost.
    """
    model_no: str = ""
    board_name: str = ""
    manufacturer: str = ""
    build_stage: str = ""
    date: str = ""
    material_cost: str = ""
    overhead_cost: str = ""
    total_cost: str = ""

    def __str__(self) -> str:
        """
        Return a human-readable multiline string representation of the header. Shows all fields as key=value, one per line.
        """
        lines = []
        for excel_label, model_field in fields.HEADER_TO_ATTR_MAP.items():
            value = getattr(self, model_field, "")
            lines.append(f"{excel_label}={value}")
        return "\n".join(lines)

    @classmethod
    def get_labels(cls) -> tuple[str, ...]:
        """
        Returns the Excel labels recognized for Header objects.

        Returns:
            tuple[str, ...]: Immutable sequence of header labels.
        """
        return tuple(fields.HEADER_TO_ATTR_MAP.keys())

    @staticmethod
    def get_attr_name_by_label(excel_label: str) -> str:
        """
        Retrieve the attribute name using its Excel label.

        Args:
            excel_label (str): Excel label.

        Returns:
            str: The corresponding attribute name.

        Raises:
            KeyError: If the label is not recognized for Header.
        """
        attr_name = fields.HEADER_TO_ATTR_MAP.get(excel_label)
        if attr_name is None:
            raise KeyError(_ERR_INVALID_HEADER_LABEL.format(a=excel_label))
        return attr_name


@dataclass(frozen=True)
class Board:
    """
    Represents a BOM for a single board, including header and all component rows.

    Attributes:
        header (Header): Board-level metadata including model, stage, and costs.
        rows (tuple[Row, ...]): Component rows associated with this board.
        sheet_name (str): Name of the Excel sheet from which this board data is read.
    """
    header: Header  # no default, assigned when created
    rows: tuple[Row, ...]  # Any length, No default, assigned when created
    sheet_name: str = ""


@dataclass(frozen=True)
class Bom:
    """
    Top-level model representing the structure of a Version 3 BOM file.

    Attributes:
        boards (tuple[Board, ...]): Board BOMs extracted from the file.
        file_name (str): Original filename of the BOM file.
        is_cost_bom (bool): True if the file represents a costed BOM; defaults to True and may be downgraded by the parser.
    """
    boards: tuple[Board, ...]  # Any length. No default, assigned when created
    file_name: str = ""
    is_cost_bom: bool = True # Fail-safe default; parser sets False only when confidently detected
