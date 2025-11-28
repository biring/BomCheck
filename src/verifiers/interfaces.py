"""
Public interface façade for BOM verification workflows.

This module exposes a curated, stable surface over the `verifiers` package so callers can run BOM verification without depending on internal layout. Currently it provides the version-3 BOM verifier.

Example Usage:
    # Preferred usage via package interface:
    from src.verifiers import interfaces as verify
    verify.v3_bom(bom)

    # Direct module usage (acceptable in tests or internal tools only):
    from src.verifiers.interfaces import v3_bom
    v3_bom(bom)

Dependencies:
    - Python >= 3.10
    - Standard Library: None
    - External Packages: None

Notes:
    - Acts as the public façade; internal verifier modules may change without affecting this interface.
    - Only functions listed in __all__ are considered part of the supported API surface.

License:
    - Internal Use Only
"""


# Re-export selected API from internal modules to expose as public API

# noinspection PyProtectedMember
from ._v3_bom import verify_v3_bom as v3_bom

__all__ = [
    "v3_bom",
]
