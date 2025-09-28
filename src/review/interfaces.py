"""
Public interfaces for the `review` package.

This module re-exports curated BOM review helpers from internal modules to provide a stable API boundary. External consumers should import from here rather than private `_` modules.

Example Usage:
    # Preferred usage via public package interface:
    from src.review import interfaces as review
    review.classification(row)

    # Direct internal access (allowed in tests or internal scripts only):
    from src.review import interfaces as review
    review.classification(row)

Dependencies:
    - Python >= 3.10
    - Standard Library: None (re-export only)
    - External Packages: None

Notes:
    - Acts as a stable import target; internal module layout may change without breaking callers.
    - Only a curated subset is exported via __all__; private helpers remain internal.
    - Intended for use by parsers, validators, and reporting tools that need BOM approval semantics.

License:
    - Internal Use Only
"""

# Re-export selected API from internal modules to expose as public API

# noinspection PyProtectedMember
from src.review._row import (
    item,
    component_type,
    device_package,
    description,
    units,
    classification,
    mfg_name,
    mfg_part_no,
    ul_vde_number,
    validated_at,
    quantity,
    designator,
    unit_price,
    sub_total,
)

# noinspection PyProtectedMember
from src.review._header import (
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
from src.review._logic import (
    quantity_zero,
    designator_required,
    designator_count,
    unit_price_specified,
    subtotal_zero,
    sub_total_calculation,
    material_cost_calculation,
    total_cost_calculation,
)

__all__ = [
    # row
    "item",
    "component_type",
    "device_package",
    "description",
    "units",
    "classification",
    "mfg_name",
    "mfg_part_no",
    "ul_vde_number",
    "validated_at",
    "quantity",
    "designator",
    "unit_price",
    "sub_total",

    # header
    "model_number",
    "board_name",
    "board_supplier",
    "build_stage",
    "bom_date",
    "material_cost",
    "overhead_cost",
    "total_cost",

    # logic
    "quantity_zero",
    "designator_required",
    "designator_count",
    "unit_price_specified",
    "subtotal_zero",
    "sub_total_calculation",
    "material_cost_calculation",
    "total_cost_calculation",

]
