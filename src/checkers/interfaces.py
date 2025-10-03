"""
Public interface for the `checkers` package.

This module serves as a facade, re-exporting selected functions from internal checker modules. Consumers should import from here instead of directly accessing internal files, preserving flexibility to change internal structure without breaking external code.

Example Usage:
    import src.checkers.interfaces as checker
    from src.models.interfaces import Bom
    result = checker.check_v3_bom(bom)

Dependencies:
    - Python >= 3.9
    - Internal: src.checkers._v3_bom

Design Notes & Assumptions:
    - Only curated functions are exported via `__all__`; internal helpers remain private.
    - Encourages consistent external usage and decouples consumers from internal layout.
    - Extendable as new checker modules are added.

License:
 - Internal Use Only
"""

# Re-export selected API from internal modules to expose as public API
# noinspection PyProtectedMember
from ._bom import (
    check_bom as check_v3_bom
)

__all__ = [
    "check_v3_bom"
]
