"""
Public interface façade for the `coerce` package.

This module re-exports curated BOM field coercion functions from internal modules to provide a stable API boundary. It defines the public entry points for BOM normalization workflows while keeping underlying logic encapsulated.

Example Usage:
    # Preferred usage via package interface:
    from src.coerce import interfaces as coerce
    value, log = coerce.board_name("  Power   PCBA  ")
    print(value)  # "Power PCBA"

    # Direct internal access (for tests or internal scripts only):
    from src.coerce import interfaces as coerce
    value, log = coerce.board_name("  Power   PCBA  ")
    print(value)  # "Power PCBA"

Dependencies:
    - Python >= 3.10
    - Standard Library: None
    - External Packages: None

Notes:
    - Provides a stable import target; internal module layout may evolve without breaking callers.
    - Only approved field-level coercers are exposed via `__all__`.
    - Intended for use by BOM parsers, validators, and approval/reporting flows.
    - Internal modules (`_helper`, `_rules`, `_regex`) remain non-public and are not imported here.

License:
    - Internal Use Only
"""

# Re-export selected API from internal modules to expose as public API

# noinspection PyProtectedMember
from ._header import (
    model_number,
    board_name,
    board_supplier,
    build_stage,
    bom_date,
    material_cost,
    overhead_cost,
    total_cost,
)

# noinspection PyProtectedMember
from ._row import (
    item,
    component_type,
    device_package,
    description,
    units,
    classification,
    manufacturer,
    mfg_part_number,
    ul_vde_number,
    validated_at,
    quantity,
    designator,
    unit_price,
    sub_total,
)

__all__ = [
    # header
    "model_number",
    "board_name",
    "board_supplier",
    "build_stage",
    "bom_date",
    "material_cost",
    "overhead_cost",
    "total_cost",

    # row
    "item",
    "component_type",
    "device_package",
    "description",
    "units",
    "classification",
    "manufacturer",
    "mfg_part_number",
    "ul_vde_number",
    "validated_at",
    "quantity",
    "designator",
    "unit_price",
    "sub_total",
]
