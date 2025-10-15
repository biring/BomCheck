"""
Package initializer for the `coerce` package.

Exposes only the `interfaces` submodule at package level to enforce a clean, stable façade for consumers. This prevents direct imports from internal modules and ensures future refactors do not break external code.

Example Usage:
    # Preferred usage via package interface:
    from src.coerce import interfaces as coerce
    value, log = coerce.model_number("  ab123x  ")
    print(value)  # "AB123X"

Dependencies:
    - Python >= 3.10
    - Standard Library: None

Notes:
    - `__all__` explicitly restricts exports to the `interfaces` façade.
    - Internal modules are not part of the public API and may change without notice.
    - This structure maintains forward compatibility for downstream parsers, checkers, and reviewers.

License:
    - Internal Use Only
"""

__all__ = ["interfaces"]
