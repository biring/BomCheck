"""
Public interface for the `cli` package.

This module serves as a facade, re-exporting selected functions from internal cli modules. Consumers should import from here instead of directly accessing internal files, preserving flexibility to change internal structure without breaking external code.

Example Usage:
    # Preferred usage via public package interface:
    from src.cli import interfaces as console
    choice = console.menu_selection(["Scan", "Parse", "Report"])

Dependencies:
 - Python >= 3.10
 - Standard Library: typing (optional)

Notes:
 - This is the public API boundary; internals may change without notice.
 - Keep this facade thin: only forward calls and avoid side effects or formatting logic.
 - Prefer importing this module in application code and tests to decouple from private modules.

License:
 - Internal Use Only
"""

# noinspection PyProtectedMember
from ._show import (
    error as show_error,
    header as show_header,
    info as show_info,
    log as show_log,
    success as show_success,
    warning as show_warning,
)
# noinspection PyProtectedMember
from ._prompt import (
    menu_selection as prompt_menu_selection,
    string_value as prompt_for_string_value,
)

# Define exactly what is public interface.
__all__ = [
    # from prompt module
    "prompt_menu_selection",
    "prompt_for_string_value",
    # from show module
    "show_error",
    "show_header",
    "show_info",
    "show_log",
    "show_success",
    "show_warning",
]
