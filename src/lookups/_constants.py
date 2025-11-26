"""
Defines constants for locating and identifying JSON files in the map module.

This module supplies shared path, prefix, and file-name constants used by resource loaders. These values are consumed by internal loaders in `_resources.py` and exposed indirectly through the public `interfaces` module.

Example Usage:
    # Preferred usage via public package interface:
    # Not publicly exposed; this is an internal module.

    # Direct module usage (acceptable in unit tests or internal scripts only):
    from src.maps import _constants as constant
    folder = constant.SETTINGS_FOLDER_PARTS

Dependencies:
    - Python >= 3.10
    - Standard Library: typing

Notes:
    - These values are intentionally kept stable to avoid breaking downstream resource loaders.
    - The module is internal-only; constants are re-exposed selectively by `interfaces.py`.

License:
    - Internal Use Only
"""
__all__ = []  # Internal-only; not part of public API. Star import from this module gets nothing.

from typing import Final

# MODULE CONSTANTS
JSON_PREFIX: Final[str] = "_"
FOLDER_PARTS: Final[tuple[str, ...]] = ("src", "lookups",)
COMPONENT_TYPE_FILE_NAME: Final[str] = "component_type"  # Name of the JSON resource file (without prefix and extension)
