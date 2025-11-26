"""
Shared constants for the 'lookups' package.

This module defines stable prefix, folder, and resource-file constants used by all internal lookup resource loaders. These constants are consumed by `_resources.py` and selectively re-exposed through the public `interfaces` module.

Example Usage:
    # Preferred usage via public package interface:
    # Not applicable; this is an internal module.

    # Direct module usage (acceptable in unit tests or internal scripts only):
    from src.lookups import _constants as constant
    folder = constant.FOLDER_PARTS

Dependencies:
    - Python >= 3.10
    - Standard Library: typing

Notes:
    - Constants here define the canonical structure and prefixes of lookup JSON resources.
    - These values ensure all loaders use consistent naming and directory resolution.
    - Internal-only; public modules should access constants via `interfaces`, not this module.

License:
    - Internal Use Only
"""
__all__ = []  # Internal-only; not part of public API.


def extract_uppercase_keys(globals_dict: dict, allowed_value_type: tuple[type, ...]) -> tuple[str, ...]:
    """
    Extract uppercase constant names from a globals mapping.

    Scans the provided mapping and returns all keys that are fully uppercase and whose
    associated values match at least one of the allowed types. The result is sorted to
    ensure stable ordering across environments.

    Args:
        globals_dict (dict): A mapping of names to objects, typically a module-level globals().
        allowed_value_type (tuple[type, ...]): Tuple of permitted value types used to filter constants.

    Returns:
        tuple[str, ...]: A sorted tuple containing all valid uppercase constant names.
    """
    exported_names: list[str] = []

    # Iterate through globals as (name, value) pairs
    for name, value in globals_dict.items():
        # Only include all-uppercase names (conventional constants)
        if name.isupper() and isinstance(value, allowed_value_type):
            exported_names.append(name)

    # Return as a sorted tuple for stable ordering and testability
    return tuple(sorted(exported_names))
