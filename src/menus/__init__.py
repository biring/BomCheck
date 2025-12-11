"""
Package initializer for the `menus` package.

This module restricts public exports to the `interfaces` façade, preserving a clean and stable API surface while allowing internal selector modules to evolve without breaking callers.

Example Usage:
    # Preferred usage via package-level import:
    from src.menus import interfaces as menu
    path = menu.folder_selector("C:\\Projects")


Dependencies:
    - Python >= 3.10
    - Standard Library: None

Notes:
    - `__all__` explicitly exposes only the `interfaces` module.
    - Internal modules are not part of the public API.

License:
    - Internal Use Only
"""

__all__ = ["interfaces"]
