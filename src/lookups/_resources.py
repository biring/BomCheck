"""
Internal loader and access layer for JSON-backed lookup resources.

This module coordinates loading, validation, and caching of lookup resources. It wraps `JsonCache` to provide checksum verification, required-key validation, and map-style access to JSON payloads. All public access occurs through `interfaces.py`; this module remains internal to preserve API stability.

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
    - External: src.common.JsonCache

Notes:
    - Designed for one-time initialization at application startup.
    - Each resource loader should assign exactly one shared JsonCache instance.
    - New lookup types should register their loader in load_cache().

License:
    - Internal Use Only
"""
__all__ = []  # Internal-only; not part of public API.

from src.common import JsonCache
from . import _constants as constant
from . import _component_type as component_type


def load_cache() -> None:
    """
    This function initializes all lookup resource caches once at startup by invoking each registered resource loader.

    Args:

    Returns:
        None: All configured mapping caches are initialized on success.

    Raises:
        RuntimeError: If any underlying resource loader fails to construct or validate its JsonCache instance.
    """

    # Initialize all settings cache; add new loaders here as new settings modules are introduced.
    _load_component_type_cache()


# ----------------------------------------------------------------------------
# COMPONENT TYPE
# ----------------------------------------------------------------------------

# MODULE VARIABLES
_component_type_cache: JsonCache | None = None  # Cache instance for storing component type settings data. Initialized once and reused for subsequent queries.


def _load_component_type_cache() -> None:
    """
    Build and cache the component-type settings JsonCache.

    This function constructs a JsonCache for the component-type JSON resource, validates required keys, and stores the instance in the module-level cache variable.

    Args:

    Returns:
        None: The module-level component-type cache variable is updated on success.

    Raises:
        RuntimeError: If JsonCache construction, file access, or validation fails for the component-type resource.
    """
    global _component_type_cache  # Require to rebind or modify the module variable
    # Build the component_type JsonCache and store it in the shared module-level cache.
    try:
        _component_type_cache = JsonCache(
            resource_name=constant.COMPONENT_TYPE_FILE_NAME,
            resource_folder_parts=constant.FOLDER_PARTS,
            required_keys=component_type.REQUIRED_KEYS,
            resource_prefix=constant.JSON_PREFIX,
        )
    except Exception as err:
        # All underlying exceptions are wrapped in RuntimeError for uniformity.
        raise RuntimeError(
            f"Failed to load '{constant.COMPONENT_TYPE_FILE_NAME}' settings cache."
            f"\n{type(err).__name__}: {str(err)}"
        ) from err


def get_component_type_cache() -> JsonCache:
    """
    Return the initialized component-type settings cache.

    This accessor provides read-only access to the shared JsonCache instance for component-type settings and enforces that initialization has occurred.

    Args:

    Returns:
        JsonCache: The initialized JsonCache instance containing component-type settings data.

Raises:
    RuntimeError: If the component-type cache has not been initialized via load_cache().
    """
    if _component_type_cache is None:
        raise RuntimeError(
            "Component-type settings cache is not initialized. Load cache before accessing it."
        )
    return _component_type_cache
