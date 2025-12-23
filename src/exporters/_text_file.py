"""
Internal helpers for writing UTF-8 text files to disk.

This module centralizes exporter-side logic to:
 - Validate destination folder paths
 - Construct and validate text file paths and extensions
 - Write line-oriented text output using shared text I/O utilities

It serves as a thin orchestration layer between exporters and low-level filesystem helpers.

Example Usage:
    # Preferred usage via exporter interfaces:
    # Not applicable; this module is internal.

    # Direct module usage (acceptable in unit tests or internal scripts only):
    from src.exporters import _text_file as tf
    tf.write_text_file_lines(folder, "output", lines)

Dependencies:
    - Python >= 3.10
    - Internal Packages:
        - src.utils.file_path
        - src.utils.folder_path
        - src.utils.text_io

Notes:
    - This module is internal to the exporters layer and not part of the public API.
    - Validation is delegated to shared path and I/O utilities.
    - All writes enforce UTF-8 encoding and explicit text file extensions.
    - Designed to fail fast with contextual RuntimeError messages.

License:
    - Internal Use Only
"""
__all__ = []  # Internal-only; not part of public API. Star imports from this module export nothing.

from ._dependencies import file_path, folder_path, text_io


def write_text_file_lines(folder: str, file_name: str, lines: tuple[str, ...], overwrite: bool = True) -> None:
    """
    Write a sequence of text lines to a file.

    Validates the destination folder, constructs and validates the output file path, enforces the expected text file extension, and writes the provided data using the shared text I/O helper.

    Args:
        folder (str): Absolute path to the destination folder.
        file_name (str): File name without extension.
        lines (tuple[str, ...]): Sequence of text lines to write.
        overwrite (bool, optional): If True, overwrite an existing file. Defaults to True.

    Returns:
        None

    Raises:
        RuntimeError: If validation fails or the file cannot be written.
    """

    try:
        # Ensure there is data to write
        if not lines:
            raise ValueError("No text data provided for writing.")

        # Ensure all lines are string data
        if not all(isinstance(line, str) for line in lines):
            raise TypeError("All text file lines must be strings.")

        # Validate destination folder exists and is accessible
        folder_path.assert_folder_path(folder)

        # Construct full output file path with enforced extension
        text_file_path = file_path.construct_file_path(folder, file_name + text_io.TEXT_FILE_TYPE)

        # Ensure the file has an allowed text extension
        file_path.assert_file_name(text_file_path, (text_io.TEXT_FILE_TYPE,))

        # Prevent accidental overwrite if overwrite is disabled
        if not overwrite and file_path.is_file_path(text_file_path):
            raise ValueError(f"Text file '{file_name}' already exists. Overwrite not allowed.")

        # Delegate actual disk write to shared text I/O utility
        write_data = "\n".join(lines)
        text_io.save_text_file(text_file_path, write_data)

        return

    except (TypeError, ValueError, RuntimeError) as e:
        raise RuntimeError(
            f"Failed to write text file '{file_name}' to folder '{folder}'.\n{e}"
        ) from e

    except Exception as e:
        raise RuntimeError(
            f"Unexpected error during write '{file_name}' text file to '{folder}'.\n{e}"
        ) from e
