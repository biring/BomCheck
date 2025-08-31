"""
Unit tests for the public `utils` package APIs.

This suite provides smoke-level coverage to ensure the top-level `utils` API behaves as expected. These tests validate that API-exposed functions delegate correctly to their implementations and return normalized results.

Example Usage (from project root):
    # Run this file:
    python -m unittest -v tests/utils/test__api.py

Dependencies:
    - Python >= 3.9
    - Standard Library: unittest, unittest.mock, tempfile, os
    - Third-party: pandas, openpyxl

Design Notes & Assumptions:
    - Tests are API-level only, not internal implementation details
    - Input/output validation is minimal; focus is on public contract correctness
    - Interactive functions (e.g., input prompts) are patched to avoid blocking
    - Temporary directories and files are used to ensure isolation and cleanup

License:
 - Internal Use Only
"""

import os
import tempfile
import unittest
from unittest.mock import patch

import pandas as pd

# noinspection PyProtectedMember
import src.utils._api as api


class TestConsole(unittest.TestCase):
    """
    Unit tests for the public API functions in the `utils._console` module.
    """

    def test_prompt_string_input(self):
        """
        Should run API function
        """
        # ARRANGE
        expected = "45"

        # Patch the API-level symbol, since we're testing the public API
        with patch("src.utils._api.prompt_string_input", return_value=expected) as mock_input:
            # ACT
            result = api.prompt_string_input("", "", "")

            # ASSERT
            with self.subTest(Out=result, Exp=expected):
                self.assertEqual(result, expected)
                mock_input.assert_called_once_with("", "", "")


class TestExcelIO(unittest.TestCase):
    """
    Unit tests for the public Excel I/O API functions exposed via `utils._api`
    """

    def setUp(self):
        """
        Create an isolated temp directory and write fixture workbooks once.
        """
        self.temp_dir = tempfile.mkdtemp(prefix="api_excel_")

        # Realistic sample data (strings, blanks preserved)
        self.name_one = "S1"
        self.df_one = pd.DataFrame({
            "Part": ["R1", "C2", "$"],
            "Qty": ["10", "5", "0"],
            "Cost": ["0.01", "0.03", "n"],
        })
        self.name_two = "S2"
        self.df_two = pd.DataFrame({
            "α": ["1", "2"],
            "β": ["A", "T"],
        })
        self.name_three = "S3"
        self.df_three = pd.DataFrame({"ColA": ["x", "y", "z"]})

        # Paths
        self.single_path = os.path.join(self.temp_dir, "single.xlsx")
        self.multi_path = os.path.join(self.temp_dir, "multi.xlsx")

        # Write fixtures
        with pd.ExcelWriter(self.single_path, engine="openpyxl") as writer:
            self.df_one.to_excel(writer, sheet_name=self.name_one, index=False)
        with pd.ExcelWriter(self.multi_path, engine="openpyxl") as writer:
            self.df_two.to_excel(writer, sheet_name=self.name_two, index=False)
            self.df_three.to_excel(writer, sheet_name=self.name_three, index=False)
            self.df_one.to_excel(writer, sheet_name=self.name_one, index=False)

    def tearDown(self):
        """
        Remove all files/directories created in setUp() and during tests.
        """
        for root, dirs, files in os.walk(self.temp_dir, topdown=False):
            for f in files:
                try:
                    os.remove(os.path.join(root, f))
                except FileNotFoundError:
                    pass
            for d in dirs:
                try:
                    os.rmdir(os.path.join(root, d))
                except OSError:
                    pass
        try:
            os.rmdir(self.temp_dir)
        except OSError:
            pass

    def test_map_excel_sheets_to_string_dataframes(self):
        """
        Should run API function
        """
        # ARRANGE
        # Expected raw data by sheet (will compare after string-conversion)
        expected = {
            self.name_two: self.df_two,
            self.name_three: self.df_three,
            self.name_one: self.df_one,
        }

        # ACT
        # Open as ExcelFile and pass the *open workbook* into the function
        with pd.ExcelFile(self.multi_path, engine="openpyxl") as workbook:
            result = api.map_excel_sheets_to_string_dataframes(workbook)

        # ASSERT
        # Compare keys (sheet names) and flattened values as strings
        for (result_key, result_value), (expected_key, expected_value) in zip(result.items(),
                                                                              expected.items()):
            with self.subTest(Out=result_key, Exp=expected_key):
                self.assertEqual(result_key, expected_key)
            # Flatten and compare all values cell-by-cell as strings
            flat_result_value = result_value.to_numpy().flatten().tolist()
            flat_expected_value = pd.DataFrame(expected_value).to_numpy().flatten().astype(
                str).tolist()
            for result, expected in zip(flat_result_value, flat_expected_value):
                with self.subTest(Out=result, Exp=expected):
                    self.assertEqual(result, expected)

    def test_reads_excel_file(self):
        """
        Should run API function
        """
        # ARRANGE
        expected = {
            self.name_two: self.df_two,
            self.name_three: self.df_three,
            self.name_one: self.df_one,
        }

        # ACT
        # Call the function under test
        result = api.read_excel_file(self.multi_path)

        # ASSERT
        # Compare keys (sheet names) and flattened values as strings
        for (result_key, result_value), (expected_key, expected_value) in zip(result.items(),
                                                                              expected.items()):
            with self.subTest("Sheet Name", Out=result_key, Exp=expected_key):
                self.assertEqual(result_key, expected_key)

                # Flatten and compare all values cell-by-cell as strings
                flat_result_value = result_value.to_numpy().flatten().tolist()
                flat_expected_value = pd.DataFrame(expected_value).to_numpy().flatten().astype(
                    str).tolist()
                for result, expected in zip(flat_result_value, flat_expected_value):
                    with self.subTest("Cell Value" , Out=result, Exp=expected):
                        self.assertEqual(result, expected)

    def test_sanitize_sheet_names_for_excel(self):
        """
        Should run API function
        """
        # ARRANGE
        test_cases = [
            # (Input, Expected)
            ("ValidName", "ValidName"),
            ("Mix:Of/All?*Chars[Here]", "MixOfAllCharsHere"),
        ]

        for input_val, expected in test_cases:
            # ACT
            result = api.sanitize_sheet_name_for_excel(input_val)

            # ASSERT
            with self.subTest(In=input_val, Out=result, Exp=expected):
                self.assertEqual(result, expected)

    def test_write_frame_to_excel(self):
        """
        Should run API function
        """
        # ARRANGE
        out_path = os.path.join(self.temp_dir, "bom.xlsx")
        expected_columns = list(self.df_one.columns)  # index should NOT be written as a column

        # ACT
        # Execute the function under test
        api.write_frame_to_excel(out_path, self.df_one)

        # Read the file back to validate outcomes (independent verification)
        with (pd.ExcelFile(out_path, engine="openpyxl") as workbook):
            read_back = pd.read_excel(workbook)

        # ASSERT
        # 1) File existence
        exists = os.path.exists(out_path)
        with self.subTest("File Exists", Out=exists, Exp=True):
            self.assertTrue(exists)

        # 2) Column headers should match original (no index column present)
        with self.subTest("Header", Out=list(read_back.columns), Exp=expected_columns):
            self.assertEqual(list(read_back.columns), expected_columns)

        # 3) Row count should match
        with self.subTest("Row count", Out=len(read_back), Exp=len(self.df_one)):
            self.assertEqual(len(read_back), len(self.df_one))

        # 4) Cell-by-cell content equality
        # Flatten and compare all values cell-by-cell as strings
        result_value = read_back.astype(str).values
        expected_value = self.df_one.astype(str).values
        flat_result_value = result_value.flatten().tolist()
        flat_expected_value = pd.DataFrame(expected_value).to_numpy().flatten().astype(str).tolist()
        for result, expected in zip(flat_result_value, flat_expected_value):
            with self.subTest("Cell value", Out=result, Exp=expected):
                self.assertEqual(result, expected)

    def test_writes_sheets_to_excel(self):
        """
        Should run API function
        """
        # ARRANGE
        out_path = os.path.join(self.temp_dir, "write_multi.xlsx")

        sheets = {
            self.name_one: self.df_one,
            self.name_two: self.df_two,
            self.name_three: self.df_three,
        }

        expected = sheets

        # ACT
        api.write_sheets_to_excel(out_path, sheets, overwrite=False)

        # ASSERT: file exists
        exists = os.path.isfile(out_path)
        with self.subTest("File Exist", Out=exists, Exp=True):
            self.assertTrue(exists)

        # ASSERT: verify sheet names and data via round-trip
        with pd.ExcelFile(out_path, engine="openpyxl") as xls:
            actual_sheet_names = tuple(xls.sheet_names)
            expected_sheet_names = tuple(expected.keys())

            with self.subTest("Sheet Name", Out=actual_sheet_names, Exp=expected_sheet_names):
                self.assertEqual(actual_sheet_names, expected_sheet_names)

            # Validate each sheet’s content
            for sheet_name, expected_df in expected.items():
                with pd.ExcelFile(out_path, engine="openpyxl") as workbook:
                    read_df = pd.read_excel(
                        workbook,
                        sheet_name=sheet_name,
                        dtype=str,  # Force all cells to be strings
                        # na_filter=False  # Keep blanks as empty strings instead of NaN
                    )

                equal = read_df.equals(expected_df)

                with self.subTest("Data frame", Sheet=sheet_name, Out=equal, Exp=True):
                    self.assertTrue(equal)


class TestFilePath(unittest.TestCase):
    """
    Unit tests for the public API functions in the `utils._file_path` module.
    """

    def test_assert_filename_with_extension(self):
        """
        Should run API function
        """
        # ARRANGE
        path_list = ["C:/logs/report.txt", "/var/tmp/config.json", "archive.data.txt"]
        expected_list = [None, RuntimeError.__name__, RuntimeError.__name__]

        for path, expected in zip(path_list, expected_list):

            # ACT
            try:
                api.assert_filename_with_extension(path, ".txt")
                result = None
            except Exception as e:
                result = type(e).__name__

            # ASSERT
            with self.subTest(Out=result, Exp=expected):
                self.assertEqual(result, expected)

    def test_build_file_path(self):
        """
        Should run API function
        """
        # ARRANGE
        folder_list = ["  /home/user  ", "", ""]
        file_list = ["  notes.txt  ", "", ""]
        expected_list = [os.path.join("/home/user", "notes.txt"), ValueError.__name__,
                         ValueError.__name__]

        for folder, file, expected in zip(folder_list, file_list, expected_list):
            # ACT
            try:
                result = api.build_file_path(folder, file)
            except Exception as e:
                result = type(e).__name__

            # ASSERT
            with self.subTest(Out=result, Exp=expected):
                self.assertEqual(result, expected)

    def test_doubles_backslashes(self):
        """
        Should run API function
        """
        # ARRANGE
        path_list = [r"C:\Users\Public\file.txt", 123, ]
        expected_list = ["C:\\\\Users\\\\Public\\\\file.txt", TypeError.__name__, ]

        for path, expected in zip(path_list, expected_list):
            # ACT
            try:
                result = api.escape_backslashes(path)  # type: ignore[arg-type]
            except Exception as e:
                result = type(e).__name__

            # ASSERT
            with self.subTest(Out=result, Exp=expected):
                self.assertEqual(result, expected)

    def test_get_files_in_directory(self):
        """
        Should run API function
        """

        # SET UP
        # Create a temporary directory structure
        self.temp_dir = tempfile.mkdtemp(prefix="api_fp_")

        try:
            # Files at top level
            self.f_txt = os.path.join(self.temp_dir, "readme.TXT")
            self.f_csv = os.path.join(self.temp_dir, "data.csv")
            self.f_json = os.path.join(self.temp_dir, "config.json")
            with open(self.f_txt, "w", encoding="utf-8"):
                pass
            with open(self.f_csv, "w", encoding="utf-8"):
                pass
            with open(self.f_json, "w", encoding="utf-8"):
                pass
            # Subdirectory (should be ignored)
            os.mkdir(os.path.join(self.temp_dir, "subdir"))

            # ARRANGE
            missing_folder = os.path.join(self.temp_dir, "does_not_exist")
            folder_list = [self.temp_dir, self.temp_dir, missing_folder, ]
            extension_list = [None, [".txt", ".JSON"], None, ]
            expected_list = [{"readme.TXT", "data.csv", "config.json"},
                             {"readme.TXT", "config.json"}, FileNotFoundError.__name__]

            for folder, extension, expected_set in zip(folder_list, extension_list, expected_list):

                # ACT
                try:
                    result_set = set(api.get_files_in_directory(folder, extension))
                except Exception as e:
                    result_set = type(e).__name__

                # ASSERT
                with self.subTest(Out=result_set, Exp=expected_set):
                    self.assertEqual(result_set, expected_set)

        finally:
            # TEAR DOWN (always runs even if assertions fail)
            for root, dirs, files in os.walk(self.temp_dir, topdown=False):
                for name in files:
                    os.remove(os.path.join(root, name))
                for name in dirs:
                    os.rmdir(os.path.join(root, name))
            os.rmdir(self.temp_dir)

    def test_is_existing_file_path(self):
        """
        Should run API function
        """
        # SETUP: create a real file and guarantee cleanup
        with tempfile.NamedTemporaryFile(prefix="api_fp_file_", delete=False) as tmp:
            existing = tmp.name
        self.addCleanup(lambda: os.path.exists(existing) and os.unlink(existing))

        # Use an isolated temp directory for the “missing” path
        with tempfile.TemporaryDirectory(prefix="api_fp_dir_") as tdir:
            missing = os.path.join(tdir, "nope_does_not_exist.xyz")

            # ARRANGE
            cases = [(existing, True), (missing, False), (123, TypeError.__name__)]

            for path, expected in cases:
                # ACT
                try:
                    result = api.is_existing_file_path(path)
                except Exception as e:
                    result = type(e).__name__

                # ASSERT
                with self.subTest(Out=result, Exp=expected):
                    self.assertEqual(result, expected)

    def test_is_valid_file_path(self):
        """
        Should run API function
        """
        # ARRANGE
        # Choose a name that is valid on Windows (no forbidden characters, not reserved)
        good_name = "Report_2025_Q4-final.txt"
        bad_name = "bad:name?.txt"

        file_path_list = [good_name, bad_name, 123]
        expected_list = [True, False, False]

        for file_path, expected in zip(file_path_list, expected_list):
            # ACT
            result = api.is_valid_file_path(file_path)

            # ASSERT
            with self.subTest(Out=result, Exp=expected):
                self.assertEqual(result, expected)


class TestParser(unittest.TestCase):
    """
    Unit tests for the public API functions in the `utils._parser` module.
    """

    def test_is_float(self):
        """
        Should run API function
        """
        # ARRANGE
        input_list = ["3.147", "A"]
        expected_list = [True, False]

        for input_str, expected in zip(input_list, expected_list):
            # ACT
            result = api.is_float(input_str)

            # ASSERT
            with self.subTest(In=input_str, Out=result, Exp=expected):
                self.assertEqual(result, expected)

    def test_is_integer(self):
        """
        Should run API function
        """
        # ARRANGE
        input_list = ["7", "3.7"]
        expected_list = [True, False]

        for input_str, expected in zip(input_list, expected_list):
            # ACT
            result = api.is_integer(input_str)

            # ASSERT
            with self.subTest(In=input_str, Out=result, Exp=expected):
                self.assertEqual(result, expected)

    def test_is_non_empty_string(self):
        """
        Should run API function
        """
        # ARRANGE
        input_list = ["Hello", ""]
        expected_list = [True, False]

        for input_str, expected in zip(input_list, expected_list):
            # ACT
            result = api.is_non_empty_string(input_str)

            # ASSERT
            with self.subTest(In=input_str, Out=result, Exp=expected):
                self.assertEqual(result, expected)

    def test_is_strict_empty_string(self):
        """
        Should run API function
        """
        # ARRANGE
        input_list = ["", "3.7"]
        expected_list = [True, False]

        for input_str, expected in zip(input_list, expected_list):
            # ACT
            result = api.is_strict_empty_string(input_str)

            # ASSERT
            with self.subTest(In=input_str, Out=result, Exp=expected):
                self.assertEqual(result, expected)

    def test_is_valid_date_string(self):
        """
        Should run API function
        """
        # ARRANGE
        input_list = ["12/10/2025", "2025/10/10"]
        expected_list = [True, False]

        for input_str, expected in zip(input_list, expected_list):
            # ACT
            result = api.is_valid_date_string(input_str)

            # ASSERT
            with self.subTest(In=input_str, Out=result, Exp=expected):
                self.assertEqual(result, expected)

    def test_parse_to_empty_string(self):
        """
        Should run API function
        """
        # ARRANGE
        input_list = ["", "a"]
        expected_list = ["", ValueError.__name__]

        for input_str, expected in zip(input_list, expected_list):
            # ACT
            try:
                result = api.parse_to_empty_string(input_str)
            except Exception as e:
                result = type(e).__name__
            # ASSERT
            with self.subTest(In=input_str, Out=result, Exp=expected):
                self.assertEqual(result, expected)

    def test_parse_to_float(self):
        """
        Should run API function
        """
        # ARRANGE
        input_list = ["22.2", "a"]
        expected_list = [22.2, ValueError.__name__]

        for input_str, expected in zip(input_list, expected_list):
            # ACT
            try:
                result = api.parse_to_float(input_str)
            except Exception as e:
                result = type(e).__name__
            # ASSERT
            with self.subTest(In=input_str, Out=result, Exp=expected):
                self.assertEqual(result, expected)

    def test_parse_to_integer(self):
        """
        Should run API function
        """
        # ARRANGE
        input_list = ["22", "a"]
        expected_list = [22, ValueError.__name__]

        for input_str, expected in zip(input_list, expected_list):
            # ACT
            try:
                result = api.parse_to_integer(input_str)
            except Exception as e:
                result = type(e).__name__
            # ASSERT
            with self.subTest(In=input_str, Out=result, Exp=expected):
                self.assertEqual(result, expected)

    def test_parse_to_iso_date_string(self):
        """
        Should run API function
        """
        # ARRANGE
        input_list = ["12/10/2025", "2025/10/10"]
        expected_list = ["2025-10-12", ValueError.__name__]

        for input_str, expected in zip(input_list, expected_list):
            # ACT
            try:
                result = api.parse_to_iso_date_string(input_str)
            except Exception as e:
                result = type(e).__name__
            # ASSERT
            with self.subTest(In=input_str, Out=result, Exp=expected):
                self.assertEqual(result, expected)

    def test_parse_to_non_empty_string(self):
        """
        Should run API function
        """
        # ARRANGE
        input_list = ["Hello", ""]
        expected_list = ["Hello", ValueError.__name__]

        for input_str, expected in zip(input_list, expected_list):
            # ACT
            try:
                result = api.parse_to_non_empty_string(input_str)
            except Exception as e:
                result = type(e).__name__
            # ASSERT
            with self.subTest(In=input_str, Out=result, Exp=expected):
                self.assertEqual(result, expected)


class TestSanitizer(unittest.TestCase):
    """
    Unit tests for the public API functions in the `utils._sanitizer` module.
    """

    def test_normalize_spaces(self):
        """
        Should run API function
        """
        # ARRANGE
        input_str = " A  B "
        expected = "A B"

        # ACT
        result = api.normalize_spaces(input_str)

        # ASSERT
        with self.subTest(Out=result, Exp=expected):
            self.assertEqual(result, expected)

    def test_normalize_to_string(self):
        """
        Should run API function
        """
        # ARRANGE
        input_int = 123
        expected = "123"

        # ACT
        result = api.normalize_to_string(input_int)

        # ASSERT
        with self.subTest(Out=result, Exp=expected):
            self.assertEqual(result, expected)

    def test_remove_all_whitespaces(self):
        """
        Should run API function
        """
        # ARRANGE
        input_str = "A B\tC\nD\rE\fF\vG"
        expected = "ABCDEFG"

        # ACT
        result = api.remove_all_whitespace(input_str)

        # ASSERT
        with self.subTest(Out=result, Exp=expected):
            self.assertEqual(result, expected)


class TestTextIO(unittest.TestCase):
    """
    Unit tests for the public API functions in the `utils._text_io` module.
    """

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp(prefix="api_textio")

    def tearDown(self):
        for root, dirs, files in os.walk(self.temp_dir, topdown=False):
            for name in files:
                os.remove(os.path.join(root, name))
            for name in dirs:
                os.rmdir(os.path.join(root, name))
        os.rmdir(self.temp_dir)

    def test_save_text_file(self):
        """
        Should run API function
        """
        # ARRANGE
        path = os.path.join(self.temp_dir, "hello.txt")
        content = "Hello\tUTF-8 ✓ — line one 🌟"
        expected_size = len(content.encode("utf-8"))

        # ACT
        api.save_text_file(path, content)

        # ASSERT
        self.assertTrue(os.path.isfile(path))
        actual_size = os.path.getsize(path)
        with self.subTest(Out=actual_size, Exp=expected_size):
            self.assertEqual(actual_size, expected_size)

    def test_save_text_file_raise(self):
        """
        Should raise when file path is a folder path.
        """
        # ARRANGE
        bad_path = os.path.join(self.temp_dir, "not_a_file")
        os.mkdir(bad_path)
        expected = RuntimeError.__name__

        # ACT
        try:
            api.save_text_file(bad_path, "content")
            result = ""
        except Exception as e:
            result = type(e).__name__

        # ASSERT
        with self.subTest(Out=result, Exp=expected):
            self.assertEqual(result, expected)

    def test_load_text_file(self):
        """
        Should run API function
        """
        # ARRANGE
        path = os.path.join(self.temp_dir, "hello.txt")
        expected = "Hello\nUTF-8 ✓ load file data 🌟"
        with open(path, "w", encoding="utf-8", newline="") as f:
            f.write(expected)

        # ACT
        actual = api.load_text_file(path)

        # ASSERT
        with self.subTest(Out=actual, Exp=expected):
            self.assertEqual(actual, expected)

    def test_load_text_file_raise(self):
        """
        Should raise error when file does not exist.
        """
        # ARRANGE
        missing = os.path.join(self.temp_dir, "does_not_exist.txt")
        expected = RuntimeError.__name__

        # ACT
        try:
            api.load_text_file(missing)
            result = ""
        except Exception as e:
            result = type(e).__name__

        # ASSERT
        with self.subTest(Out=result, Exp=expected):
            self.assertEqual(result, expected)


if __name__ == "__main__":
    unittest.main()
