"""
Unit tests for the internal Excel loader helper `read_excel_as_dict`.

This module validates that the loader:
    - Successfully reads a real .xlsx workbook into a dict[str, DataFrame]
    - Preserves sheet names and DataFrame shapes
    - Raises RuntimeError for missing files, wrong extensions, or invalid filenames
    - Ensures filename structure rules (exactly one dot before extension)

Example Usage:
    # Preferred usage via project-root invocation:
    python -m unittest tests/importers/test__excel_file.py

    # Direct discovery (runs all tests):
    python -m unittest discover -s tests

Dependencies:
    - Python >= 3.10
    - Standard Library: unittest, tempfile, shutil, os
    - External Packages: pandas

Notes:
    - Tests treat the loader as a pure wrapper that normalizes paths, enforces extension rules, and delegates Excel I/O to the underlying excel_io utilities.
    - Real temp Excel workbooks are created to validate end-to-end behavior.
    - Tests compare sheet names, DataFrame types, and basic shapes only—content comparison is intentionally minimal.

License:
    - Internal Use Only
"""

import os
import shutil
import tempfile
import unittest

import pandas as pd

# noinspection PyProtectedMember
from src.importers import _excel_file as excel_file


class TestReadExcelAsDict(unittest.TestCase):
    """
    Unit tests for the `read_excel_as_dict` Excel loader helper.
    """

    def setUp(self):
        """
        Create a temporary folder and a real Excel workbook for testing.
        """
        # ARRANGE (common for tests)
        self.file_name = "sample_workbook.xlsx"
        # Create a temporary directory to hold the test Excel file
        self.temp_dir = tempfile.mkdtemp(prefix="excel_load_test_")

        # Full path to the temporary Excel file
        self.excel_path = os.path.join(self.temp_dir, self.file_name)

        # Build realistic sample DataFrames for multiple sheets.
        sheet1_df = pd.DataFrame(
            {
                "Item": [1, 2, 3],
                "Description": ["Resistor", "Capacitor", "Inductor"],
                "Qty": [10, 20, 30],
                "Price": [1.56, 0.67, 99.89],
            }
        )
        sheet2_df = pd.DataFrame(
            {
                "PartNumber": ["R1", "C1", "L1"],
                "Value": ["10k", "1uF", "10uH"],
            }
        )

        # Store expected sheet data for later comparison in tests
        self.expected_sheets: dict[str, pd.DataFrame] = {
            "BOM": sheet1_df,
            "Details": sheet2_df,
        }

        # Create a real Excel workbook on disk
        with pd.ExcelWriter(self.excel_path) as writer:
            sheet1_df.to_excel(writer, sheet_name="BOM", index=False)
            sheet2_df.to_excel(writer, sheet_name="Details", index=False)

    def tearDown(self):
        """
        Remove the temporary directory and all created files.
        """
        if os.path.isdir(self.temp_dir):
            shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_happy_path(self):
        """
        Should load a valid Excel file and return a dict of DataFrames keyed by sheet name.
        """
        # ARRANGE
        folder_path = self.temp_dir
        file_name = self.file_name
        expected_result = set(self.expected_sheets.keys())

        # ACT
        actual_result = excel_file.read_excel_as_dict(folder_path,file_name)
        actual_sheet_names = set(actual_result.keys())

        # ASSERT
        with self.subTest("Result type", Out=type(actual_result).__name__, Exp="dict"):
            self.assertIsInstance(actual_result, dict)

        with self.subTest("Sheet name", Out=actual_sheet_names, Exp=expected_result, ):
            self.assertEqual(actual_sheet_names, expected_result)

        for sheet_name, expected_df in self.expected_sheets.items():
            result_df = actual_result[sheet_name]

            with self.subTest("Data type", Out=type(result_df).__name__, Exp=pd.DataFrame.__name__):
                self.assertIsInstance(result_df, pd.DataFrame)

            with self.subTest("Data size", Out=result_df.shape, Exp=expected_df.shape):
                self.assertEqual(result_df.shape, expected_df.shape)

    def test_raise_for_missing_file(self):
        """
        Should raise an error when the file is missing.
        """
        # ARRANGE
        folder_path = self.temp_dir
        missing_file_name = "does_not_exist.xlsx"
        expected = RuntimeError.__name__

        # ACT
        try:
            excel_file.read_excel_as_dict(folder_path, missing_file_name)
            actual = ""
        except Exception as exc:
            actual = type(exc).__name__

        # ASSERT
        with self.subTest(Out=actual, Exp=expected):
            self.assertEqual(actual, expected)

    def test_raise_for_wrong_extension(self):
        """
        Should raise an error when the file does not have .xlsx extension.
        """
        # ARRANGE
        folder_path = self.temp_dir
        bad_file_name_extension = "not_excel.txt"
        bad_path = os.path.join(folder_path, bad_file_name_extension)
        with open(bad_path, "w") as f:
            f.write("not an excel file")

        expected = RuntimeError.__name__

        # ACT
        try:
            excel_file.read_excel_as_dict(folder_path, bad_file_name_extension)
            actual = ""
        except Exception as exc:
            actual = type(exc).__name__

        # ASSERT
        with self.subTest(Out=actual, Exp=expected):
            self.assertEqual(actual, expected)

    def test_raise_for_multiple_dots_in_filename(self):
        """
        Should raise an error when the filename contains more than one dot.
        """
        # ARRANGE
        folder_path = self.temp_dir
        bad_file_name = "two.dot.name.xlsx"
        bad_path = os.path.join(folder_path, bad_file_name)

        # Create a valid Excel file but with invalid filename structure
        df = pd.DataFrame({"A": [1, 2, 3]})
        with pd.ExcelWriter(bad_path) as writer:
            df.to_excel(writer, index=False)

        expected = RuntimeError.__name__

        # ACT
        try:
            excel_file.read_excel_as_dict(folder_path, bad_file_name)
            actual = ""
        except Exception as exc:
            actual = type(exc).__name__

        # ASSERT
        with self.subTest(Out=actual, Exp=expected):
            self.assertEqual(actual, expected)


if __name__ == "__main__":
    unittest.main()
