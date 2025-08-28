"""
Public API aggregator for the `utils` package.

This module defines and re-exports the curated, stable surface of `utils`. All symbols listed in `__all__` are imported from internal implementation modules (e.g., `_sanitizer`) and exposed here for external use.

Example Usage:
    # Preferred usage via the package interface:
    # Not exposed publicly; this is an internal module.

    # Direct module usage (intended for testing or internal tooling only):
    import src.utils._api as api
    text = api.normalize_spaces("A    B")

Dependencies:
    - Python >= 3.9
    - Standard Library: re, typing

Notes:
    - This module acts only as a stable facade; implementation lives in internal modules.
    - Keep this file logic-free to preserve clarity and predictable imports.
    - Public imports should always go through `src.utils` rather than `_api`.

License:
 - Internal Use Only

"""

# noinspection PyProtectedMember
from ._console import (
    prompt_string_input
)
# Import the implementation symbols from internal modules
# noinspection PyProtectedMember
from ._sanitizer import (
    normalize_spaces,
    normalize_to_string,
    remove_all_whitespace,
)

# Define exactly what is public.
# __all__ is the single source of truth for the public API.
__all__ = [
    "prompt_string_input",
    "normalize_spaces",
    "normalize_to_string",
    "remove_all_whitespace",
]
