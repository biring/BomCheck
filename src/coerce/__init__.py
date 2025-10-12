"""
Package initializer for the `coerce` package.

Exposes only the `interfaces` submodule at package level to enforce a clean, stable façade for consumers. This prevents direct imports from internal modules and ensures future refactors do not break external code.

Example Usage:
    from src.coerce import interfaces as coerce
    result_bom, result_log = coerce.v3_bom(raw_bom)
    print(result_log)

Dependencies:
    - Python >= 3.10
    - Standard Library only

Notes:
    - Keeps __all__ minimal to expose only the façade module (`interfaces`).
    - Internal submodules are not considered public API and may change without notice.

License:
    - Internal Use Only
"""

__all__ = ["interfaces"]
