"""
Utility functions for safe and minimal file path operations.

This module provides reusable, stateless helpers for working with file paths. It is designed for use across application layers, especially where low-level file operations are needed without business logic coupling.

Example Usage:
    # Preferred usage via public package interface:
    from src.utils import file_path
    files = file_path.get_files_in_directory("configs", extensions=[".json"])

    # Direct module usage (acceptable in tests or internal scripts):
    import src.utils._file_path as file_path
    file_path.assert_filename_with_extension("data/input.txt", ".txt")

Dependencies:
 - Python >= 3.10
 - Standard Library: os, pathlib, typing

Notes:
    - This module assumes caller responsibility for input validation and higher-level error handling.
    - All functions are stateless and do not maintain any internal context.
    - Designed for cross-layer utility use, including in CLI tools, UI layers, and service/controllers.

License:
 - Internal Use Only
"""

__all__ = [
    "assert_filename_with_extension",
    "construct_file_path",
    "escape_backslashes",
    "get_files_in_folder",
    "is_file_path",
    "is_valid_windows_file_path",
    "normalize_file_path",
]

import os
from pathlib import Path
from typing import Optional


def assert_filename_with_extension(file_path: str, expected_ext: str) -> None:
    """
    Ensures that a file's name has exactly one dot and matches the required extension.

    This function validates that the filename portion of the provided path:
      - Contains exactly one dot, separating the name and extension.
      - Has an extension that exactly matches the specified `expected_ext`

    Args:
        file_path (str): Absolute or relative path to the file.
        expected_ext (str): Required file extension including the leading dot (e.g., ".txt").

    Returns:
        None: This function only validates the filename and raises exceptions for violations.

    Raises:
        ValueError: If validation cannot be completed due to errors
    """
    try:
        path_obj = Path(file_path)  # Convert string path to a Path object for easy name/suffix access
        file_name = path_obj.name  # Extract just the filename (without directories)
        file_ext = path_obj.suffix  # Extract the extension

        # Check that the filename contains exactly one dot
        if file_name.count(".") != 1:
            raise ValueError(f"Invalid filename '{file_name}': must contain exactly one dot.")

        # Validate the file extension matches the expected one (case-sensitive)
        if file_ext != expected_ext:
            raise ValueError(
                f"Invalid extension for '{file_name}': expected '{expected_ext}', got '{file_ext}'."
            )
    except Exception as err:
        # Wrap and raise a RuntimeError with the original exception details
        raise RuntimeError(
            f"Failed file name and extension check '{file_path}'\n"
            f"{type(err).__name__} - {err}"
        ) from err


def construct_file_path(folder: str, file: str) -> str:
    """
    Joins a folder path and file name into a full file system path.

    Strips leading/trailing whitespace from both inputs and combines them using the appropriate OS-specific separator.

    Args:
        folder (str): The folder portion of the path.
        file (str): The file name or relative file path to append.

    Returns:
        str: The combined full file path.

    Raises:
        ValueError: If either `folder` or `file` is empty or not a string.
    """
    if not isinstance(folder, str) or not folder.strip():
        raise ValueError("The folder path must be a non-empty string.")
    if not isinstance(file, str) or not file.strip():
        raise ValueError("The file name must be a non-empty string.")

    # Validate inputs and strip whitespace before joining paths
    full_path = os.path.join(folder.strip(), file.strip())

    return normalize_file_path(full_path)


def escape_backslashes(file_path: str) -> str:
    """
    Escapes backslashes in a file path for display or logging.

    Converts all single backslashes to double backslashes so the path
    resembles a raw string literal. Useful for logging or serialization on
    Windows systems where backslashes are common in paths.

    Args:
        file_path (str): The original file path string.

    Returns:
        str: The file path with all backslashes escaped.

    Raises:
        TypeError: If the input is not a string.
    """
    if not isinstance(file_path, str):
        raise TypeError(f"'{file_path}' is not a string.")

    # Replace single backslashes with double for safe string display/logging
    return file_path.replace("\\", "\\\\")


def get_files_in_folder(folder_path: str, extensions: Optional[list[str]] = None) -> tuple[str, ...]:
    """
    Lists immediate files in a folder, optionally filtering by extension.

    Scans the given folder and returns all non-folder files found at the top level. If `extensions` are provided, only files matching those extensions are included (case-insensitive).

    Args:
        folder_path (str): The folder path to scan for files.
        extensions (Optional[list[str]]): List of file extensions to filter by (e.g., ['.txt', '.csv']). If None or empty, all files are returned.

    Returns:
        tuple[str, ...]: Names of files directly inside the folder, optionally filtered.

    Raises:
        FileNotFoundError: If the specified folder does not exist.
        NotADirectoryError: If the given path is not a folder.
        PermissionError: If access to the folder is denied.
    """
    if not os.path.exists(folder_path):
        raise FileNotFoundError(f"The folder '{folder_path}' does not exist.")
    if not os.path.isdir(folder_path):
        raise NotADirectoryError(f"The path '{folder_path}' is not a folder.")

    # List all entries in the folder
    try:
        dir_entries = os.listdir(folder_path)
    except PermissionError as e:
        raise PermissionError(f"Permission denied for folder '{folder_path}'.") from e

    # Filter to include only files (ignore subdirectories)
    immediate_files = [
        entry for entry in dir_entries
        if os.path.isfile(os.path.join(folder_path, entry))
    ]

    # If extensions are specified, filter files by matching extensions
    if extensions:
        extensions = [ext.lower() for ext in extensions]  # Normalize extensions
        matched_files = [
            filename for filename in immediate_files
            if any(filename.lower().endswith(ext) for ext in extensions)
        ]
    else:
        matched_files = immediate_files

    return tuple(matched_files)


def is_file_path(file_path: str) -> bool:
    """
    Determines if a given file path exists and is a regular file.

    This function checks whether the specified filesystem path exists and refers to a regular file (not a folder, symbolic link, or special file type).

    Args:
        file_path (str): The absolute or relative path to check.

    Returns:
        bool: True if the path exists and is a regular file, False otherwise.

    Raises:
        TypeError: If file_path is not a string.
    """
    if not isinstance(file_path, str):
        raise TypeError("file_path must be a string.")

    # Check if the given path exists and refers to a regular file (not a folder or symlink)
    return os.path.isfile(file_path)


def is_valid_windows_file_path(name: str) -> bool:
    """
    Checks whether a given file path name contains only safe characters on Windows.

    This function validates that the name contains no invalid characters and does not match any reserved system names. On non-Windows platforms, it returns False.

    Args:
        name (str): The file path name to validate.

    Returns:
        bool: True if the name is valid on Windows, False otherwise.
    """
    # Windows forbidden characters (source: https://learn.microsoft.com/en-us/windows/win32/fileio/naming-a-file)
    windows_forbidden_chars = {'<', '>', ':', '"', '/', '\\', '|', '?', '*'}

    if not name or not isinstance(name, str):
        return False

    if os.name != 'nt':
        # This utility is Windows-specific
        return False

    if any(char in windows_forbidden_chars for char in name):
        return False

    return True

def normalize_file_path(raw_path: str) -> str:
    """
    Normalize a file path by stripping whitespace and resolving redundant separators, while preserving whether the path is relative or absolute.

    Args:
        raw_path (str): Any file path to normalize.

    Returns:
        str: Normalized file path with OS-native separators.

    Raises:
        TypeError: If path is not a string.
    """
    if not isinstance(raw_path, str):
        raise TypeError("Path must be a string.")

    # Trim leading/trailing whitespace
    cleaned = raw_path.strip()

    # Normalize separators and remove redundant components,
    # but keep relative/absolute semantics as-is.
    return os.path.normpath(cleaned)
