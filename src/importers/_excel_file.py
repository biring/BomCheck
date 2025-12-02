"""
Helpers for loading Excel workbooks into pandas DataFrames with shared path validation and error handling.

This module centralizes the logic to:
 - Normalize and validate an input Excel file path before reading
 - Enforce the expected workbook extension defined by the shared excel_io utilities
 - Read all sheets into a dict of DataFrames while wrapping failures in a consistent RuntimeError contract

Example Usage:
    # Preferred usage via public package interface:
    from src.importers import excel_reader
    sheets = excel_reader.read_excel_as_dict("data/sample_workbook.xlsx")

    # Direct module usage (acceptable in unit tests or internal scripts only):
    from src.importers import _excel_reader as _excel_reader
    sheets = _excel_reader.read_excel_as_dict("data/sample_workbook.xlsx")

Dependencies:
    - Python >= 3.10
    - Standard Library: typing
    - External Packages: pandas

Notes:
    - This module is intended for internal use within the importers layer, sitting between controllers and src.utils.excel_io.
    - Callers should treat read_excel_as_dict as a thin, side-effect-free wrapper that normalizes the path, enforces the Excel file type, and delegates reading to excel_io.
    - All low-level I/O and engine selection remain owned by src.utils.excel_io; this module focuses on path handling and consistent error messages.

License:
    - Internal Use Only
"""

__all__ = []  # Internal-only; not part of public API. Star imports from this module export nothing.

import pandas as pd

from src.utils import file_path
from src.utils import excel_io


def read_excel_as_dict(excel_path: str) -> dict[str, pd.DataFrame]:
    """
    Read an Excel workbook from disk and return all sheets as a dict of DataFrames.

    This helper normalizes and validates the input path, enforces the expected Excel file extension, and delegates reading to the shared excel_io utilities. All failures are wrapped in a RuntimeError with a consistent message.

    Args:
        excel_path (str): Absolute or relative path to the source .xlsx file.

    Returns:
        dict[str, pd.DataFrame]: Mapping of sheet name to loaded DataFrame.

    Raises:
        RuntimeError: If the path is invalid, the file is not an Excel workbook, or reading the workbook fails for any reason.
    """
    try:
        # Normalize the given path into a Path object
        normalized_path = file_path.normalize_file_path(excel_path)

        # Enforce the expected Excel file extension (e.g., ".xlsx")
        file_path.assert_file_name(normalized_path, (excel_io.EXCEL_FILE_TYPE,))

        # Ensure the path refers to an existing regular file
        file_path.assert_file_path(normalized_path)

        # Delegate the actual read to the shared excel_io helper
        return excel_io.read_excel_file(normalized_path)

    except (TypeError, ValueError, RuntimeError) as e:
        raise RuntimeError(
            f"Failed to read Excel workbook '{excel_path}'.\n{e}"
        ) from e

    except Exception as e:
        raise RuntimeError(
            f"Unexpected error while reading Excel workbook '{excel_path}'.\n{e}"
        ) from e
