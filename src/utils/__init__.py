"""
Public initializer for the `utils` package.

This module re-exports the curated public API of `utils` so that consumers can access functionality through a flat, stable interface:

Example Usage:
    # Preferred usage via package import:
    import src.utils as utils
    clean = utils.remove_all_whitespace(raw_string)

Capabilities:
    - Re-export all public functions and classes defined in `_api.py`.
    - Centralize the list of exported symbols via a single `__all__`.
    - Ensure consumers do not depend on private/internal modules.

Dependencies:
    - Python >= 3.9
    - Standard Library only

Notes:
    - `_api.py` is the single source of truth for public symbols.
    - Keeps package imports flat and avoids leaking internal module structure.
    - Consumers should always import through `src.utils` rather than `_api`.

License:
 - Internal Use Only
"""

# --- public module namespaces ---
from . import file_path
from . import folder_path
from . import json_io
from . import parser
from . import sanitizer
from . import text_io
from . import timestamp

# --- Combined public symbols ---
__all__ = [
    "file_path",
    "folder_path",
    "json_io",
    "parser",
    "sanitizer",
    "text_io",
    "timestamp",
]
