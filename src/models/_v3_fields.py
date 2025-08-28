"""
Internal constants and field mappings for version 3 BOM model support.

This module defines string constants and mapping dictionaries used to translate raw Excel headers into structured model attributes (Header, Row). It enables automated parsing workflows within the Version 3 BOM parser.

Main capabilities:
    - Definitions for board-level and component-level Excel fields
    - Mappings from Excel labels to internal model attribute names
    - Identifiers used to detect Version 3 BOM templates

Example Usage:
    # Preferred usage via public package interface:
    # Not exposed publicly; this is an internal module.

    # Direct module usage (acceptable in unit tests or internal scripts only):
    import src.models._v3_fields as fields
    fields = v3.BoardHeaderFields.BOM_DATE

Dependencies:
    - Python >= 3.10
    - Standard Library only

Notes:
    - This module is internal to `src.models`. It is not part of the public API.
    - External code should import public interfaces via `src.models.interface`.
    - Use in unit tests is acceptable to validate parsing logic and constants.

License:
    - Internal Use Only
"""

__all__ = []  # Internal-only; not part of public API. Star import from this module gets nothing


class HeaderFields:
    """
    Field constants for board header in Version 3 BOM sheets.

    Each class attribute corresponds to a known header label in the Excel sheet, used to extract metadata like model number, revision, supplier, and costs.

    Class Methods:
        names(): Returns a list of all defined header field strings.
    """
    MODEL_NUMBER = "Model No:"  # Product model identifier
    BUILD_STAGE = "Rev:"  # Build stage or revision (e.g., EB0, MP)
    BOARD_NAME = "Description:"  # Board or BOM description
    BOARD_SUPPLIER = "Manufacturer:"  # Board supplier or manufacturer name
    BOM_DATE = "Date:"  # BOM creation or approval date
    MATERIAL_COST = "Material"  # Material cost subtotal
    OVERHEAD_COST = "OHP"  # Overhead or handling cost
    TOTAL_COST = "Total"  # Total cost (material + overhead)

    @classmethod
    def names(cls) -> list[str]:
        """
        Returns all board header field strings defined in the class.

        Returns:
            list[str]: List of board metadata field labels used in Excel.
        """
        return [
            value for name, value in vars(cls).items()
            if not name.startswith("__") and isinstance(value, str)
        ]


"""
Mapping of board-level Excel header fields to Header dataclass attributes.

This dictionary translates raw Excel labels from the Version 3 BOM template (as defined in `HeaderFields`) into corresponding attribute names of the internal `Header` dataclass. It enables consistent field matching during BOM parsing and model population.

Key:
    str: Excel label for a board-level metadata field (e.g., "Model No:")
Value:
    str: Attribute name in the `Header` dataclass (e.g., "model_no")
"""
HEADER_TO_ATTR_MAP = {
    HeaderFields.MODEL_NUMBER: "model_no",
    HeaderFields.BUILD_STAGE: "build_stage",
    HeaderFields.BOARD_NAME: "board_name",
    HeaderFields.BOARD_SUPPLIER: "manufacturer",
    HeaderFields.BOM_DATE: "date",
    HeaderFields.MATERIAL_COST: "material_cost",
    HeaderFields.OVERHEAD_COST: "overhead_cost",
    HeaderFields.TOTAL_COST: "total_cost"
}


class RowFields:
    """
    Field constants for component rows in Version 3 BOM sheets.

    Each class attribute represents a standardized header in the board rows, such as part number, quantity, or pricing information.

    Class Methods:
        names(): Returns a list of all defined table field strings.
    """

    ITEM = "Item"  # Line number in the BOM
    COMPONENT = "Component"  # Component name or ID
    PACKAGE = "Device Package"  # Physical package type (e.g., QFN-8)
    DESCRIPTION = "Description"  # Part description
    UNITS = "Unit"  # Unit of measure (e.g., pcs)
    CLASSIFICATION = "Classification"  # Component class (e.g., A, B, C)
    MANUFACTURER = "Manufacturer"  # Part manufacturer
    MFG_PART_NO = "Manufacturer P/N"  # Manufacturer part number
    UL_VDE_NUMBER = "UL/VDE Number"  # Certification reference (if applicable)
    VALIDATED_AT = "Validated at"  # Validation build stage
    QTY = "Qty"  # Quantity used
    DESIGNATOR = "Designator"  # Reference designators (e.g., R1, C4)
    UNIT_PRICE = "U/P (RMB W/ VAT)"  # Unit price (incl. VAT) in RMB
    SUB_TOTAL = "Sub-Total (RMB W/ VAT)"  # Line subtotal cost

    @classmethod
    def names(cls) -> list[str]:
        """
        Returns all component table field strings defined in the class.

        Returns:
            list[str]: List of component table column labels used in Excel.
        """
        return [
            value for name, value in vars(cls).items()
            if not name.startswith("__") and isinstance(value, str)
        ]


"""
Mapping of component table column labels to Row dataclass attributes.

This dictionary translates raw Excel column headers from the Version 3 BOM template (as defined in `RowFields`) into corresponding attribute names of the internal `Row` dataclass. It enables automated parsing of component-level 
data into structured models during BOM ingestion.

Key:
    str: Excel label for a component table column (e.g., "Qty")
Value:
    str: Attribute name in the `Row` dataclass (e.g., "qty")
"""
ROW_TO_ATTR_MAP = {
    RowFields.ITEM: "item",
    RowFields.COMPONENT: "component_type",
    RowFields.PACKAGE: "device_package",
    RowFields.DESCRIPTION: "description",
    RowFields.UNITS: "unit",
    RowFields.CLASSIFICATION: "classification",
    RowFields.MANUFACTURER: "manufacturer",
    RowFields.MFG_PART_NO: "mfg_part_number",
    RowFields.UL_VDE_NUMBER: "ul_vde_number",
    RowFields.VALIDATED_AT: "validated_at",
    RowFields.QTY: "qty",
    RowFields.DESIGNATOR: "designator",
    RowFields.UNIT_PRICE: "unit_price",
    RowFields.SUB_TOTAL: "sub_total"
}

"""
Required column labels used to detect Version 3 BOM templates.

This list defines the minimum set of Excel column headers that must be present in a sheet for it to be recognized as conforming to the Version 3 BOM format. These fields are typically found in the component table section of the sheet.

Returns:
    list[str]: List of field labels used to validate a Version 3 BOM sheet.
"""
REQ_V3_BOM_IDENTIFIERS: list[str] = [
    RowFields.CLASSIFICATION,
    RowFields.DESIGNATOR,
    RowFields.MANUFACTURER,
    RowFields.MFG_PART_NO
]

"""
Required column labels used to identify Version 3 BOM board rows.

This list contains key Excel column headers that must be present in a sheet's component table for it to be recognized as following the Version 3 BOM board template. These fields help ensure structural compatibility before parsing.

Returns:
    list[str]: Column labels expected in a valid Version 3 board-level BOM table.
"""
REQ_V3_ROW_IDENTIFIERS: list[str] = [
    RowFields.CLASSIFICATION,
    RowFields.DESIGNATOR,
    RowFields.MANUFACTURER,
    RowFields.MFG_PART_NO
]
