"""
Public interface for `models` package.

This module serves as a facade, re-exporting selected functions from internal checker modules. Consumers should import from here instead of directly accessing internal files, preserving flexibility to change internal structure without breaking external code.

Main capabilities:
    - Exposes Board, Bom, Header, and Row dataclasses
    - Exposes field mappings and template identifiers
    - Hides internal implementation from external consumers

Example Usage:
    from src.models import interfaces as models
    board = models.Board.empty()

Dependencies:
    - Python >= 3.10

Notes:
    - Only symbols listed in `__all__` are exposed via `src.models`.
    - Designed to maintain a clean, testable, and stable external API.

License:
    - Internal Use Only
"""

# Re-export selected API from internal modules to expose as public API
# noinspection PyProtectedMember
from ._v3_fields import (
    HeaderFields,
    RowFields,
)
# noinspection PyProtectedMember
from ._v3_raw import (
    Board,
    Bom,
    Header,
    Row
)

__all__ = [
    'HeaderFields',
    'RowFields',
    'Board',
    'Bom',
    'Header',
    'Row'
]
