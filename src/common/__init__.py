"""
Common shared components exposed as stable interfaces for the application.

This package provides public access to cross-cutting components such as ChangeLog, shared data structures, and runtime helpers. These elements carry application-level meaning and are used across multiple subsystems.

Example Usage:
    # Preferred usage via package interface:
    from src.common import ChangeLog
    log = ChangeLog()

Dependencies:
    - Python >= 3.10
    - Standard Library: typing

Notes:
    - Only explicitly exported symbols in __all__ constitute the public API.
    - Internal modules (prefixed with "_") are not intended for external import.
    - This package defines shared, semantic components—not general-purpose helpers.

License:
    - Internal Use Only
"""
# noinspection PyProtectedMember
from ._change_log import ChangeLog  # Direct internal import for export via package interface
# noinspection PyProtectedMember
from ._cache_read_only import extract_uppercase_keys  # Direct internal import for export via package interface
# noinspection PyProtectedMember
from ._cache_read_only import CacheReadOnly # Direct internal import for export via package interface
# noinspection PyProtectedMember
from ._cache_read_write import CacheReadWrite # Direct internal import for export via package interface

__all__ = [
    "ChangeLog",
    "CacheReadOnly",
    'CacheReadWrite',
    "extract_uppercase_keys",
]
