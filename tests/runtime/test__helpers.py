"""
Unit tests for runtime JSON helper utilities.

Example Usage:
    # Preferred usage via project-root invocation:
    python -m unittest tests/runtime/test__helpers.py

    # Direct discovery (runs all tests, including this module):
    python -m unittest discover -s tests

Dependencies:
    - Python >= 3.10
    - Standard Library: unittest, tempfile, pathlib, json
    - External Packages: None

Notes:
    - Tests use temporary files and controlled JSON payloads to exercise checksum pass/fail paths.
    - Error assertions check message clarity and exception types without relying on internal implementation details.
    - Keep fixtures minimal; prefer inline JSON for readability and isolation.

License:
    - Internal Use Only
"""

import os
import shutil
import tempfile
import unittest
from typing import Any
from unittest.mock import patch

import src.utils as utils
# noinspection PyProtectedMember
import src.runtime._helpers as hlp  # Module under test


class Asserts(unittest.TestCase):
    """
    Common assertion helpers for unit tests.
    """

    def assert_equal(self, *, actual: Any, expected: Any):
        """
        Assert that two values are equal when compared as strings.
        """
        val_out = str(actual)
        val_exp = str(expected)
        with self.subTest(Actual=val_out, Expected=val_exp):
            self.assertEqual(val_out, val_exp)

    def assert_empty(self, *, actual: Any):
        """
        Assert that the given value is an empty string.
        """
        val_out = str(actual)
        with self.subTest("Empty", Actual=val_out):
            self.assertEqual(val_out, "")

    def assert_no_error(self, *, actual: str):
        """
        Assert that no error occurred, represented by an empty string.
        """
        with self.subTest("No Error", Actual=actual):
            self.assertEqual(actual, "")


class TestAssertAllValuesAreStrOrListStr(Asserts):
    """
    Tests for `assert_all_values_are_str_or_list_str`.
    """

    def test_valid(self):
        """
        Should accept mappings of str and list[str] without raising.
        """
        # ARRANGE
        cases = (
            {  # Strings only
                "KEY1": "Value1",
                "KEY2": "Value2",
                "KEY3": ""
            },
            {  # List of string only
                "KEY1": ["Value1", "Value2"],
                "KEY2": ["", "Value3"],
                "KEY3": [""]
            },
            {  # Mix of string and list of string
                "KEY1": "Value1",
                "KEY2": ["Value2", "Value3"],
            }
        )

        for key_value_map in cases:
            # ACT
            try:
                hlp.assert_all_values_are_str_or_list_str(key_value_map)
                result = ""  # No exception raised
            except Exception as e:
                result = type(e)

            # ASSERT
            self.assert_no_error(actual=result)

    def test_invalid(self):
        """
        Should raise TypeError when a value or list element is not a str.
        """
        # ARRANGE
        cases = (
            {
                "KEY1": "Valid",
                "KEY2": 123,  # Non-string value
            },
            {
                "KEY1": ["Valid", 123],  # Non-string list
                "KEY2": "Also valid"
            }
        )

        expected_error = TypeError.__name__

        # ACT
        for key_value_map in cases:
            # ACT
            try:
                hlp.assert_all_values_are_str_or_list_str(key_value_map)
                actual_error = ""  # No exception raised
            except Exception as e:
                actual_error = type(e).__name__

            # ASSERT
            self.assert_equal(actual=actual_error, expected=expected_error)


class TestAssertRequiredKeysArePresent(Asserts):
    """
    Unit tests for the `assert_required_keys_are_present` function.
    """

    def test_all_required_present(self):
        """
        Should pass when all required keys exist.
        """
        # ARRANGE
        key_value_map = {
            "APP_NAME": "MyApp",
            "WELCOME": "Hello",
            "VERSION": "1.0.0",
        }
        required_keys = ["APP_NAME", "WELCOME"]

        # ACT
        try:
            hlp.assert_required_keys_are_present(key_value_map, required_keys)
            result = ""  # No exception raised
        except Exception as e:
            result = type(e).__name__

        # ASSERT
        self.assert_no_error(actual=result)

    def test_missing_single_key_raises(self):
        """
        Should raise KeyError when one required key is absent.
        """
        # ARRANGE
        key_value_map = {
            "APP_NAME": "MyApp",
            "WELCOME": "Hello",
        }
        required_keys = ["APP_NAME", "WELCOME", "VERSION"]
        expected_error = KeyError.__name__

        # ACT
        try:
            hlp.assert_required_keys_are_present(key_value_map, required_keys)
            result = ""  # No exception raised
        except Exception as e:
            result = type(e).__name__

        # ASSERT
        self.assert_equal(actual=result, expected=expected_error)

    def test_missing_multiple_keys_raises(self):
        """
        Should raise KeyError when multiple required keys are absent.
        """
        # ARRANGE
        key_value_map = {
            "WELCOME": "Hello",
        }
        required_keys = ["APP_NAME", "WELCOME", "VERSION"]
        expected_error = KeyError.__name__

        # ACT
        try:
            hlp.assert_required_keys_are_present(key_value_map, required_keys)
            result = ""  # No exception raised
        except Exception as e:
            result = type(e).__name__

        # ASSERT
        self.assert_equal(actual=result, expected=expected_error)

    def test_empty_required_keys(self):
        """
        Should pass when no required keys are provided.
        """
        # ARRANGE
        key_value_map = {
            "APP_NAME": "MyApp",
            "WELCOME": "Hello",
        }
        required_keys = []
        expected_error = ""

        # ACT
        try:
            hlp.assert_required_keys_are_present(key_value_map, required_keys)
            result = ""  # No exception raised
        except Exception as e:
            result = type(e).__name__

        # ASSERT
        self.assert_equal(actual=result, expected=expected_error)


class TestExportKeys(Asserts):
    """
    Unit test for the `export_keys` function.
    """

    def test_with_uppercase_string_constants(self):
        """
        Should return only uppercase names whose values are strings.
        """
        # ARRANGE
        module_globals = {
            "FOO": "foo",  # valid
            "BAR": "bar",  # valid
            "baz": "baz",  # lowercase, excluded
            "REQUIRED_KEYS": ["X"],  # uppercase but not string, excluded
            "NUM": 123,  # uppercase but not string, excluded
        }
        expected = ["FOO", "BAR"]

        # ACT
        actual = hlp.export_keys(module_globals)

        # ASSERT
        self.assert_equal(actual=actual, expected=expected)

    def test_without_uppercase_strings(self):
        """
        Should return an empty list when no uppercase string constants exist.
        """
        # ARRANGE
        module_globals = {
            "lower": "value",
            "MixedCase": "value",
            "LIST": [1, 2, 3],
            "NUM": 42
        }
        expected = []

        # ACT
        actual = hlp.export_keys(module_globals)

        # ASSERT
        self.assert_equal(actual=actual, expected=expected)


class TestLoadRuntimeJson(Asserts):
    """
    Unit tests for `load_runtime_json` function.
    """

    def setUp(self):
        """
        Create a temporary runtime directory and patch `_resolve_json_file_path` so it resolves into this directory for the duration of each test.
        """
        self.tmpdir = tempfile.mkdtemp(prefix="runtime_json_")
        self.orig_resolver = hlp.resolve_json_file_path

        # Patch the path resolver to always return a file within our temp directory.
        def _resolver(resource_name: str):
            filename = resource_name + utils.JSON_FILE_EXT
            return os.path.join(self.tmpdir, filename)

        hlp.resolve_json_file_path = _resolver  # simple, library-free patch

        # Convenience: name for our resource (e.g., "_info")
        self.resource = "_test_resource"
        self.filename = self.resource + utils.JSON_FILE_EXT
        self.filepath = os.path.join(self.tmpdir, self.filename)

    def tearDown(self):
        """
        Restore the original resolver and remove temp files.
        """
        hlp.resolve_json_file_path = self.orig_resolver
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_valid(self):
        """
        Should return payload when file exists and checksum is valid.
        """
        # ARRANGE
        payload = {"APP_NAME": "MyApp", "WELCOME": "Hello"}
        packet = utils.create_json_packet(payload, source_file=self.filename)
        utils.save_json_file(self.filepath, packet)
        expected = payload

        # ACT
        actual = hlp.load_and_validate_json(self.resource, self.filepath)

        # ASSERT
        self.assert_equal(actual=actual, expected=expected)

    def test_missing_json(self):
        """
        Should raise RuntimeError when the JSON file is missing.
        """
        # ARRANGE
        expected = RuntimeError.__name__

        # ACT
        try:
            hlp.load_and_validate_json(self.resource, self.filepath)
            actual = ""  # Unexpected: no exception
        except Exception as e:
            actual = type(e).__name__

        # ASSERT
        self.assert_equal(actual=actual, expected=expected)

    def test_corrupt_json(self):
        """
        Should raise RuntimeError when checksum verification fails.
        """
        # ARRANGE
        payload = {"APP_NAME": "MyApp", "WELCOME": "Hello"}
        packet = utils.create_json_packet(payload, source_file=self.filename)
        utils.save_json_file(self.filepath, packet)
        expected = RuntimeError.__name__

        with patch.object(utils, "verify_json_payload_checksum") as p_checksum_ok:
            p_checksum_ok.return_value = False

            # ACT
            try:
                hlp.load_and_validate_json(self.resource, self.filepath)
                actual = ""  # Unexpected: no exception
            except Exception as e:
                actual = type(e).__name__

        # ASSERT
        self.assert_equal(actual=actual, expected=expected)

    def test_empty_json(self):
        """
        Should raise RuntimeError when payload data is empty.
        """
        # ARRANGE
        payload = {}  # empty
        packet_data = utils.create_json_packet(payload, source_file=self.filename)
        utils.save_json_file(self.filepath, packet_data)

        expected = RuntimeError.__name__

        # ACT
        try:
            hlp.load_and_validate_json(self.resource, self.filepath)
            actual = ""  # Unexpected: no exception
        except Exception as e:
            actual = type(e).__name__

            # ASSERT
        self.assert_equal(actual=actual, expected=expected)


class TestResolveJsonFilePath(Asserts):
    """
    Unit tests for `resolve_json_file_path` function.
    """

    def setUp(self):
        """
        Create a temporary directory to act as the runtime folder.
        """
        # Create a unique temporary root directory
        self.tmp_root = tempfile.mkdtemp(prefix="runtime_tmp_")

        # Create folders inside temp root
        self.tmp_runtime = os.path.join(self.tmp_root, hlp.RUNTIME_FOLDER[0], hlp.RUNTIME_FOLDER[1])
        os.makedirs(self.tmp_runtime, exist_ok=True)

    def tearDown(self):
        """
        Remove the temporary directory after tests.
        """
        shutil.rmtree(self.tmp_root, ignore_errors=True)

    def test_file_exists(self):
        """
        Should return the absolute path when the JSON file exists.
        """
        # ARRANGE
        resource = "test_resource"
        filename = hlp.RUNTIME_JSON_PREFIX + resource + utils.JSON_FILE_EXT
        expected_path = os.path.join(self.tmp_runtime, filename)

        with open(expected_path, "w", encoding="utf-8") as f:
            f.write('{"meta": {}, "data": {}}')

        # path project root to temp
        with patch.object(utils, "find_root_folder") as p_root:
            p_root.return_value = self.tmp_root

            # ACT
            result = hlp.resolve_json_file_path(resource)

        # ASSERT
        self.assert_equal(actual=result, expected=expected_path)

    def test_file_missing(self):
        """
        Should raise FileNotFoundError when the JSON file is absent.
        """
        # ARRANGE
        resource = "test_resource"
        expected_error = FileNotFoundError.__name__

        # path project root to temp
        with patch.object(utils, "find_root_folder") as p_root:
            p_root.return_value = self.tmp_root

            # ACT
            try:
                hlp.resolve_json_file_path(resource)
                result = ""  # No exception raised (unexpected)
            except Exception as e:
                result = type(e).__name__

        # ASSERT
        self.assert_equal(actual=result, expected=expected_error)


if __name__ == "__main__":
    unittest.main()
