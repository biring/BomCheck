"""
Public interface façade for the `menus` package.

This module exposes the approved, stable menu-selection API for callers. It re-exports interactive menu selector workflows implemented in internal modules, ensuring that internal structure may evolve without breaking imports.

Example Usage:
    # Preferred usage via package interface:
    from src.menus import interfaces as menu
    selected_file = menu.file_selector("C:\\Data\\Inputs", (".csv", ".xlsx"))
    selected_folder = menu.folder_selector("C:\\Users\\Desktop")

    # Direct internal usage (acceptable in tests only):
    import src.menus._file_selector as _fs  # not recommended for production use
    f = _fs.file_selector("C:\\Data")

Dependencies:
    - Python >= 3.10
    - Standard Library: None
    - Internal Modules: ._file_selector, ._folder_selector

Notes:
    - Serves as the single public import location for all menu interactions.
    - Internal modules remain non-public and may change without notice.


License:
    - Internal Use Only
"""

# Re-export approved API functions from internal modules
# noinspection PyProtectedMember
from . import _file_selector as file_selector
from . import _folder_selector as folder_selector

__all__ = [
    "file_selector",
    "folder_selector",
]
