"""
CLI helpers for prompting the user for values and menu selections.

Example Usage:
    # Preferred usage via package interface:
    from src.cli import interfaces as cli
    choice = cli.menu_selection(["alpha", "bravo", "charlie"])

    # Direct module usage in internal scripts or tests:
    from src.cli import _prompt as prompt
    text = prompt.string_value("Enter new value: ")

Dependencies:
 - Python >= 3.10
 - Standard Library: None
 - External Packages: None

Notes:

License:
 - Internal Use Only
"""
__all__ = []  # Internal-only; not part of public API. Star import from this module gets nothing.

from src.cli import _request as request
from src.cli import _show as show

_DEFAULT_MENU_HEADER = "Menu options"
_DEFAULT_MENU_PROMPT = "Enter a number to make menu selection: "
_DEFAULT_STRING_VALUE_PROMPT = "Enter new value: "

_ERR_MENU_EMPTY = "Empty menu provided for user selection. "
_ERR_MENU_SELECTION = "Invalid menu selection. "
_ERR_CLI_MODULE = "Unexpected problem with CLI. "


def string_value(select_msg: str = _DEFAULT_STRING_VALUE_PROMPT) -> str:
    try:
        return request.string_input(select_msg)
    except (EOFError, KeyboardInterrupt):
        raise  # pass through exactly as is
    except Exception as e:
        # unexpected bug (e.g., TypeError in caller formatting, etc.)
        # TODO log exception using logger and raise generic error
        raise RuntimeError(_ERR_CLI_MODULE) from e


def menu_selection(menu_items: list[str], header_msg: str = _DEFAULT_MENU_HEADER,
                   select_msg: str = _DEFAULT_MENU_PROMPT) -> int:
    """
    """
    # local variables
    menu_size = len(menu_items)  # include Abort

    if menu_size == 0:
        raise ValueError(_ERR_MENU_EMPTY)
    if menu_size == 1:
        return menu_size - 1  # convert to 0-based index and return

    # Print the list of options available for the user to select
    show.header(f'*** {header_msg.upper()} ***')
    for idx, label in enumerate(menu_items):
        show.info(f"[{idx}] {label}")

    while True:
        try:
            user_input = request.integer_input(select_msg)

            # Valid selection: from 0 to menu_size - 1
            if 0 <= user_input <= menu_size - 1:
                return user_input

            # Otherwise, warn and reprompt
            show.warning(_ERR_MENU_SELECTION)
        except (EOFError, KeyboardInterrupt):
            # pass through expected user exits with their friendly messages from _request
            raise
        except Exception as e:
            # unexpected bug (e.g., TypeError in caller formatting, etc.)
            # TODO log exception using logger and raise generic error
            raise RuntimeError(_ERR_CLI_MODULE) from e
