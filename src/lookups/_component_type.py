"""
Component type lookup loader for BOM parsing and normalization.

This module provides read-only access to the component type lookup JSON resource used during BOM parsing, correction, and validation flows. It lazily loads the lookup table from runtime resources, validates integrity via a read-only cache, and always returns a defensive copy.

Example Usage:
    # Preferred usage via public package interface:
    # Not applicable; this is an internal module.

    # Direct module usage (acceptable in unit tests or internal scripts only):
    from src.lookups import _component_type_lookup as ct
    table = ct.get_component_type_lookup_table()

Dependencies:
    - Python >= 3.10
    - Standard Library: typing
    - Internal Packages: src.common.CacheReadOnly, src.utils.folder_path

Notes:
    - Internal-only module; not part of the public lookup API surface.
    - JSON resources are treated as immutable runtime data and cached once per process.
    - Callers always receive a defensive copy to prevent accidental mutation.
    - Intended for parsers, fixers, and validators requiring stable component type mappings.

License:
    - Internal Use Only
"""
__all__ = []  # Internal-only; not part of public API. Star import from this module gets nothing.

from typing import Final, Any

from src.common import CacheReadOnly
from src.utils import folder_path

# MODULE CONSTANTS
# Where the JSON resource resides in the project
COMPONENT_TYPE_FOLDER_PARTS: Final[tuple[str, ...]] = ("src", "resources", "lookups",)
# Name of the JSON resource file
COMPONENT_TYPE_RESOURCE_NAME: Final[str] = "component_type"
# Define required schema keys for settings validation
_REQUIRED_KEYS: Final[tuple[str, ...]] = ()

# MODULE VARIABLES
# Lazily initialized cache for the shared application settings instance.
_cache: CacheReadOnly | None = None


def get_component_type_lookup_table() -> dict[str, Any]:
    """
    Return a defensive copy of the component type lookup table.

    The lookup table is loaded lazily from the runtime resources directory and cached for the lifetime of the process. The returned dictionary is a copy to prevent mutation of shared state.

    Returns:
        dict[str, Any]: Component type lookup mapping.

    Raises:
        RuntimeError: If the lookup resource cannot be loaded or validated.
    """
    global _cache

    # Lazily initialize the cache on first access
    if _cache is None:
        resource_folder = folder_path.construct_folder_path(
            base_path=folder_path.resolve_project_folder(),
            subfolders=COMPONENT_TYPE_FOLDER_PARTS
        )
        try:
            _cache = CacheReadOnly(
                resource_folder=resource_folder,
                resource_name=COMPONENT_TYPE_RESOURCE_NAME,
                required_keys=_REQUIRED_KEYS,
            )
        except Exception as exc:
            raise RuntimeError(
                f"Failed to load component type lookup '{COMPONENT_TYPE_RESOURCE_NAME}' from resource folder '{resource_folder}'."
                f"\n{exc}"
            ) from exc

    # Always return a defensive copy to prevent shared-state mutation
    return _cache.get_data_map_copy()
