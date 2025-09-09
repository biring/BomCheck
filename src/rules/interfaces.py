"""
Public interface for the `rules` package.

This module acts as a stable facade layer, re-exporting selected validation functions from internal modules. External code should import exclusively from here to remain decoupled from internal package layout and implementation details.

Example Usage:
    import src.rules.interfaces as rules
    rules.assert_price("12.50")

Dependencies:
    - Python >= 3.9
    - Internal: src.rules._v3_cell_value, src.rules._v3_cell_logic

Design Notes & Assumptions:
    - Provides a public API surface while preserving the freedom to reorganize internal modules without breaking consumers.
    - `__all__` defines the supported contract; functions not listed remain internal.
    - Intended as the only import path for external consumers of `rules`.

License:
 - Internal Use Only
"""

# Re-export selected API from internal modules to expose as public API
# noinspection PyProtectedMember
from ._v3_cell_value import (
    assert_board_name,
    assert_build_stage,
    assert_classification,
    assert_component_type,
    assert_date_format,
    assert_description,
    assert_designator,
    assert_device_package,
    assert_item,
    assert_manufacturer,
    assert_material_cost,
    assert_mfg_part_number,
    assert_model_number,
    assert_overhead_cost,
    assert_qty,
    assert_sub_total,
    assert_total_cost,
    assert_ul_vde_number,
    assert_unit_price,
    assert_units,
    assert_validated_at,

)
# noinspection PyProtectedMember
from ._v3_cell_logic import (
    assert_designator_count_matches_quantity,
    assert_designator_required_for_positive_item_and_qty,
    assert_quantity_positive_when_item_positive,
    assert_quantity_zero_when_item_blank,
    assert_subtotal_matches_product,
    assert_subtotal_zero_when_quantity_zero,
    assert_unit_price_positive_when_quantity_positive
)

__all__ = [
    # Value-level assertions
    "assert_board_name",
    "assert_build_stage",
    "assert_classification",
    "assert_component_type",
    "assert_date_format",
    "assert_description",
    "assert_designator",
    "assert_device_package",
    "assert_item",
    "assert_manufacturer",
    "assert_material_cost",
    "assert_mfg_part_number",
    "assert_model_number",
    "assert_overhead_cost",
    "assert_qty",
    "assert_sub_total",
    "assert_total_cost",
    "assert_ul_vde_number",
    "assert_unit_price",
    "assert_units",
    "assert_validated_at",

    # Logic-level assertions
    "assert_designator_count_matches_quantity",
    "assert_designator_required_for_positive_item_and_qty",
    "assert_quantity_positive_when_item_positive",
    "assert_quantity_zero_when_item_blank",
    "assert_subtotal_matches_product",
    "assert_subtotal_zero_when_quantity_zero",
    "assert_unit_price_positive_when_quantity_positive"
]
