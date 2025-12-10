"""
Public initializer and facade for the `settings` package.

This module exposes stable, public entry points to settings submodules (for example, temporary settings used by the application at runtime).

Example Usage:
    # Preferred usage via package import:
    from src.settings import temporary
    temp_settings = temporary.get_settings()

Dependencies:
    - Python >= 3.9
    - Standard Library only

Notes:
    - Intended as the public entry point for the `settings` package.
    - Submodules listed in `__all__` are part of the supported surface area.
    - Internal layout of the `src.settings` package may change without affecting this facade.

License:
    - Internal Use Only
"""

# --- public module namespaces ---
from . import _temporary as temporary

# --- Combined public symbols ---
__all__ = [
    "temporary",
]
