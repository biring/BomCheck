"""
Public initializer and facade for the settings package.

This module defines the supported public surface for application settings and re-exports stable entry points for runtime and application-level configuration access.

Example Usage:
    # Preferred usage via package import:
    from src.settings import temporary
    temp_settings = temporary.get_settings()

Dependencies:
    - Python >= 3.9
    - Standard Library only

Notes:
    - This module is the only supported public entry point for the settings package.
    - Submodules explicitly re-exported here are considered stable API.
    - Internal module structure may change without notice outside this facade.
    - Callers should not import protected modules directly.

License:
    - Internal Use Only
"""

# --- public module namespaces ---
from . import _application as application
from . import _temporary as temporary

# --- Combined public symbols ---
__all__ = [
    "application",
    "temporary",
]
