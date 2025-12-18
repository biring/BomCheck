"""
Public interface for JSON-backed lookup resources.

This module exposes a stable API for loading JSON-backed lookup resources and accessing their caches, while keeping per-resource implementation modules private.

Example Usage:
    # Preferred usage via public package interface:
    from src.lookups import interfaces as lookup
    table = lookup.get_component_type_lookup_table()

    # Direct imports of private modules (acceptable only in unit tests):
    # Not applicable. Use public package interface.

Dependencies:
    - Python >= 3.10
    - Standard Library: typing
    - Internal Modules: src.lookups._component_type

Notes:
    - Acts as the sole public access point for lookup resources.

License:
    - Internal Use Only
"""

# noinspection PyProtectedMember
from ._component_type import (
    COMPONENT_TYPE_FOLDER_PARTS,
    COMPONENT_TYPE_RESOURCE_NAME,
    get_component_type_lookup_table,
)

__all__ = [
    "COMPONENT_TYPE_FOLDER_PARTS",
    "COMPONENT_TYPE_RESOURCE_NAME",
    "get_component_type_lookup_table",
]