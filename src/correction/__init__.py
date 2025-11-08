"""
Package initializer for the `correction` package.

Exposes only the `interfaces` submodule at package level to enforce a clean, stable façade for consumers. This prevents direct imports from internal modules and ensures future refactors do not break external code.

Example Usage:
    # Preferred usage via package interface:
    from src.correction import interfaces as correction
    value, log = correction.expand_designators("R1,R2-R5,R7")
    print(value)  # "R1,R2,R3,R4,R5,R7"

Dependencies:
    - Python >= 3.10
    - Standard Library: None

Notes:
    - `__all__` explicitly restricts exports to the `interfaces` façade.
    - Internal modules are not part of the public API and may change without notice.

License:
    - Internal Use Only
"""

__all__ = ["interfaces"]
