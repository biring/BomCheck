"""
Defines symbolic key constants representing valid entries in the _component_type.json runtime resource.

This module defines all uppercase string constants expected in the `_component_type.json` file under the runtime directory. Each constant represents a JSON key mapped to a string or list[str] value in the "data" section.

Example Usage:
    # Preferred usage via public package interface:
    # Not publicly exposed; this is an internal module.

    # Direct module usage (acceptable in tests or internal tools only):
    from src.runtime import _component_type as ct
    print(ct.CONNECTOR)

Dependencies:
    - Python >= 3.10
    - Internal: ._core (for export_keys)

Notes:
    - `__all__` is generated automatically using `export_keys(globals())`.
    - Keep constants in uppercase for automatic inclusion in REQUIRED_KEYS.
    - Designed for internal runtime schema validation; loaded by Cache in `_helpers.py`.
    - Do not manually modify `__all__` or `REQUIRED_KEYS`; both are derived from module constants.

License:
 - Internal Use Only
"""

from . import _helpers as hlp

# Required key constants for this runtime resource
# No hardcoded symbolic constants defined here. Keys are dynamically derived from the JSON schema at runtime.

# Derive `__all__` from all UPPERCASE string constants defined in this module.
# This ensures only symbolic keys are exported and used elsewhere.
__all__ = hlp.export_keys(globals())

# Snapshot of required keys expected to exist in `_component_type.json`.
# Keep this in sync with the constant list above.
REQUIRED_KEYS: list[str] = __all__.copy()
