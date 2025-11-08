"""
Public interface façade for the `correct` package.

This module re-exports curated BOM field-correction functions for BOM fix/issue workflows while keeping underlying logic encapsulated. It defines the public entry points for BOM correction workflows while keeping underlying logic encapsulated.

Example Usage:
    # Preferred usage via package interface:
    from src.correct import interfaces as correct
    value, log = correct.expand_designators("R1,R2-R5,R7")
    print(value)  # "R1,R2,R3,R4,R5,R7"

    # Direct internal access (for tests or internal scripts only):
    from src.correct import interfaces as correct
    value, log = correct.expand_designators("R1,R2-R5,R7")
    print(value)  # "R1,R2,R3,R4,R5,R7"

Dependencies:
    - Python >= 3.10
    - Standard Library: None
    - External Packages: None

Notes:
    - Provides a stable import target; internal module layout may evolve without breaking callers.
    - Only approved field-level correction functions are exposed via __all__.
    - Internal modules (_helper, _assist, _auto) remain non-public to callers; this façade re-exports approved functions.

License:
    - Internal Use Only
"""

# Re-export selected API from internal modules to expose as public API

# noinspection PyProtectedMember
from ._assist import (
    model_number,
    board_name,
    board_supplier,
    build_stage,
    bom_date,
    overhead_cost,
    item,
    component_type,
    device_package,
    description,
    unit,
    classification,
    manufacturer,
    mfg_part_number,
    ul_vde_number,
    validated_at,
    qty,
    designator,
    unit_price,
)

# noinspection PyProtectedMember
from ._auto import (
    component_type_lookup,
    expand_designators,
    material_cost,
    sub_total,
    total_cost,
)

__all__ = [
    # header assist
    "model_number",
    "board_name",
    "board_supplier",
    "build_stage",
    "bom_date",
    "overhead_cost",

    # row assist
    "item",
    "component_type",
    "device_package",
    "description",
    "unit",
    "classification",
    "manufacturer",
    "mfg_part_number",
    "ul_vde_number",
    "validated_at",
    "qty",
    "designator",
    "unit_price",

    # auto
    "component_type_lookup",
    "expand_designators",
    "material_cost",
    "sub_total",
    "total_cost",

]
