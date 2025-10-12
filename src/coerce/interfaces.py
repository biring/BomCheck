"""
Public interfaces for the `coerce` package.

This module re-exports curated BOM approval helpers from internal modules to provide a stable API boundary. External consumers should import from here rather than private `_` modules.

Example Usage:
    from src.coerce import interfaces as coerce
    result_bom, result_log = coerce.v3_bom(raw_bom)
    print(result_log)

    # Direct internal access (allowed in tests or internal scripts only):
    from src.coerce import interfaces
    result_bom, result_log = coerce.v3_bom(raw_bom)
    print(result_log)

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
from src.coerce._bom import (
    coerce_bom as v3_bom,
)

__all__ = [
    "v3_bom",
]
