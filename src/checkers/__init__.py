"""
Package initializer for the `checkers` package.

Exposes only the `interfaces` submodule at package level to enforce a clean, stable facade for consumers. This prevents direct imports from internal modules and ensures future refactors do not break external code.

Example Usage:
    import src.checkers.interfaces as checkers
    checkers.check_v3_bom(bom)

Dependencies:
    - Python >= 3.10
    - Standard Library only

Notes:
    - Keeps `__all__` minimal to expose only the facade module (`interfaces`).
    - Internal submodules are not considered public API and may change without notice.

License:
 - Internal Use Only
"""

__all__ = ["interfaces"]
