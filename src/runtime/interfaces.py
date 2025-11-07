"""
Public bindings for runtime resources.

Provides a stable import surface for loading runtime JSON resources and accessing component-type keys/values while keeping per-category modules private.This module exposes the minimal API to load runtime JSON resources and retrieve component-type data without directly accessing internal modules.

Example Usage:
    # Preferred usage via public package interface:
    from src.runtime import interfaces as rt
    rt.load_all_resources()

    # Direct internal access (allowed in tests or internal scripts only):
    Not applicable. Use public package interface provided above

Dependencies:
    - Python >= 3.10
    - Standard Library: typing

Notes:
    - Serves as the boundary layer for runtime resource access.
    - Keeps lower-level modules private and stable across refactors.
    - Intended for other layers like controllers or services.

License:
    - Internal Use Only
"""

# noinspection PyProtectedMember
from ._helpers import (
    RUNTIME_JSON_PREFIX,
    RUNTIME_FOLDER,
)

# noinspection PyProtectedMember
from ._resources import (
    COMPONENT_TYPE_SOURCE,

    load_all_resources,

    get_component_type_data_map,
    get_component_type_keys,
    get_component_type_values,
)

__all__ = [
    # Constants
    RUNTIME_JSON_PREFIX,
    RUNTIME_FOLDER,
    COMPONENT_TYPE_SOURCE,
    # All resource loader
    'load_all_resources',
    # Component type resource
    'get_component_type_data_map',
    'get_component_type_keys',
    'get_component_type_values',
    # Add other resource below as needed
]
