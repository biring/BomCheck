"""
Internal loader and access layer for JSON-backed lookup resources.

This module coordinates loading, validation, and caching of lookup resources. It wraps `CacheReadOnly` to provide checksum verification, required-key validation, and map-style access to JSON payloads. All public access occurs through `interfaces.py`; this module remains internal to preserve API stability.

Example Usage:
    # Preferred usage via public package interface:
    # Not applicable. This module is internal.

    # Direct module usage (acceptable only in unit tests or internal scripts):
    from src.lookups import _resources as res
    res.load_cache()
    cache = res.get_component_type_cache()
    data = cache.get_data_map_copy()

Dependencies:
    - Python >= 3.10
    - Standard Library: functools, typing
    - External: src.common.CacheReadOnly

Notes:
    - Designed for one-time initialization at application startup.
    - Each resource loader should assign exactly one shared CacheReadOnly instance.
    - New lookup types should register their loader in load_cache().

License:
    - Internal Use Only
"""
__all__ = []  # Internal-only; not part of public API.

from typing import Final

from src.common import CacheReadOnly
from src.utils import folder_path
from . import _component_type as component_type

# MODULE CONSTANTS
FOLDER_PARTS: Final[tuple[str, ...]] = ("src", "lookups",)
COMPONENT_TYPE_FILE_NAME: Final[str] = "_component_type"  # Name of the JSON resource file


def load_cache() -> None:
    """
    Initialize all lookup resource caches.

    This function invokes each registered loader to construct and validate the module-level CacheReadOnly instances required by the lookup subsystem.

    Args:

    Returns:
        None: All configured caches are initialized on success.

    Raises:
        RuntimeError: If any underlying loader fails to build or validate its CacheReadOnly instance.
    """
    # Initialize all settings cache; add new loaders here as new settings modules are introduced.
    _load_component_type_cache()


# ----------------------------------------------------------------------------
# COMPONENT TYPE
# ----------------------------------------------------------------------------

# MODULE VARIABLES
_component_type_cache: CacheReadOnly | None = None  # Cache instance for storing component type settings data. Initialized once and reused for subsequent queries.


def _load_component_type_cache() -> None:
    """
    Build and cache the component-type CacheReadOnly.

    Loads the component-type JSON resource, validates required keys, and stores the resulting CacheReadOnly instance in the module-level cache variable for reuse.

    Args:

    Returns:
        None: The module-level cache is updated on success.

    Raises:
        RuntimeError: If the CacheReadOnly fails to load, validate, or if the resource file cannot be accessed.
    """
    global _component_type_cache  # Require to rebind or modify the module variable

    # Resolve the absolute path to the lookup resource folder.
    project_root = folder_path.resolve_project_folder()
    lookup_folder_path = folder_path.construct_folder_path(project_root, FOLDER_PARTS)

    # Build the component_type CacheReadOnly and store it in the shared module-level cache.
    try:
        _component_type_cache = CacheReadOnly(
            resource_folder=lookup_folder_path,
            resource_name=COMPONENT_TYPE_FILE_NAME,
            required_keys=component_type.REQUIRED_KEYS,
        )
    except Exception as err:
        # Wrap any underlying failure to provide uniform error reporting.
        raise RuntimeError(
            f"Failed to load '{COMPONENT_TYPE_FILE_NAME}' settings cache. \n{str(err)}"
        ) from err


def get_component_type_cache() -> CacheReadOnly:
    """
    Return the initialized component-type CacheReadOnly.

    Ensures that the corresponding cache was successfully initialized by load_cache() before returning the stored instance.

    Args:

    Returns:
        CacheReadOnly: The initialized cache for the component-type resource.

    Raises:
        RuntimeError: If the component-type cache has not been initialized.
    """
    if _component_type_cache is None:
        raise RuntimeError(
            "Component-type settings cache is not initialized. Load cache before accessing it."
        )
    return _component_type_cache
