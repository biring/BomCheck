"""
Package initializer for the `importers` package.

This module exposes the stable public façade for BOM and related file import workflows via the `interfaces` module while keeping internal implementation modules private and free to evolve.

Example Usage:
    # Preferred usage via package-level façade:
    from src.importers import interfaces as importers
    excel_dict = importers.read_excel_as_dict("C:\\Data\\Inputs.xlsx")

Dependencies:
    - Python >= 3.10
    - Standard Library: None
    - External Packages: None

Notes:
    - `__all__` is restricted to expose only the `interfaces` façade as the supported public API.
    - Callers should not rely on internal module names or layouts; they may change without notice.
    - Intended for internal use as part of the `src.importers` package within the BomCheck toolchain.

License:
    - Internal Use Only
"""
__all__ = ["interfaces"]
