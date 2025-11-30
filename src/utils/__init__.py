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

# Import the internal API collector (as a module object)
from . import _api as _api

# Re-export all curated public symbols into the package namespace
from ._api import *  # noqa: F401,F403

# Ensure __all__ matches what _api declares as public.
# This avoids duplication and makes _api the single source of truth.
_api_public = list(getattr(_api, "__all__", []))

# --- public module namespaces ---
from . import folder_path as folder
from . import json_io
from . import timestamp

# --- Combined public symbols ---
__all__ = _api_public + [
    "folder",
    "json_io",
    "timestamp",
]
