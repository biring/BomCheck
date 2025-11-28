"""
Utility functions for safe and minimal folder path operations.

This module provides reusable, stateless helpers for working with folder paths. It is designed for use across application layers, especially where low-level file operations are needed without business logic coupling.

Example Usage:
    # Preferred usage via public package interface:
    import src.utils as utils
    app_root = utils.find_root_folder()

    # Direct module usage (acceptable in unit tests or internal scripts only):
    import src.utils._folder_path as fp
    app_root = fp.find_root_folder()

Dependencies:
 - Python >= 3.8
 - Standard Library: os, sys, typing

Notes:
 - Assumes development environments organize source under a `src` folder
 - Automatically distinguishes between dev and packaged binary execution modes (e.g., PyInstaller)
 - All paths are normalized for cross-platform behavior

License:
 - Internal Use Only
"""

import os
import sys
from typing import Final

# CONSTANTS
SOURCE_CODE_FOLDER_NAME: Final = 'src'


def construct_folder_path(base_path: str, subfolders: tuple[str, ...]) -> str:
    """
    Constructs a fully normalized folder path from a base path and a sequence of sub folders.

    Each sub folder is joined in order to the base path using `os.path.join`. The final result is passed through `normalize_dir_path` to ensure consistent formatting across platforms, such as resolving redundant separators or adding a trailing slash if required.

    Args:
        base_path (str): The starting folder path.
        subfolders (tuple[str, ...]): A sequence of sub folder names to append to the base path.

    Returns:
        str: The final normalized folder path.
    """
    # Iteratively join each subfolder to the base path
    base_path = os.path.join(base_path, *subfolders)

    # Normalize the final path to ensure consistent formatting across platforms
    base_path = _normalize_folder_path(base_path)

    return base_path


def create_folder_if_missing(dir_path: str) -> bool:
    """
    Creates a folder at the specified path if it does not already exist.

    This function uses `os.makedirs` to create the folder and any necessary parent folders. It first checks whether the folder already exists. If creation fails, or if the folder still does not exist after the attempt, an `OSError` is raised.

    Args:
        dir_path (str): The full folder path to create.

    Returns:
        bool: True if the folder exists after the operation.

    Raises:
        OSError: If the folder cannot be created due to permission issues, invalid paths, or other filesystem-related errors.
    """

    # Skip creation if the folder already exists
    if is_folder_path(dir_path):
        # TODO f"Folder '{path}' exists before creation attempt.")
        return True

    try:
        # Try creating the folder and any necessary parent folders
        os.makedirs(dir_path, exist_ok=True)
    except OSError as e:
        # Raise error with context if creation fails
        raise OSError(
            f"Failed to create folder '{dir_path}'."
            f"\nReason: {e.strerror or str(e)}."
            f"\nPossible causes: invalid path, permission denied, or name conflict with a file."
        ) from e

    # Confirm folder now exists
    if not is_folder_path(dir_path):
        raise OSError(
            f"Folder '{dir_path}' does not exist after creation attempt."
            f"\nThis may indicate a race condition, a transient filesystem error, or permission issue."
        )

    return True


def is_folder_path(dir_path: str) -> bool:
    """
    Checks whether the specified path exists and is a folder.

    This function determines if the given path exists on the filesystem and refers to a folder. It returns False if the path does not exist or if it points to a file, symbolic link, or other non-folder object.

    Args:
        dir_path (str): The filesystem path to check.

    Returns:
        bool: True if the path exists and is a folder, False otherwise.
    """
    # Return True only if the path exists and is a folder
    return os.path.isdir(dir_path)


def _is_running_as_executable() -> bool:
    """
    Checks whether the application is running as a frozen executable.

    This is used to differentiate between development mode (executing Python source files) and production mode where the application is packaged as a standalone binary using tools like PyInstaller. These tools typically set the `sys.frozen` attribute.

    Returns:
        bool: True if the application is running as a frozen executable, False otherwise.
    """
    # Check if the 'frozen' attribute is set on the sys module (used by PyInstaller)
    return getattr(sys, 'frozen', False)


def list_immediate_sub_folders(folder_path: str) -> tuple[str, ...]:
    """
    Returns the names of all immediate sub folder within a given folder path.

    This function lists only the sub folders directly under the specified folder. It raises an error if the path does not exist or is not a folder.

    Args:
        folder_path (str): The folder path to scan for sub folders.

    Returns:
        tuple[str, ...]: A tuple containing the names of immediate sub folders.

    Raises:
        FileNotFoundError: If the path does not exist or is not a folder.
    """

    # Verify that the given path exists and is a folder
    if not is_folder_path(folder_path):
        raise FileNotFoundError(f"'{folder_path}' is not a valid folder")

    # List all entries (files and folders) in the folder
    all_entries = os.listdir(folder_path)

    # Keep only entries that are sub folders
    sub_dirs = [
        entry for entry in all_entries
        if os.path.isdir(os.path.join(folder_path, entry))
    ]

    # Return sub folder names as an immutable tuple
    return tuple(sub_dirs)


def _normalize_folder_path(raw_path: str) -> str:
    """
    Normalizes a filesystem path by expanding the home folder and simplifying the structure.

    This function expands user home references (e.g., `~`) and simplifies the path by resolving redundant components such as `.` (current folder), `..` (parent folder), and multiple separators. It does not verify whether the resulting path exists on the filesystem.

    Args:
        raw_path (str): A relative or absolute filesystem path to normalize.

    Returns:
        str: A normalized path with user expansion and cleaned structure.

    Raises:
        TypeError: If the input is not a string.
    """
    # Ensure the input is a string
    if not isinstance(raw_path, str):
        raise TypeError(f"Expected '{raw_path}' as a string path, but got type: " + type(raw_path).__name__)

    # Expand user folder symbols like ~ to full home path
    expanded_path = os.path.expanduser(raw_path)

    # Clean the path by removing redundant slashes, ".", and ".."
    normalized_path = os.path.normpath(expanded_path)

    return normalized_path


def find_root_folder() -> str:
    """
    Determines and returns the application's root folder based on the execution context.

    In a packaged (frozen) application, this function returns the folder containing the executable. In development mode, it returns the root of the source project. The returned path is normalized and absolute. An error is raised if the root cannot be resolved.

    Returns:
        str: Normalized absolute path to the application's root folder.

    Raises:
        FileNotFoundError: If the root folder cannot be resolved or does not exist.
    """
    try:
        # Determine resolution strategy based on packaging state
        if _is_running_as_executable():
            # Running from a frozen executable (e.g., PyInstaller)
            app_root_folder = _resolve_exe_folder()
        else:
            # Running from source (development mode)
            app_root_folder = _resolve_dev_folder()

        return app_root_folder

    except Exception as e:
        # Raise a more informative error if resolution fails
        raise FileNotFoundError(f"Unable to resolve application root folder: {e}") from e


def _resolve_dev_folder() -> str:
    """
    Resolves the project root folder when running in development mode.

    This function determines the root of the project by inspecting the location of the source file. If the `src` folder is part of the current path, it assumes the root is one level above it. The returned path is normalized and checked for existence.

    Returns:
        str: Normalized absolute path to the project root folder.

    Raises:
        FileNotFoundError: If the determined project root folder does not exist.
    """
    script_folder: str
    dev_folder: str

    # Get the absolute path of the current script's folder
    script_folder = os.path.dirname(__file__)

    # If the script resides in the source code folder, treat its parent as the root
    while SOURCE_CODE_FOLDER_NAME in script_folder:
        script_folder = os.path.split(script_folder)[0]

    # Normalize for consistent cross-platform behavior
    dev_folder = _normalize_folder_path(script_folder)

    # Verify the resolved path exists and is a folder
    if not is_folder_path(dev_folder):
        raise FileNotFoundError(f"Path = '{dev_folder}' is not a folder path")

    return dev_folder


def find_drive_letter() -> str:
    """
    Determines and returns the drive letter of the application root folder.

    This function resolves the application's root path using `_resolve_app_root()` and extracts the drive component (e.g., 'C:/') from it. It is designed for use on Windows systems where drive letters are required. On non-Windows platforms, a ValueError is raised.

    Returns:
        str: Normalized drive letter with a trailing slash (e.g., 'C:/').

    Raises:
        ValueError: If the function is called on a non-Windows platform or if the drive letter cannot be determined.
    """
    # Ensure the platform supports drive letters
    if os.name != "nt":
        raise ValueError("resolve_drive() is only supported on Windows systems.")

    # Extract the drive component from the resolved application root
    drive, _ = os.path.splitdrive(find_root_folder())

    # Validate that a drive letter was successfully found
    if not drive:
        raise ValueError(
            "Drive letter could not be determined from the application root path. "
            "Ensure the application is running on a Windows system with a valid root path."
        )

    # Normalize the drive path (e.g., 'C:/' instead of 'C:')
    return _normalize_folder_path(drive + os.sep)


def _resolve_exe_folder() -> str:
    """
    Retrieves the folder of the currently executing binary in frozen mode.

    This function returns the folder that contains the executable file when the application is packaged as a standalone binary (e.g., via PyInstaller). It normalizes the path for cross-platform compatibility and verifies that the resolved folder exists.

    Returns:
        str: Normalized absolute path to the executable's parent folder.

    Raises:
        FileNotFoundError: If the resolved path does not exist or is not a folder.
    """
    # Get the folder where the current executable resides
    exe_folder = os.path.dirname(sys.executable)

    # Normalize the path for consistent formatting across platforms
    normalized_exe_folder = _normalize_folder_path(exe_folder)

    # Confirm the resolved path exists and is a folder
    if not is_folder_path(normalized_exe_folder):
        raise FileNotFoundError(
            f"Executable folder '{normalized_exe_folder}' does not exist or is not a valid folder. "
            "This may indicate a packaging error or incorrect frozen execution context."
        )

    return normalized_exe_folder

def go_up_one_folder(path: str) -> str:
    """
    Returns the normalized parent folder of the given path.

    If the path is already at the filesystem root (e.g., 'C:\\' or '/'), the same root path is returned without raising an error.

    Args:
        path (str): The starting folder path.

    Returns:
        str: The normalized parent folder path, or the same path if already at root level.
    """
    normalized = _normalize_folder_path(path)
    parent = os.path.dirname(normalized)

    # If moving up doesn't change the path → we are already at root
    if parent == normalized:
        return normalized

    return _normalize_folder_path(parent)
