"""
Package initializer for the `rules` package.

Provides a clean entry point for BOM value and logic validation utilities. Consumers should import from `src.rules.interfaces` to access the supported API surface, rather than relying on internal modules.

Example Usage:
    import src.rules.interfaces as rules
    rules.assert_board_name("Main Control PCBA")

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
