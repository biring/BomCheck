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

# noinspection PyProtectedMember
import src.utils._api as api


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


if __name__ == "__main__":
    unittest.main()
