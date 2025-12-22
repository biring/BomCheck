"""
Package initializer for the exporters package.

This package provides the public façade for BOM-related export workflows. All supported exports are exposed through the interfaces module while internal implementation modules remain private and free to evolve.

Example Usage:
    # Preferred usage via package-level façade:
    from src.exporters import interfaces as export
    file_name = export.build_checker_log_filename(bom)

Dependencies:
    - Python >= 3.10
    - Standard Library: None
    - External Packages: None

Notes:
    - Only the interfaces module is considered part of the supported public API.
    - Internal modules may change without notice and should not be imported directly.

License:
    - Internal Use Only
"""
__all__ = ["interfaces"]
