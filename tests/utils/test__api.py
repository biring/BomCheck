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
import json
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
                    with self.subTest("Cell Value", Out=result, Exp=expected):
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


class TestFolderPath(unittest.TestCase):
    """
    Unit tests for the public API functions in the `utils._folder_path` module.
    """

    def setUp(self):
        """
        Create a temporary directory tree for testing folder utilities.
        """
        self.temp_dir = tempfile.mkdtemp(prefix="api_folder_")
        self.sub_a = os.path.join(self.temp_dir, "A")
        self.sub_b = os.path.join(self.temp_dir, "B")
        os.makedirs(self.sub_a, exist_ok=True)
        os.makedirs(self.sub_b, exist_ok=True)

    def tearDown(self):
        """
        Clean up all directories created for tests.
        """
        for root, dirs, files in os.walk(self.temp_dir, topdown=False):
            for name in files:
                os.remove(os.path.join(root, name))
            for name in dirs:
                os.rmdir(os.path.join(root, name))
        os.rmdir(self.temp_dir)

    def test_construct_folder_path(self):
        """
        Should join subfolders to base path and normalize the result.
        """
        # ARRANGE
        base = self.temp_dir
        subs = ("x", "y", "z")
        expected = os.path.normpath(os.path.join(base, *subs))

        # ACT
        result = api.construct_folder_path(base, subs)

        # ASSERT
        with self.subTest(Out=result, Exp=expected):
            self.assertEqual(result, expected)

    def test_create_folder_if_missing(self):
        """
        Should create a folder if missing and return True.
        """
        # ARRANGE
        new_dir = os.path.join(self.temp_dir, "new_folder")
        exists_before = os.path.isdir(new_dir)

        # ACT
        result = api.create_folder_if_missing(new_dir)
        exists_after = os.path.isdir(new_dir)

        # ASSERT
        with self.subTest("Pre-existence", Out=exists_before, Exp=False):
            self.assertFalse(exists_before)
        with self.subTest("Result", Out=result, Exp=True):
            self.assertTrue(result)
        with self.subTest("Existence after", Out=exists_after, Exp=True):
            self.assertTrue(exists_after)

    def test_create_folder_if_missing_existing(self):
        """
        Should return True when folder already exists.
        """
        # ARRANGE
        os.makedirs(self.sub_a, exist_ok=True)

        # ACT
        result = api.create_folder_if_missing(self.sub_a)

        # ASSERT
        with self.subTest(Out=result, Exp=True):
            self.assertTrue(result)

    def test_is_folder_path(self):
        """
        Should return True for folders and False otherwise.
        """
        # ARRANGE
        file_path = os.path.join(self.temp_dir, "file.txt")
        with open(file_path, "w", encoding="utf-8") as f:
            f.write("x")

        test_cases = [(self.temp_dir, True), (file_path, False), ("nope", False)]

        # ACT + ASSERT
        for path, expected in test_cases:
            result = api.is_folder_path(path)
            with self.subTest(Out=result, Exp=expected):
                self.assertEqual(result, expected)

    def test_list_immediate_sub_folders(self):
        """
        Should list only direct subfolders and raise for invalid path.
        """
        # ARRANGE
        expected = {"A", "B"}

        # ACT
        result = set(api.list_immediate_sub_folders(self.temp_dir))

        # ASSERT
        with self.subTest(Out=result, Exp=expected):
            self.assertEqual(result, expected)

        # INVALID path should raise
        bad_path = os.path.join(self.temp_dir, "no_folder_here")
        expected_error = FileNotFoundError.__name__
        try:
            api.list_immediate_sub_folders(bad_path)
            err = ""
        except Exception as e:
            err = type(e).__name__

        with self.subTest(Out=err, Exp=expected_error):
            self.assertEqual(err, expected_error)

    def test_find_root_folder_and_dev_resolution(self):
        """
        Should return a valid folder path for project root.
        """
        # ACT
        result = api.find_root_folder()

        # ASSERT
        with self.subTest("Exists", Out=os.path.isdir(result), Exp=True):
            self.assertTrue(os.path.isdir(result))

    def test_find_drive_letter_non_windows(self):
        """
        Should raise ValueError on non-Windows systems.
        """
        # ARRANGE
        expected = ValueError.__name__

        # ACT
        try:
            api.find_drive_letter()
            result = ""
        except Exception as e:
            result = type(e).__name__

        # ASSERT
        with self.subTest(Out=result, Exp=expected):
            if os.name != "nt":
                self.assertEqual(result, expected)
            else:
                self.assertIn(result, ("", None))  # allowed on Windows


class TestJsonIO(unittest.TestCase):
    """
    Unit tests for the public JSON I/O API functions exposed via `src.utils._api`.
    """

    def test_create_json_packet(self):
        """
        Should build a packet with meta (timestamp, source, checksum) and a shallow-copied payload.
        """
        # ARRANGE
        payload = {"a": 1, "b": "two", "c": "$"}
        expected_source = "sample.csv"
        expected_payload = dict(payload)  # for equality check

        # ACT
        pkt = api.create_json_packet(payload, expected_source)

        # ASSERT
        # Use implementation constants so we don't hard-code field names
        from src.utils import _json_io as _jio

        # Structure: top-level keys present
        with self.subTest("Has meta", Out=(_jio._KEY_META in pkt), Exp=True):
            self.assertIn(_jio._KEY_META, pkt)
        with self.subTest("Has payload", Out=(_jio._KEY_PAYLOAD in pkt), Exp=True):
            self.assertIn(_jio._KEY_PAYLOAD, pkt)

        meta = pkt[_jio._KEY_META]

        # Structure: required meta keys present (no value pinning except source)
        for key in (_jio._KEY_UTC, _jio._KEY_SOURCE, _jio._KEY_SHA256):
            with self.subTest("Meta key present", Key=key, Out=(key in meta), Exp=True):
                self.assertIn(key, meta)

        # Stable meta value: source should equal the input
        with self.subTest(Field=_jio._KEY_SOURCE, Out=meta[_jio._KEY_SOURCE], Exp=expected_source):
            self.assertEqual(meta[_jio._KEY_SOURCE], expected_source)

        # Payload equality + shallow-copy semantics
        result_payload = pkt[_jio._KEY_PAYLOAD]
        with self.subTest(Field=_jio._KEY_PAYLOAD, Out=result_payload, Exp=expected_payload):
            self.assertEqual(result_payload, expected_payload)
            self.assertIsNot(result_payload, payload)  # shallow copy, not same object

    def test_dict_to_json_string(self):
        """
        Should serialize dict to JSON string and honor optional indentation.
        """
        # ARRANGE
        data = {"name": "Alice", "age": 30, "emoji": "😀"}
        expected_compact = json.dumps(data, ensure_ascii=False)
        expected_pretty = json.dumps(data, ensure_ascii=False, indent=2)

        # ACT
        result_compact = api.dict_to_json_string(data)
        result_pretty = api.dict_to_json_string(data, indent_spaces=2)

        # ASSERT
        with self.subTest(Out=result_compact, Exp=expected_compact):
            self.assertEqual(result_compact, expected_compact)
        with self.subTest(Out=result_pretty, Exp=expected_pretty):
            self.assertEqual(result_pretty, expected_pretty)

    def test_json_string_to_dict(self):
        """
        Should parse valid JSON string into an equivalent dict; malformed JSON raises RuntimeError.
        """
        # ARRANGE
        input_json_good = '{"x":1,"y":true,"txt":"hi"}'
        input_json_bad = '{"a": 1,}'  # trailing comma
        input_json = [input_json_good, input_json_bad]

        expected_dict_good = {"x": 1, "y": True, "txt": "hi"}
        expected_dict_bad = RuntimeError.__name__
        expected_dict = [expected_dict_good, expected_dict_bad]

        # ACT
        for input_data, expected in zip(input_json, expected_dict):
            try:
                result = api.json_string_to_dict(input_data)
            except Exception as e:
                result = type(e).__name__

            # ASSERT
            with self.subTest(Out=result, Exp=expected):
                self.assertEqual(result, expected)

    def test_extract_payload(self):
        """
        Should return a shallow copy of the 'payload_data' mapping from the packet.
        """
        # ARRANGE
        payload = {"k": "v", "n": 7}
        pkt = {
            "meta_data": {
                "generated_at_utc": "2025-01-01T00:00:00Z",
                "source_file_name": "x",
                "payload_checksum": 0,
            },
            "payload_data": payload,
        }

        # ACT
        result = api.extract_payload(pkt)

        # ASSERT
        with self.subTest(Out=result, Exp=payload):
            self.assertEqual(result, payload)
            self.assertIsNot(result, payload)  # shallow copy per contract

    def test_load_json_file(self):
        """
        Should read a JSON file and return its dict; missing/invalid files raise RuntimeError.
        """
        # SETUP: Create isolated temp directory and file paths
        self.tmpdir = tempfile.mkdtemp(prefix="api_json_load_")
        good_path = os.path.join(self.tmpdir, "ok.json")
        missing_path = os.path.join(self.tmpdir, "missing.json")
        if os.path.exists(good_path):
            os.remove(good_path)

        # ARRANGE
        expected = {"a": 1, "emoji": "😀"}
        with open(good_path, "w", encoding="utf-8") as f:
            json.dump(expected, f, ensure_ascii=False)  # type: ignore[arg-type]

        # ACT
        loaded = api.load_json_file(good_path)
        try:
            api.load_json_file(missing_path)
            missing_err = ""
        except Exception as e:
            missing_err = type(e).__name__

        # ASSERT
        with self.subTest(Out=loaded, Exp=expected):
            self.assertEqual(loaded, expected)
        with self.subTest(Out=missing_err, Exp=RuntimeError.__name__):
            self.assertEqual(missing_err, RuntimeError.__name__)

        # CLEANUP: remove file first, then remove the directory
        if os.path.isfile(good_path):
            os.remove(good_path)
        if os.path.isdir(self.tmpdir):
            os.rmdir(self.tmpdir)

    def test_save_json_file(self):
        """
        Should write dict as JSON to path and honor indent_spaces.
        """
        # SETUP: Create an isolated temp directory and output file path
        self.tmpdir = tempfile.mkdtemp(prefix="api_json_save_")
        self.out_path = os.path.join(self.tmpdir, "out.json")
        if os.path.exists(self.out_path):
            os.remove(self.out_path)

        # ARRANGE
        data = {"hello": "world", "n": 3}

        # ACT
        api.save_json_file(self.out_path, data, indent_spaces=None)

        # ASSERT
        with open(self.out_path, "r", encoding="utf-8") as f:
            text = f.read()
        exp = json.dumps(data, ensure_ascii=False, indent=None)
        with self.subTest(Out=text, Exp=exp):
            self.assertEqual(text, exp)

        # CLEANUP: remove file then remove dir
        if os.path.isfile(self.out_path):
            os.remove(self.out_path)
        if os.path.isdir(self.tmpdir):
            os.rmdir(self.tmpdir)

    def test_parse_strict_key_value_to_dict(self):
        """
        Should parse strict `"Key" = "Value"` lines, ignore comments/blank lines, and yield dict.
        """
        # ARRANGE
        src = "cfg.txt"
        text = (
            '"A" = "1"\n'
            '   # comment\n'
            '"B"="2"  # trailing\n'
        )
        expected = {"A": "1", "B": "2"}

        # ACT
        with patch("builtins.print"):  # suppress warning prints for invalid lines (if any)
            result = api.parse_strict_key_value_to_dict(src, text)

        # ASSERT
        with self.subTest(Out=result, Exp=expected):
            self.assertEqual(result, expected)

    def test_verify_json_payload_checksum(self):
        """
        Should return True for matching checksum and False when payload changes.
        """
        # ARRANGE
        data = {"x": "10", "y": True}
        # Compute checksum via implementation helper to build a valid packet
        from src.utils import _json_io as _jio  # local import to access helper
        ck_good = _jio._compute_payload_sha256(data)
        pkt_good = {
            "meta_data": {"generated_at_utc": "Z", "source_file_name": "s",
                          "payload_sha256": ck_good},
            "payload_data": dict(data),
        }
        not_data = {"one": "1", "two": "2"}  # not the same as data
        ck_bad = _jio._compute_payload_sha256(not_data)  # make incorrect checksum
        pkt_bad = {
            "meta_data": {"generated_at_utc": "Z", "source_file_name": "s",
                          "payload_sha256": ck_bad},
            "payload_data": {"x": "10", "y": False},  # changed payload
        }

        input_packet = [pkt_good, pkt_bad]
        expected_output = [True, False]

        for packet, expected in zip(input_packet, expected_output):
            # ACT
            result = api.verify_json_payload_checksum(packet)

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
