"""
Utility functions for command-line console interactions.

This module provides helpers for prompting and processing user input from the command line. It is intended for **internal use only** within the `utils` package.

Example Usage:
    # Preferred usage via public package interface:
    # Not exposed publicly; this is an internal module.

    # Direct module usage (acceptable in unit tests or internal scripts only):
    import src.utils._console as console
    user_input = console.prompt_string_input("Info", "NOTE", "Enter your name: ")

Dependencies:
    - Python >= 3.9
    - Standard Library

Notes:
    - This module is intended for internal use within the `utils` package.
    - Public functions should be imported via `<root>.utils` where possible to preserve API boundaries.

License:
    - Internal Use Only
"""

__all__ = []  # Internal-only; not part of public API


def prompt_string_input(context_message: str, advisory_message: str, input_prompt: str) -> str:
    """
    Display contextual information and prompt the user for a string input.

    This function optionally displays a context string and an advisory message before prompting the user for input. Leading and trailing whitespace from the user's response is stripped.

    Args:
        context_message (str): Contextual information to display before the message. Ignored if empty or None.
        advisory_message (str): Advisory message to display before the prompt. Ignored if empty or None.
        input_prompt (str): The input prompt shown directly to the user.

    Returns:
        str: The user-provided input with leading/trailing whitespace removed.

    Raises:
        EOFError: If the input stream is closed unexpectedly.
        KeyboardInterrupt: If the user interrupts input (Ctrl+C).
    """

    # Show context message if provided
    if context_message:
        print(context_message)

    # Show advisory message if provided
    if advisory_message:
        print(advisory_message)

    # Prompt the user for input and strip extra spaces
    try:
        return input(input_prompt).strip()
    except EOFError:
        raise EOFError("Input stream closed unexpectedly. No input could be read.")
    except KeyboardInterrupt:
        raise KeyboardInterrupt("Input was interrupted by the user (Ctrl+C).")
