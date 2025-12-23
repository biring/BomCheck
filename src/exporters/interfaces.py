"""
Public interface façade for the `exporters` package.

This module exposes the approved, stable import API for callers. It re-exports file import implemented in internal modules, ensuring that internal structure may evolve without breaking imports.

Example Usage:
    # Preferred usage via package interface:
    from src.exporters import interfaces as export
    file_name = export.build_checker_log_file_name(Bom)

    # Direct internal usage (acceptable in tests only):
    # Not applicable. Use public package interface.

Dependencies:
    - Python >= 3.10
    - Standard Library: None
    - Internal Modules: ._build_filename.py

Notes:
    - Serves as the single public import location for all menu interactions.
    - Internal modules remain non-public and may change without notice.


License:
    - Internal Use Only
"""

# Re-export approved API functions from internal modules
# noinspection PyProtectedMember
from ._build_filename import build_checker_log_filename
# noinspection PyProtectedMember
from ._text_file import write_text_file_lines

__all__ = [
    "build_checker_log_filename",
    "write_text_file_lines",
]
