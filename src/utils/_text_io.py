"""
Public utilities for reading and writing UTF-8 encoded text files.

This module provides minimal, safe wrappers around Python's file I/O:
 - Read entire text files into strings
 - Write text content to disk with explicit UTF-8 encoding
 - Surface clearer error messages while preserving underlying exceptions

Example Usage:
    # Preferred usage through the public utils namespace:
    from src.utils import text_io
    text_io.save_text_file("notes.txt", "Hello World")
    text = text_io.load_text_file("notes.txt")

    # Direct module usage in unit tests:
    import src.utils._text_io as text_io
    content = text_io.load_text_file("sample.txt")

Dependencies:
    - Python >= 3.9
    - Standard Library: builtins (open), io

Notes:
    - Functions overwrite existing file content; no append mode is provided.
    - All operations use UTF-8 encoding; binary file reading/writing is not supported here.
    - Designed for use in internal tooling, data preprocessing, and small-scale file persistence.

License:
 - Internal Use Only
"""

__all__ = [
    "TEXT_FILE_TYPE",
    "load_text_file",
    "save_text_file",
]

# CONSTANTS
TEXT_FILE_TYPE = ".txt"


def save_text_file(file_path: str, text_content: str) -> None:
    """
    Writes the given text content to a file using UTF-8 encoding.

    Opens (or creates) the file in write mode, replacing any existing content. Raises a descriptive error if the file cannot be created, opened, or written.

    Args:
        file_path (str): Absolute or relative path to the target file.
        text_content (str): Text content to be written into the file.

    Returns:
        None

    Raises:
        RuntimeError: If the file cannot be opened or written for any reason.
    """
    try:
        # Open the file in write mode (overwrites existing content)
        with open(file_path, mode="w", encoding="utf-8") as f:
            # Write the provided text content into the file
            f.write(text_content)
    except Exception as err:
        # Wrap the original error with more context for easier debugging
        raise RuntimeError(
            f"Failed to write text file at '{file_path}'\n"
            f"{type(err).__name__} - {err}"
        ) from err


def load_text_file(file_path: str) -> str:
    """
    Reads the entire contents of a text file and returns it as a string.

    Opens the file in read-only mode using UTF-8 encoding and retrieves its complete contents. This function raises a descriptive error if the file cannot be read, including details about the underlying exception.

    Args:
        file_path (str): Absolute or relative path to the text file.

    Returns:
        str: Entire content of the file as a single string.

    Raises:
        RuntimeError: If the file cannot be opened or read for any reason.
    """
    try:
        # Open the file with UTF-8 encoding for consistent text handling
        with open(file_path, mode="r", encoding="utf-8") as f:
            # Read and return the entire file content
            return f.read()
    except Exception as err:
        # Wrap and raise a RuntimeError with the original exception details
        raise RuntimeError(
            f"Failed to read text file from '{file_path}'\n"
            f"{type(err).__name__} - {err}"
        ) from err
