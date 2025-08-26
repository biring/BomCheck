"""
Test fixtures for checkers package unit tests.

Provides canonical "good" data objects for headers, rows, boards, and complete BOMs. These fixtures are reused across multiple test suites to keep tests consistent, concise, and maintainable.

Example Usage:
    from ._fixtures import _HEADER
    result = _check_header("file.xlsx", "Sheet1", _HEADER)

Dependencies:
    - Python >= 3.9
    - Internal: src.models.interfaces (Bom, Board, Header, Row)

Design Notes & Assumptions:
    - Fixtures are intentionally valid to serve as a baseline for tests.
    - Tests may clone/modify these fixtures with `dataclasses.replace` to simulate invalid cases.
    - Centralizing fixtures reduces duplication and ensures consistency across test modules.

License:
 - Internal Use Only
"""

from src.models.interfaces import Bom, Board, Header, Row

_HEADER = Header(
    model_no="AB100", board_name="Power PCBA", manufacturer="Delta",
    build_stage="MB", date="01/12/2025", material_cost="0.8",
    overhead_cost="0.4", total_cost="1.2")

_ROW_ONE = Row(
    item="1", component_type="Resistor", device_package="0603",
    description="2k, 1%, 0603", unit="PCS", classification="A",
    manufacturer="Delta", mfg_part_number="RES002R3A0306", ul_vde_number="UL569",
    validated_at="EB0", qty="2", designator="R1, R2", unit_price="0.1", sub_total="0.2"
)

_ROW_ONE_ALT = Row(
    item="", component_type="ALT1", device_package="0603",
    description="2k, 1%, 0603", unit="PCS", classification="A", manufacturer="Alpha",
    mfg_part_number="AR200010603", ul_vde_number="VDE2345TJ", validated_at="P1",
    qty="0", designator="", unit_price="0.2", sub_total="0"
)

_ROW_TWO = Row(
    item="2", component_type="Capacitor", device_package="0805",
    description="10uF, 10%, 50V, 0805", unit="PCS", classification="B", manufacturer="Sigma",
    mfg_part_number="CC106050100805", ul_vde_number="UL1C2", validated_at="MP",
    qty="3", designator="C1, C2, C3", unit_price="0.2", sub_total="0.6"
)

_BOARD_ONE = Board(
    header=_HEADER,
    sheet_name="Sheet1",
    rows=[_ROW_ONE, _ROW_ONE_ALT],
)

_BOARD_TWO = Board(
    header=_HEADER,
    sheet_name="Sheet2",
    rows=[_ROW_TWO],
)

_BOM = Bom(file_name="sample.xlsx", boards=[_BOARD_ONE, _BOARD_TWO])
