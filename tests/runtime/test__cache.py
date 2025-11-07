"""
Unit tests for the Cache class that manages runtime JSON resource loading and access.

Example Usage:
    # Preferred usage via project-root invocation:
    python -m unittest tests/runtime/test__cache.py

    # Direct discovery (runs all tests under runtime package):
    python -m unittest discover -s tests

Dependencies:
 - Python >= 3.10
 - Standard Library: unittest, tempfile, shutil, os, typing, unittest.mock
 - External Packages: None
 - Internal Modules: src.runtime._cache, src.runtime._helpers, src.utils

Notes:
 - Uses temporary directories and JSON packet creation via utils for isolation.
 - Asserts implemented via helper class _Asserts for consistency in result reporting.
 - Resource loading is patched to avoid dependence on actual runtime directory.
 - Designed to ensure robustness of the caching layer and error handling paths.

License:
 - Internal Use Only
"""

import os
import shutil
import tempfile
import unittest
from typing import Any
from unittest.mock import patch

# noinspection PyProtectedMember
import src.runtime._cache as cache  # module under test

# noinspection PyProtectedMember
import src.runtime._helpers as hlp

import src.utils as utils

# MODULE_CONSTANTS
TEST_RESOURCE_NAME = "test_resource"
TEST_DATA_JSON = {"Alpha": "A", "Beta": "B", "Delta": "D", "Gamma": "G", "List": ["1", "2"]}
TEST_REQUIRED_KEYS = ["Delta", "Beta"]


class _Asserts(unittest.TestCase):
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


class _TestFixture(unittest.TestCase):
    """
    Test fixture that provisions a temporary runtime root with a JSON resource and cleans it up.
    """

    def setUp(self):
        """
        Prepare a temporary project root and runtime folder, write a JSON resource packet, and create a Cache under test.
        """
        # Create an isolated project root; deleted in tearDown()
        self.tmp_project_root = tempfile.mkdtemp(prefix="runtime_tmp_")

        # Mirror the on-disk runtime layout used by production code
        runtime_dir = utils.construct_folder_path(self.tmp_project_root, hlp.RUNTIME_FOLDER)
        os.makedirs(runtime_dir, exist_ok=True)

        # Build resource file paths and names
        resource_filename = hlp.RUNTIME_JSON_PREFIX + TEST_RESOURCE_NAME + utils.JSON_FILE_EXT
        resource_path = os.path.join(runtime_dir, resource_filename)

        # Wrap the payload in the standard packet envelope expected by the loader
        resource_packet = utils.create_json_packet(TEST_DATA_JSON, source_file=resource_filename)

        # Persist the packet where Cache.load() will look for it
        utils.save_json_file(resource_path, resource_packet)

        # Cache under test
        self.cache = cache.Cache()

    def tearDown(self):
        """
        Remove the temporary project root and all generated files.
        """
        # Best-effort cleanup to avoid leaking temp files on test failures
        shutil.rmtree(self.tmp_project_root, ignore_errors=True)


class TestFetchValue(_Asserts, _TestFixture):
    """
    Unit tests for Cache._fetch_value.
    """

    def test_valid(self):
        """
        Should return the stored value when the key exists.
        """
        # ARRANGE
        requested_key = "Delta"
        expected_value = "D"

        with patch.object(utils, "find_root_folder") as p_root:
            p_root.return_value = self.tmp_project_root
            # ACT
            self.cache.load_resource(TEST_RESOURCE_NAME, TEST_REQUIRED_KEYS)
            actual_value = self.cache._fetch_value(requested_key)

        # ASSERT
        self.assert_equal(actual=actual_value, expected=expected_value)

    def test_missing(self):
        """
        Should raise KeyError when the key does not exist.
        """
        # ARRANGE
        requested_key = "MissingKeyName"
        expected_error = KeyError.__name__

        with patch.object(utils, "find_root_folder") as p_root:
            p_root.return_value = self.tmp_project_root
            # ACT
            try:
                self.cache.load_resource(TEST_RESOURCE_NAME, TEST_REQUIRED_KEYS)
                _ = self.cache._fetch_value(requested_key)
                actual_error = ""
            except Exception as e:
                actual_error = type(e).__name__

        # ASSERT
        self.assert_equal(actual=actual_error, expected=expected_error)

    def test_invalid_name_type(self):
        """
        Should raise TypeError when key is not a string.
        """
        # ARRANGE
        requested_key = 123
        expected_error = TypeError.__name__

        with patch.object(utils, "find_root_folder") as p_root:
            p_root.return_value = self.tmp_project_root
            # ACT
            try:
                self.cache.load_resource(TEST_RESOURCE_NAME, TEST_REQUIRED_KEYS)
                _ = self.cache._fetch_value(requested_key)  # type: ignore[arg-type]
                actual_error = ""
            except Exception as e:
                actual_error = type(e).__name__

        # ASSERT
        self.assert_equal(actual=actual_error, expected=expected_error)


class TestGetAllKeys(_Asserts, _TestFixture):
    """
    Unit tests for Cache.get_all_keys.
    """

    def test_valid(self):
        """
        Should return all keys in stable order after load.
        """
        # ARRANGE
        expected_keys = ("Alpha", "Beta", "Delta", "Gamma", "List")

        with patch.object(utils, "find_root_folder") as p_root:
            p_root.return_value = self.tmp_project_root
            # ACT
            self.cache.load_resource(TEST_RESOURCE_NAME, TEST_REQUIRED_KEYS)
            actual_keys = self.cache.get_all_keys()

        # ASSERT
        self.assertEqual(actual_keys, expected_keys)

    def test_missing_key(self):
        """
        Should raise KeyError when a required key is absent during load.
        """
        # ARRANGE
        required_keys = ["Alpha", "MissingKey"]
        expected_error = KeyError.__name__

        with patch.object(utils, "find_root_folder") as p_root:
            p_root.return_value = self.tmp_project_root
            # ACT
            try:
                self.cache.load_resource(TEST_RESOURCE_NAME, required_keys)
                actual_error = ""
            except Exception as e:
                actual_error = type(e).__name__

        # ASSERT
        self.assert_equal(actual=actual_error, expected=expected_error)


class TestGetDataMap(_Asserts, _TestFixture):
    """
    Unit test for get_data_map.
    """

    def test_valid(self):
        """
        Should return the validated dictionary of key–value pairs for the loaded resource.
        """
        # ARRANGE
        expected_map = TEST_DATA_JSON

        with patch.object(utils, "find_root_folder") as p_root:
            p_root.return_value = self.tmp_project_root

            # ACT
            self.cache.load_resource(TEST_RESOURCE_NAME, TEST_REQUIRED_KEYS)
            actual_map = self.cache.get_data_map()

        # ASSERT
        self.assert_equal(actual=actual_map, expected=expected_map)

    def test_raises(self):
        """
        Should raise if called before any resource has been loaded.
        """
        # ARRANGE
        expected_error = ResourceWarning.__name__

        # ACT
        try:
            _ = self.cache.get_data_map()
            actual_error = ""
        except Exception as e:
            actual_error = type(e).__name__

        # ASSERT
        self.assert_equal(actual=actual_error, expected=expected_error)


class TestGetListValue(_Asserts, _TestFixture):
    """
    Unit tests for Cache.get_list_value.
    """

    def test_valid(self):
        """
        Should return a tuple of strings when the stored value is a list of strings.
        """
        # ARRANGE
        requested_key = "List"
        expected_value = ("1", "2")

        with patch.object(utils, "find_root_folder") as p_root:
            p_root.return_value = self.tmp_project_root
            # ACT
            self.cache.load_resource(TEST_RESOURCE_NAME, TEST_REQUIRED_KEYS)
            actual_value = self.cache.get_list_value(requested_key)

        # ASSERT
        self.assert_equal(actual=actual_value, expected=expected_value)

    def test_invalid(self):
        """
        Should raise TypeError when the stored value is not a list of strings.
        """
        # ARRANGE
        requested_key = "Alpha"
        expected_error = TypeError.__name__

        with (
            patch.object(utils, "find_root_folder") as p_root,
            patch.object(self.cache, "_fetch_value") as p_fetch,
        ):
            p_root.return_value = self.tmp_project_root
            p_fetch.return_value = 123
            # ACT
            try:
                self.cache.load_resource(TEST_RESOURCE_NAME, TEST_REQUIRED_KEYS)
                _ = self.cache.get_list_value(requested_key)
                actual_error = ""
            except Exception as e:
                actual_error = type(e).__name__

        # ASSERT
        self.assert_equal(actual=actual_error, expected=expected_error)


class TestGetStrValue(_Asserts, _TestFixture):
    """
    Unit tests for Cache.get_str_value.
    """

    def test_valid(self):
        """
        Should return a string when the stored value is a string.
        """
        # ARRANGE
        requested_key = "Delta"
        expected_value = "D"

        with patch.object(utils, "find_root_folder") as p_root:
            p_root.return_value = self.tmp_project_root
            # ACT
            self.cache.load_resource(TEST_RESOURCE_NAME, TEST_REQUIRED_KEYS)
            actual_value = self.cache.get_str_value(requested_key)

        # ASSERT
        self.assert_equal(actual=actual_value, expected=expected_value)

    def test_invalid(self):
        """
        Should raise TypeError when the stored value is not a string.
        """
        # ARRANGE
        requested_key = "List"
        expected_error = TypeError.__name__

        with patch.object(utils, "find_root_folder") as p_root:
            p_root.return_value = self.tmp_project_root
            # ACT
            try:
                self.cache.load_resource(TEST_RESOURCE_NAME, TEST_REQUIRED_KEYS)
                _ = self.cache.get_str_value(requested_key)
                actual_error = ""
            except Exception as e:
                actual_error = type(e).__name__

        # ASSERT
        self.assert_equal(actual=actual_error, expected=expected_error)


class TestLoadResource(_Asserts, _TestFixture):
    """
    Unit tests for Cache.load_resource.
    """

    def test_valid(self):
        """
        Should load the resource and populate the cache mapping.
        """
        # ARRANGE
        expected_map = TEST_DATA_JSON

        with patch.object(utils, "find_root_folder") as p_root:
            p_root.return_value = self.tmp_project_root
            # ACT
            self.cache.load_resource(TEST_RESOURCE_NAME, TEST_REQUIRED_KEYS)
            result = self.cache.data_map

        # ASSERT
        self.assertEqual(result, expected_map)

    def test_reload(self):
        """
        Should raise ResourceWarning when load is called twice on the same instance.
        """
        # ARRANGE
        expected_error = ResourceWarning.__name__

        with patch.object(utils, "find_root_folder") as p_root:
            p_root.return_value = self.tmp_project_root
            # ACT
            self.cache.load_resource(TEST_RESOURCE_NAME, TEST_REQUIRED_KEYS)
            try:
                self.cache.load_resource(TEST_RESOURCE_NAME, TEST_REQUIRED_KEYS)
                actual_error = ""
            except Exception as e:
                actual_error = type(e).__name__

        # ASSERT
        self.assert_equal(actual=actual_error, expected=expected_error)

    def test_missing(self):
        """
        Should raise FileNotFoundError when the resource file does not exist.
        """
        # ARRANGE
        resource = "not_a_resource"
        expected_error = FileNotFoundError.__name__

        with patch.object(utils, "find_root_folder") as p_root:
            p_root.return_value = self.tmp_project_root
            # ACT
            try:
                self.cache.load_resource(resource, TEST_REQUIRED_KEYS)
                actual_error = ""
            except Exception as e:
                actual_error = type(e).__name__

        # ASSERT
        self.assert_equal(actual=actual_error, expected=expected_error)


if __name__ == "__main__":
    unittest.main()
