"""
Helper functions for colorized CLI output.

This module wraps `colorama` to provide consistent colored printing for user interface messages and prompts for user input. These utilities are used across CLI-driven workflows to standardize console feedback.

Example Usage:
    # Preferred usage via package interface:
    # Not exposed publicly; this is an internal module.

    # Direct usage (acceptable in tests or scripts only):
    from src.cli import _show as show
    show.error("Something went wrong")

Dependencies:
 - Python >= 3.9
 - External Packages: colorama
 - Standard Library: None

Notes:
 - Functions here print directly to stdout, except `prompt` which returns a formatted string.
 - This module is internal-only; prefer importing via higher-level interfaces.

License:
 - Internal Use Only
"""
__all__ = []  # Internal-only; not part of public API. Star import from this module gets nothing

from colorama import init, Fore, Style

# Initialize colorama to auto-reset styles after each print
init(autoreset=True)


def error(msg: str) -> None:
    """
    Print an error message in red.

    Args:
        msg (str): The error message to display.

    Returns:
        None
    """
    print(f"{Fore.RED}{msg}{Style.RESET_ALL}")


def header(msg: str) -> None:
    """
    Print a header message in bright white.

    Typically used for section headers or key titles in CLI output.

    Args:
        msg (str): The header text to display.

    Returns:
        None
    """
    print(f"{Fore.LIGHTWHITE_EX}{msg}{Style.RESET_ALL}")


def info(msg: str) -> None:
    """
    Print an informational message in the default terminal color.

    Args:
        msg (str): The informational message to display.

    Returns:
        None
    """
    print(f"{Style.RESET_ALL}{msg}{Style.RESET_ALL}")


def log(msg: str) -> None:
    """
    Print a log message in gray.

    Typically used for low-importance or debug information.

    Args:
        msg (str): The log message to display.

    Returns:
        None
    """
    print(f"{Fore.LIGHTBLACK_EX}{msg}{Style.RESET_ALL}")


def prompt(msg: str) -> str:
    """
    Return a prompt string formatted in blue.

    Unlike other functions in this module, this function does not print directly.
    It is intended for use with `input()` so the prompt color is preserved.

    Args:
        msg (str): The prompt text to display.

    Returns:
        str: The formatted prompt string with blue color applied.
    """
    return f"{Fore.BLUE}{msg}{Style.RESET_ALL}"


def success(msg: str) -> None:
    """
    Print a success message in green.

    Args:
        msg (str): The success message to display.

    Returns:
        None
    """
    print(f"{Fore.GREEN}{msg}{Style.RESET_ALL}")


def warning(msg: str) -> None:
    """
    Print a warning message in yellow.

    Args:
        msg (str): The warning message to display.

    Returns:
        None
    """
    print(f"{Fore.YELLOW}{msg}{Style.RESET_ALL}")
