"""
Helpers functions for interactive console input handling.

This module provides safe wrappers for user input. These functions ensure consistent messaging and integrate with `_show` for colorized CLI prompts and warnings.

Example Usage:
    # Preferred usage via package interface:
    # Not exposed publicly; this is an internal module.

    # Direct usage (acceptable in tests or scripts only):
    from src.cli import _request as request
    number = request.integer_input("Enter a number:")

Dependencies:
    - Python >= 3.9
    - Standard Library: builtins (input), exceptions (EOFError, KeyboardInterrupt)
    - Internal: src.cli._show, src.utils

Notes:
    - Designed for interactive CLI workflows.
    - Integer parsing delegates to `utils.parse_to_integer` to centralize numeric validation.
    - Errors are re-raised with user-friendly messages for testability.

License:
    - Internal Use Only
"""
__all__ = []  # Internal-only; not part of public API. Star import from this module gets nothing

import src.utils as utils

# noinspection PyProtectedMember
from src.cli import _show as show

_ERR_INTEGER_INPUT = "Invalid user input. "
_ERR_EOF = "Input stream closed unexpectedly. No input could be read."
_ERR_CTRL_ABORT = "Input was interrupted by the user (Ctrl+C)."


def string_input(prompt) -> str:
    """
    Prompt the user for a string value.

    Displays a colorized prompt and returns the user’s raw input. If the input stream is closed or interrupted, a friendly exception message is raised.

    Args:
        prompt (str): The text prompt to display to the user.

    Returns:
        str: The user’s entered string.

    Raises:
        EOFError: If the input stream is closed before reading.
        KeyboardInterrupt: If the user aborts input with Ctrl+C.
    """
    # Prompt the user for input
    try:
        return input(show.prompt(prompt))
    except EOFError:
        raise EOFError(_ERR_EOF)
    except KeyboardInterrupt:
        raise KeyboardInterrupt(_ERR_CTRL_ABORT)


def integer_input(prompt) -> int:
    """
    Prompt the user until a valid integer is entered.

    Displays a colorized prompt and retries until the user provides an integer. Non-numeric input triggers a warning message and re-prompts.

    Args:
        prompt (str): The text prompt to display to the user.

    Returns:
        int: The validated integer input from the user.

    Raises:
        EOFError: If the input stream is closed before reading.
        KeyboardInterrupt: If the user aborts input with Ctrl+C.
    """
    while True:
        try:
            user_input = string_input(prompt)
            # numeric validation
            return utils.parser.parse_to_integer(user_input)
        except ValueError:
            show.warning(_ERR_INTEGER_INPUT)
