"""
Public initializer for the `utils` package.

This module exposes the primary `src.utils` namespace and re-exports key utility submodules as a flat, stable entry point.

Example Usage:
    # Preferred usage via package import:
    from src.utils import excel_io
    df_map = excel_io.map_excel_sheets_to_string_dataframes(path)

Dependencies:
    - Python >= 3.9
    - Standard Library only

Notes:
    - Intended as the public entry point for the `utils` package.
    - Submodules listed in `__all__` are part of the supported surface area.
    - Internal layout of the `src.utils` package may change without affecting this facade.

License:
 - Internal Use Only
"""

# --- public module namespaces ---
from . import excel_io
from . import file_path
from . import folder_path
from . import json_io
from . import parser
from . import sanitizer
from . import text_io
from . import timestamp

# --- Combined public symbols ---
__all__ = [
    "excel_io",
    "file_path",
    "folder_path",
    "json_io",
    "parser",
    "sanitizer",
    "text_io",
    "timestamp",
]
