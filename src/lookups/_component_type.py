"""
Defines symbolic key constants for the component-type lookup resource.

This module declares the uppercase symbolic constants that represent required keys in the `_component_type.json` lookup file. The REQUIRED_KEYS tuple is dynamically derived from module globals to ensure consistency with schema expectations.

Example Usage:
    # Preferred usage via public package interface:
    # Not applicable; this is an internal module.

    # Direct module usage (acceptable in tests or internal tools only):
    from src.lookups import _component_type as ct
    keys = ct.REQUIRED_KEYS

Dependencies:
    - Python >= 3.10
    - Internal: src.lookups._helpers

Notes:
    - Only uppercase constants are extracted into REQUIRED_KEYS.
    - This module contains no hardcoded symbolic constants for now; schema-driven values should be added as uppercase names when needed.
    - Not part of the public API; accessed indirectly through resource loaders.

License:
    - Internal Use Only
"""

# Required key constants for this resource
# No hardcoded symbolic constants defined here. Keys are dynamically derived from the JSON schema at settings.

# Snapshot of required keys expected to exist in `_component_type.json`. Keep this in sync with the constant list above.
REQUIRED_KEYS: tuple[str, ...] = ()  # No required keys for this module
