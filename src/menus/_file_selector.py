"""
Interactive file selector workflow for the CLI.

This module provides a menu-driven helper that lets a user select a file from a single, caller-specified folder. You may provide an optional tuple of file extensions (e.g., (".csv", ".json")) to filter the file list.

Example Usage:
    # Preferred usage via the CLI package interface:
    from src.menus import interfaces as menu
    chosen_file = menu.select_file(folder_path="C:\\Data\\Inputs", extensions=(".csv", ".xlsx"))

    # Direct module usage in tests or internal scripts:
    import src.menus._file_selector as fs
    chosen_file = fs.file_selector(folder_path="C:\\Data\\Configs",extensions=(".json",))

Dependencies:
    - Python >= 3.10
    - Standard Library: None
    - External Packages: src.cli.interfaces, src.utils.file_path

Notes:
    - This selector does not support folder navigation.
      The caller is responsible for providing a valid folder path.
    - Intended for interactive, terminal-based use.

License:
    - Internal Use Only
"""

__all__ = []  # Internal-only; not part of the public CLI API.

from src.utils import file_path as file_path
from src.utils import folder_path as folder_path
from src.cli import interfaces as cli

_DEFAULT_MENU_TITLE: str = "Select a file"
_DEFAULT_MENU_PROMPT: str = "Enter a number to select a file: "
_ERR_INVALID_FOLDER_PATH: str = "File selector folder path is not a valid directory: {a!r}"
_ERR_NO_FILES_AVAILABLE: str = "No files found in folder {a!r} with the given extensions."


def file_selector(
        folder_path_in: str,
        extensions: tuple[str, ...] | None = None,
        menu_title: str | None = None,
        menu_prompt: str | None = None,
) -> str:
    """
    Run an interactive file selector and return the chosen file path.

    The selector lists only the files directly contained in the provided folder. If `extensions` are supplied, only files with those extensions are shown. The user selects one file, and the full path is returned.

    Args:
        folder_path_in (str): The folder to scan for files. Must be a valid directory.
        extensions (tuple[str, ...] | None): Tuple of file extensions to filter by, e.g. (".csv", ".json"). If None or empty, all files are included.
        menu_title (str | None): Optional menu title (e.g., "Select Input File"). If None or empty, a default title is used.
        menu_prompt (str | None): Optional prompt text shown before user selection. If None or empty, a default prompt is used.

    Returns:
        str:
            Full file system path to the selected file.

    Raises:
        ValueError:
            - If the supplied folder path is not a valid directory.
            - If no files are available in the folder for the given filter.
    """
    # Validate and normalize the folder path first
    if not folder_path.is_folder_path(folder_path_in):
        raise ValueError(_ERR_INVALID_FOLDER_PATH.format(a=folder_path_in))

    normalized_folder = folder_path.normalize_folder_path(folder_path_in)

    # Convert tuple of extensions to list for file_path helper
    ext_list: list[str] | None
    if extensions:
        ext_list = list(extensions)
    else:
        ext_list = None

    # Retrieve the list of files in the folder (filtered if extensions given)
    try:
        file_names = list(file_path.get_files_in_folder(normalized_folder, ext_list))
    except (FileNotFoundError, NotADirectoryError, PermissionError) as err:
        # Wrap low-level exceptions into a ValueError for the caller
        raise ValueError(_ERR_INVALID_FOLDER_PATH.format(a=folder_path_in)) from err

    if not file_names:
        # No files available to select (either empty folder or filter too strict)
        raise ValueError(_ERR_NO_FILES_AVAILABLE.format(a=normalized_folder))

    file_names = sorted(file_names)

    # Resolve menu title and prompt, falling back to module defaults
    effective_title = menu_title or _DEFAULT_MENU_TITLE
    effective_prompt = menu_prompt or _DEFAULT_MENU_PROMPT

    # Build menu options (one line per file)
    menu_options: list[str] = file_names

    # Keep prompting until the user selects a valid file
    chosen_file_path = ""
    while True:
        # Prompt user for selection (indices are expected to be 0..len(files)-1)
        selected_index = cli.prompt_menu_selection(
            menu_options,
            effective_title,
            effective_prompt,
        )

        # Defensive guard: ensure index is within range
        if 0 <= selected_index < len(file_names):
            break
        else:
            # In case the CLI returns an invalid index, ask again
            continue

    chosen_file_name = file_names[selected_index]
    chosen_file_path = file_path.construct_file_path(normalized_folder, chosen_file_name)

    # Join folder and file into a full path
    return file_path.normalize_file_path(chosen_file_path)
