"""
Runtime resource loader and accessor.

This module provides a unified API to load and access all runtime JSON resources used by the application. It wraps the `Cache` class to handle loading, validation (checksum + required keys), and retrieval of key/value pairs from JSON files stored under `src/runtime/`.

Example Usage:
    # Preferred usage via package interface:
    from src.runtime import interfaces as runtime
    runtime.load_all_resources()
    keys = runtime.get_component_type_keys()

    # Direct module usage (for internal scripts or tests only):
    from src.runtime import _resources as res
    res.load_all_resources()
    values = res.get_component_type_values("Capacitor")

Dependencies:
    - Python >= 3.10
    - Standard Library: functools, typing
    - Internal Packages: src.runtime._cache, src.runtime._component_type
    - External Packages: None

Notes:
    - The `*_SOURCE` constant must match the JSON file (e.g., for resource "_component_type.json").
    - All values in the JSON `data` section must be strings or lists of strings.
    - The business logic for validation and I/O resides in `_helpers`; this module only coordinates loading and access.
    - Intended to be imported indirectly via `src.runtime.interfaces` to preserve a stable, public surface while keeping per-category modules private.

License:
 - Internal Use Only
"""
__all__ = []  # Internal-only; not part of public API.

from typing import Final
from . import _cache as cache


def load_all_resources() -> None:
    """
    Load all supported runtime resource categories into memory.

    Initializes per-category caches once during application startup. Add new loaders here as more runtime resource modules are introduced.

    Args:

    Returns:
        None: All registered resource caches are populated on success.

    Raises:
        RuntimeError: If any resource fails to load or validate.
    """
    # Initialize all runtime caches; add new loaders here as new resource modules are introduced.
    _load_component_type()


# ----------------------------------------------------------------------------
# COMPONENT TYPE RESOURCE
# ----------------------------------------------------------------------------

from . import _component_type as component_type

# MODULE CONSTANTS
# Name of the JSON resource file (without extension) for component type definitions.
# Used as the logical identifier for loading the corresponding runtime resource.
COMPONENT_TYPE_SOURCE: Final[str] = "component_type"

# MODULE VARIABLES
# Global cache instance storing data from the '_component_type.json' resource.
# Initialized once and reused for subsequent queries.
component_type_cache: cache.Cache = cache.Cache()


def _load_component_type() -> None:
    """
    Load and validate the 'component_type' runtime resource.

    Delegates to the shared cache to load the JSON by resource stem and enforce required keys for the category.

    Args:

    Returns:
        None: Updates the module-level cache in place.

    Raises:
        RuntimeError: If the resource cannot be loaded, validated, or accessed.
    """
    try:
        component_type_cache.load_resource(COMPONENT_TYPE_SOURCE, component_type.REQUIRED_KEYS)
    except Exception as err:
        # All underlying exceptions are wrapped in RuntimeError for uniformity.
        raise RuntimeError(
            f"'{COMPONENT_TYPE_SOURCE}' resource failed to load."
            f"\n{type(err).__name__}: {str(err)}"
        ) from err


def get_component_type_keys() -> tuple[str, ...]:
    """
    Return all keys defined in the 'component_type' resource.

    Provides an immutable snapshot of available top-level keys for downstream logic.

    Args:

    Returns:
        tuple[str, ...]: All keys present in the resource, in cache order.

    Raises:
        RuntimeError: If the resource cannot be loaded, validated, or accessed.
    """
    try:
        return component_type_cache.get_all_keys()
    except Exception as err:
        # All underlying exceptions are wrapped in RuntimeError for uniformity.
        raise RuntimeError(
            f"'{COMPONENT_TYPE_SOURCE}' resource has no keys."
            f"\n{type(err).__name__}: {str(err)}"
        ) from err


def get_component_type_values(key: str) -> tuple[str, ...]:
    """
    Retrieve the string list associated with a 'component_type' key.

    Returns a normalized, immutable tuple of strings for the specified key.

    Args:
        key (str): The component type key to look up.

    Returns:
        tuple[str, ...]: The list of strings mapped to the key.

    Raises:
        RuntimeError: If the resource cannot be loaded, validated, or accessed.
    """
    try:
        return component_type_cache.get_list_value(key)
    except Exception as err:
        # All underlying exceptions are wrapped in RuntimeError for uniformity.
        raise RuntimeError(
            f"'{COMPONENT_TYPE_SOURCE}' resource key '{key}' could not be read. "
            f"\n{type(err).__name__}: {str(err)}"
        ) from err
