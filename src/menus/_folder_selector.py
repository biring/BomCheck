"""
Interactive folder selector workflow for the CLI.

This module provides a menu-driven helper that lets a user browse from the application root (or an optional starting folder) and select a target folder path. It relies on the shared CLI interfaces and folder-path utilities for consistent prompting, parent-folder navigation, and subfolder discovery.

Example Usage:
    # Preferred usage via the CLI package interface:
    from src.menus import interfaces as menu
    chosen_folder = menu.select_folder()

    # Direct module usage in tests or internal scripts:
    import src.menus._folder_selector as fs
    chosen_folder = fs.select_folder("C:\\Code")

Dependencies:
    - Python >= 3.10
    - Standard Library: None
    - External Packages: src.cli.interfaces

Notes:
    - Intended for interactive, terminal-based use; not suitable for non-interactive or batch execution.

License:
    - Internal Use Only
"""

__all__ = []  # Internal-only; not part of the public CLI API.

from src.utils import folder_path
from src.cli import interfaces as cli

_DEFAULT_MENU_TITLE: str = "Select a folder"
_DEFAULT_MENU_PROMPT: str = "Enter a number to make folder selection: "
_MSG_FOLDER_LEVEL_UP: str = "Go up one level"
_MSG_SELECT_THIS_FOLDER: str = "Select current folder '{a}'"
_ERR_INVALID_START_PATH: str = "Folder selection start path is not a valid directory: {a!r}"


def folder_selector(
        start_path: str | None = None,
        menu_title: str | None = None,
        menu_prompt: str | None = None,
) -> str:
    """
    Run an interactive folder selector loop and return the chosen folder path.

    The selector starts at the application root folder by default and uses a menu-based CLI prompt to let the user move up one level, enter a subfolder, or select the current folder. If a valid `start_path` is provided, that folder is used as the initial location instead of the project root.

    Menu text can be customized via the `menu_title` and `menu_prompt` parameters. If either is None or an empty string, the default values defined in this module are used.

    Args:
        start_path (str | None): Optional starting folder path. If None, the application root folder is used. If provided, it must be a valid folder path.
        menu_title (str | None): Optional menu title shown above the list of folder options (for example, "Select Input File Folder" or "Select Output File Folder"). If None or an empty string, a default title is used.
        menu_prompt (str | None): Optional prompt line shown to the user when asking for a selection (for example, "Enter a number to select input folder: "). If None or an empty string, a default prompt is used.

    Returns:
        str: The normalized path of the folder selected by the user at the end of the interactive session.

    Raises:
        ValueError: If `start_path` is provided but does not represent a valid folder path.
    """
    # Resolve default starting folder from the project configuration
    current_folder: str = folder_path.resolve_project_folder()

    # Override starting folder if a valid explicit path is supplied
    if start_path is not None:
        if folder_path.is_folder_path(start_path):
            current_folder = start_path
        else:
            # Fail fast if the caller passes an invalid starting directory
            raise ValueError(_ERR_INVALID_START_PATH.format(a=start_path))

    # Derive effective menu title and prompt, falling back to module defaults
    effective_title = menu_title or _DEFAULT_MENU_TITLE
    effective_prompt = menu_prompt or _DEFAULT_MENU_PROMPT

    # Main interactive loop: keep prompting until the user selects a folder
    while True:
        # Compute parent folder, falling back to current if the helper returns an invalid value
        parent_folder = folder_path.go_up_one_folder(current_folder)
        if parent_folder is None or parent_folder == "":
            # Defensive guard, in case folder_path returns an invalid path
            parent_folder = current_folder

        # Build the list of subfolders immediately under the current path
        subfolder_names = sorted(folder_path.list_immediate_sub_folders(current_folder))

        # Construct the menu shown to the user (up, select current, then subfolders)
        menu_options: list[str] = [
            _MSG_FOLDER_LEVEL_UP,
            _MSG_SELECT_THIS_FOLDER.format(a=current_folder),
            *subfolder_names,
        ]

        # Ask the user which action to take using the shared CLI menu helper
        user_selection = cli.prompt_menu_selection(
            menu_options,
            effective_title,
            effective_prompt,
        )

        # Handle "go up one level"
        if user_selection == 0:
            current_folder = parent_folder
            continue

        # Handle "select current folder" and exit loop
        if user_selection == 1:
            break

        # Map the selection index back into the subfolder list (menu is offset by 2)
        subfolder_index = user_selection - 2
        if not (0 <= subfolder_index < len(subfolder_names)):
            # Defensive guard in case the CLI returns an out-of-range index
            continue

        # Move into the selected subfolder and continue the loop
        selected_subfolder_name = subfolder_names[subfolder_index]
        current_folder = folder_path.construct_folder_path(current_folder, (selected_subfolder_name,))

    # Return the final folder path chosen by the user
    return folder_path.normalize_folder_path(current_folder)


if __name__ == "__main__":
    print(folder_selector("C:\\Code"))
