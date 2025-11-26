"""
Public interface for the 'lookups' package.

This module exposes a stable API for loading JSON-backed lookup resources and accessing their caches, while keeping per-resource implementation modules private.

Example Usage:
    # Preferred usage via public package interface:
    from src.lookups import interfaces as lookup
    lookup.load_cache()
    cache = lookup.get_component_type_cache()
    data_map = cache.get_data_map_copy()

    # Direct imports of private modules (acceptable only in unit tests):
    # Not applicable. Use public package interface.

Dependencies:
    - Python >= 3.10
    - Standard Library: typing
    - Internal Modules: ._constants, ._resources

Notes:
    - Provides a stable surface for all lookup-related resource loading.
    - Internal modules may change structure, but this API remains consistent.
    - Supports centralized lookup/coercion maps used across settings, parsing, and validation.

License:
    - Internal Use Only
"""



# noinspection PyProtectedMember
from ._constants import (
    JSON_PREFIX,
    FOLDER_PARTS,
    COMPONENT_TYPE_FILE_NAME,
)

# noinspection PyProtectedMember
from ._resources import (
    load_cache,
    get_component_type_cache,
)

__all__ = [
    # Constants
    JSON_PREFIX,
    FOLDER_PARTS,
    COMPONENT_TYPE_FILE_NAME,
    # All resource loader
    'load_cache',
    # Resource(s)
    'get_component_type_cache',
]
