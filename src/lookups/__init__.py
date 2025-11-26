"""
Package initializer for 'lookups'.

This package centralizes all JSON-backed resource files and exposes a single stable public interface (`interfaces`) while keeping implementation modules private.

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

Notes:
    - Only `interfaces` is considered public; all other modules remain internal.
    - Centralizes all lookup/coercion maps for consistent use across settings, parsing, and validation layers.
    - Designed to maintain API stability while permitting internal refactors or data source changes.

License:
    - Internal Use Only
"""
__all__: list[str] = ["interfaces"]
