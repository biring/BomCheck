"""
Unit tests for the JSON resource cache and related helper functions.

These tests verify JSON payload loading, required-key validation, path resolution, and cache isolation behavior for the JsonCache component.

Example Usage:
    # Preferred usage via project-root invocation:
    python -m unittest tests/common/test__json_cache.py

    # Direct discovery (runs all tests under tests package):
    python -m unittest discover -s tests

Dependencies:
 - Python >= 3.10

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
import src.utils as utils

# noinspection PyProtectedMember
import src.common._json_cache as jc  # module under test

# MODULE_CONSTANTS
TEST_RESOURCE_PREFIX: str = "_"
TEST_RESOURCE_FOLDER_PARTS: tuple[str, ...] = ("a", "b",)

TEST_VALID_JSON: dict[str, Any] = {"Char": "A", "String": "ABC123!@#", "List": ["1", "ABC"]}
TEST_VALID_RESOURCE_NAME: str = "test_resource"
TEST_VALID_REQ_KEYS: tuple[str, ...] = ("String", "List",)

TEST_EMPTY_JSON: dict[str, Any] = {}
TEST_EMPTY_RESOURCE_NAME: str = "test_empty_resource"
TEST_EMPTY_REQ_KEYS: tuple[str, ...] = ()


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
        Prepare a temporary project root and runtime folder, and write a JSON resource packet for use by tests.
        """
        # Create an isolated project root; deleted in tearDown()
        self.tmp_project_root = tempfile.mkdtemp(prefix="runtime_tmp_")

        # Mirror the on-disk runtime layout used by production code
        self.runtime_dir = utils.construct_folder_path(self.tmp_project_root, TEST_RESOURCE_FOLDER_PARTS)
        os.makedirs(self.runtime_dir, exist_ok=True)

        # Build resource file paths and names
        resource_filename = TEST_RESOURCE_PREFIX + TEST_VALID_RESOURCE_NAME + utils.JSON_FILE_EXT
        resource_path = os.path.join(self.runtime_dir, resource_filename)

        # Wrap the payload in the standard packet envelope expected by the loader
        resource_packet = utils.create_json_packet(TEST_VALID_JSON, source_file=resource_filename)

        # Persist the packet where Cache.load() will look for it
        utils.save_json_file(resource_path, resource_packet)

    def tearDown(self):
        """
        Remove the temporary project root and all generated files.
        """
        # Best-effort cleanup to avoid leaking temp files on test failures
        shutil.rmtree(self.tmp_project_root, ignore_errors=True)

    def _valid_json(self):
        """
        Create a valid JSON resource packet.
        """

        # Build resource file paths and names
        resource_filename = TEST_RESOURCE_PREFIX + TEST_VALID_RESOURCE_NAME + utils.JSON_FILE_EXT
        resource_path = os.path.join(self.runtime_dir, resource_filename)

        # Wrap the payload in the standard packet envelope expected by the loader
        resource_packet = utils.create_json_packet(TEST_VALID_JSON, source_file=resource_filename)

        # Persist the packet where Cache.load() will look for it
        utils.save_json_file(resource_path, resource_packet)

    def _empty_json(self):
        """
        Create an empty JSON resource packet.
        """
        # Build resource file paths and names
        resource_filename = TEST_RESOURCE_PREFIX + TEST_EMPTY_RESOURCE_NAME + utils.JSON_FILE_EXT
        resource_path = os.path.join(self.runtime_dir, resource_filename)

        # Wrap the payload in the standard packet envelope expected by the loader
        resource_packet = utils.create_json_packet(TEST_EMPTY_JSON, source_file=resource_filename)

        # Persist the packet where Cache.load() will look for it
        utils.save_json_file(resource_path, resource_packet)


class TestJsonCache(_Asserts, _TestFixture):
    """
    Unit tests for JsonCache initialization and required-key validation.
    """

    def test_empty_payload(self):
        """
        Should raise error when the loaded JSON payload is empty.
        """
        # ARRANGE
        self._empty_json()
        expected_error = ImportError.__name__

        # ACT
        try:
            with patch.object(utils, "find_root_folder") as p_root:
                p_root.return_value = self.tmp_project_root
                _ = jc.JsonCache(TEST_EMPTY_RESOURCE_NAME, TEST_RESOURCE_FOLDER_PARTS, TEST_EMPTY_REQ_KEYS)
            actual_error = ""
        except Exception as e:
            actual_error = type(e).__name__

        # ASSERT
        self.assert_equal(actual=actual_error, expected=expected_error)

    def test_missing_required_key(self):
        """
        Should raise error when one or more required keys are missing.
        """
        # ARRANGE
        required_keys = ("List", "MissingKey")
        expected_error = ImportError.__name__

        # ACT
        with patch.object(utils, "find_root_folder") as p_root:
            p_root.return_value = self.tmp_project_root
            try:
                _ = jc.JsonCache(TEST_VALID_RESOURCE_NAME, TEST_RESOURCE_FOLDER_PARTS, required_keys)
                actual_error = ""
            except Exception as e:
                actual_error = type(e).__name__

        # ASSERT
        self.assert_equal(actual=actual_error, expected=expected_error)


class TestGetDataMapCopy(_Asserts, _TestFixture):
    """
    Unit tests for get_data_map_copy.
    """

    def test_valid(self):
        """
        Should return a dictionary containing the validated JSON payload.
        """
        # ARRANGE
        with patch.object(utils, "find_root_folder") as p_root:
            p_root.return_value = self.tmp_project_root
            test_cache = jc.JsonCache(TEST_VALID_RESOURCE_NAME, TEST_RESOURCE_FOLDER_PARTS)
        expected_map = TEST_VALID_JSON

        # ACT
        actual_map = test_cache.get_data_map_copy()

        # ASSERT
        self.assert_equal(actual=actual_map, expected=expected_map)

    def test_get_data_map_copy_isolation(self):
        """
        Should return a copy that does not mutate the cache's internal data map.
        """

        # ARRANGE
        with patch.object(utils, "find_root_folder") as p_root:
            p_root.return_value = self.tmp_project_root
            cache = jc.JsonCache(TEST_VALID_RESOURCE_NAME, TEST_RESOURCE_FOLDER_PARTS)
        copy_map = cache.get_data_map_copy()

        # ACT
        # Mutate the data
        copy_map["String"] = "MUTATED"
        # Optionally mutate nested list as well
        copy_map["List"].append("NEW")
        # Re-fetch from cache to confirm isolation
        fresh = cache.get_data_map_copy()

        # ASSERT
        self.assert_equal(actual=fresh, expected=TEST_VALID_JSON)


class TestGetKeys(_Asserts, _TestFixture):
    """
    Unit tests for get_keys.
    """

    def test_valid(self):
        """
        Should return all JSON keys as a sorted list.
        """
        # ARRANGE
        with patch.object(utils, "find_root_folder") as p_root:
            p_root.return_value = self.tmp_project_root
            test_cache = jc.JsonCache(TEST_VALID_RESOURCE_NAME, TEST_RESOURCE_FOLDER_PARTS,
                                      TEST_VALID_REQ_KEYS)
        expected_keys = ("Char", "List", "String",)  # Sorted

        # ACT
        actual_keys = test_cache.get_keys()

        # ASSERT
        self.assertEqual(actual_keys, expected_keys)


class TestGetValue(_Asserts, _TestFixture):
    """
    Unit tests for get_value.
    """

    def test_valid(self):
        """
        Should return the stored value when the key exists and type matches.
        """
        # ARRANGE
        with patch.object(utils, "find_root_folder") as p_root:
            p_root.return_value = self.tmp_project_root
            test_cache = jc.JsonCache(TEST_VALID_RESOURCE_NAME, TEST_RESOURCE_FOLDER_PARTS,
                                      TEST_VALID_REQ_KEYS)
        cases = (
            (str, "String", "ABC123!@#"),
            (list, "List", ["1", "ABC"]),
        )

        for data_type, key, expected_value in cases:
            # ACT
            actual_value = test_cache.get_value(key, data_type)
            # ASSERT
            self.assert_equal(actual=actual_value, expected=expected_value)

    def test_missing_key(self):
        """
        Should raise KeyError when the requested key does not exist.
        """
        # ARRANGE
        with patch.object(utils, "find_root_folder") as p_root:
            p_root.return_value = self.tmp_project_root
            test_cache = jc.JsonCache(TEST_VALID_RESOURCE_NAME, TEST_RESOURCE_FOLDER_PARTS,
                                      TEST_VALID_REQ_KEYS)
        requested_key = "MissingKeyName"
        expected_error = KeyError.__name__

        # ACT
        try:
            _ = test_cache.get_value(requested_key, str)
            actual_error = ""
        except Exception as e:
            actual_error = type(e).__name__

        # ASSERT
        self.assert_equal(actual=actual_error, expected=expected_error)

    def test_invalid_key_type(self):
        """
        Should raise error when the key argument is not a string.
        """
        # ARRANGE
        with patch.object(utils, "find_root_folder") as p_root:
            p_root.return_value = self.tmp_project_root
            test_cache = jc.JsonCache(TEST_VALID_RESOURCE_NAME, TEST_RESOURCE_FOLDER_PARTS, TEST_VALID_REQ_KEYS)
        requested_key = 123
        expected_error = TypeError.__name__

        # ACT
        try:
            _ = test_cache.get_value(requested_key, str)  # type: ignore
            actual_error = ""
        except Exception as e:
            actual_error = type(e).__name__

        # ASSERT
        self.assert_equal(actual=actual_error, expected=expected_error)

    def test_type_mismatch_raises_type_error(self):
        """
        Should raise error when the stored value type does not match the requested type.
        """
        # ARRANGE
        with patch.object(utils, "find_root_folder") as p_root:
            p_root.return_value = self.tmp_project_root
            test_cache = jc.JsonCache(TEST_VALID_RESOURCE_NAME, TEST_RESOURCE_FOLDER_PARTS, TEST_VALID_REQ_KEYS)
        requested_key = "String"
        expected_error = TypeError.__name__

        # ACT
        try:
            _ = test_cache.get_value(requested_key, list)
            actual_error = ""
        except Exception as e:
            actual_error = type(e).__name__

        # ASSERT
        self.assert_equal(actual=actual_error, expected=expected_error)


class TestAssertRequiredKeys(_Asserts):
    """
    Unit tests for the _assert_required_keys helper.
    """

    def test_all_required_present(self):
        """
        Should NOT raise an exception when all required keys are present.
        """
        # ARRANGE
        key_value_map = {
            "APP_NAME": "MyApp",
            "WELCOME": "Hello",
            "VERSION": "1.0.0",
        }
        required_keys: tuple[str, ...] = ("APP_NAME", "WELCOME")

        # ACT
        try:
            jc._assert_required_keys(key_value_map, required_keys)
            result = ""  # No exception raised
        except Exception as e:
            result = type(e).__name__

        # ASSERT
        self.assert_no_error(actual=result)

    def test_missing_single_key_raises(self):
        """
        Should raise error when exactly one required key is missing.
        """
        # ARRANGE
        key_value_map = {
            "APP_NAME": "MyApp",
            "WELCOME": "Hello",
        }
        required_keys: tuple[str, ...] = ("APP_NAME", "WELCOME", "VERSION")
        expected_error = KeyError.__name__

        # ACT
        try:
            jc._assert_required_keys(key_value_map, required_keys)
            result = ""  # No exception raised
        except Exception as e:
            result = type(e).__name__

        # ASSERT
        self.assert_equal(actual=result, expected=expected_error)

    def test_missing_multiple_keys_raises(self):
        """
        Should raise error when multiple required keys are missing.
        """
        # ARRANGE
        key_value_map = {
            "WELCOME": "Hello",
        }
        required_keys: tuple[str, ...] = ("APP_NAME", "WELCOME", "VERSION")
        expected_error = KeyError.__name__

        # ACT
        try:
            jc._assert_required_keys(key_value_map, required_keys)
            result = ""  # No exception raised
        except Exception as e:
            result = type(e).__name__

        # ASSERT
        self.assert_equal(actual=result, expected=expected_error)

    def test_empty_required_keys(self):
        """
        Should NOT raise an exception when the required-key list is empty.
        """
        # ARRANGE
        key_value_map = {
            "APP_NAME": "MyApp",
            "WELCOME": "Hello",
        }
        required_keys: tuple[str, ...] = ()
        expected_error = ""

        # ACT
        try:
            jc._assert_required_keys(key_value_map, required_keys)
            result = ""  # No exception raised
        except Exception as e:
            result = type(e).__name__

        # ASSERT
        self.assert_equal(actual=result, expected=expected_error)


class TestLoadRuntimeJson(_Asserts):
    """
    Unit tests for the _load_json_resource helper.
    """

    def setUp(self):
        """
        Create a temporary runtime directory and (for forward compatibility) patch _resolve_json_resource_path to resolve into this directory.
        """
        self.tmpdir = tempfile.mkdtemp(prefix="runtime_json_")
        self.orig_resolver = jc._resolve_json_resource_path

        # Patch the path resolver to always return a file within our temp directory.
        def _resolver(resource_name: str):
            filename = resource_name + utils.JSON_FILE_EXT
            return os.path.join(self.tmpdir, filename)

        jc._resolve_json_resource_path = _resolver  # simple, library-free patch

        # Convenience: name for our resource (e.g., "_info")
        self.resource = "_test_resource"
        self.filename = self.resource + utils.JSON_FILE_EXT
        self.filepath = os.path.join(self.tmpdir, self.filename)

    def tearDown(self):
        """
        Restore the original resolver and remove temp files.
        """
        jc._resolve_json_resource_path = self.orig_resolver
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_valid(self):
        """
        Should return payload data when the JSON file exists and checksum is valid.
        """
        # ARRANGE
        payload = {"APP_NAME": "MyApp", "WELCOME": "Hello"}
        packet = utils.create_json_packet(payload, source_file=self.filename)
        utils.save_json_file(self.filepath, packet)
        expected = payload

        # ACT
        actual = jc._load_json_resource(self.resource, self.filepath)

        # ASSERT
        self.assert_equal(actual=actual, expected=expected)

    def test_missing_json(self):
        """
        Should raise RuntimeError when the JSON file does not exist.
        """
        # ARRANGE
        expected = RuntimeError.__name__

        # ACT
        try:
            _ = jc._load_json_resource(self.resource, self.filepath)
            actual = ""  # Unexpected: no exception
        except Exception as e:
            actual = type(e).__name__

        # ASSERT
        self.assert_equal(actual=actual, expected=expected)

    def test_corrupt_json(self):
        """
        Should raise ValueError when checksum verification fails.
        """
        # ARRANGE
        payload = {"APP_NAME": "MyApp", "WELCOME": "Hello"}
        packet = utils.create_json_packet(payload, source_file=self.filename)
        utils.save_json_file(self.filepath, packet)
        expected = ValueError.__name__

        with patch.object(utils, "verify_json_payload_checksum") as p_checksum_ok:
            p_checksum_ok.return_value = False

            # ACT
            try:
                _ = jc._load_json_resource(self.resource, self.filepath)
                actual = ""  # Unexpected: no exception
            except Exception as e:
                actual = type(e).__name__

        # ASSERT
        self.assert_equal(actual=actual, expected=expected)

    def test_empty_json(self):
        """
        Should raise ValueError when the JSON payload is empty.
        """
        # ARRANGE
        payload = {}  # empty
        packet_data = utils.create_json_packet(payload, source_file=self.filename)
        utils.save_json_file(self.filepath, packet_data)

        expected = ValueError.__name__

        # ACT
        try:
            _ = jc._load_json_resource(self.resource, self.filepath)
            actual = ""  # Unexpected: no exception
        except Exception as e:
            actual = type(e).__name__

            # ASSERT
        self.assert_equal(actual=actual, expected=expected)


class TestResolveJsonFilePath(_Asserts):
    """
    Unit tests for _resolve_json_resource_path function.
    """

    def setUp(self):
        """
        Create a temporary directory to act as the runtime folder.
        """
        # Create a unique temporary root directory
        self.tmp_root = tempfile.mkdtemp(prefix="runtime_tmp_")

        # Create folders inside temp root
        self.tmp_runtime = os.path.join(self.tmp_root, TEST_RESOURCE_FOLDER_PARTS[0], TEST_RESOURCE_FOLDER_PARTS[1])
        os.makedirs(self.tmp_runtime, exist_ok=True)

    def tearDown(self):
        """
        Remove the temporary directory after tests.
        """
        shutil.rmtree(self.tmp_root, ignore_errors=True)

    def test_file_exists(self):
        """
        Should return the JSON file path when the resource file exists.
        """
        # ARRANGE
        resource = "test_resource"
        filename = TEST_RESOURCE_PREFIX + resource + utils.JSON_FILE_EXT
        expected_path = os.path.join(self.tmp_runtime, filename)

        with open(expected_path, "w", encoding="utf-8") as f:
            f.write('{"meta": {}, "data": {}}')

        # path project root to temp
        with patch.object(utils, "find_root_folder") as p_root:
            p_root.return_value = self.tmp_root

            # ACT
            result = jc._resolve_json_resource_path(resource, TEST_RESOURCE_FOLDER_PARTS)

        # ASSERT
        self.assert_equal(actual=result, expected=expected_path)

    def test_file_missing(self):
        """
        Should raise error when the resource file is absent.
        """
        # ARRANGE
        resource = "test_resource"
        expected_error = FileNotFoundError.__name__

        # ACT
        try:
            # path project root to temp
            with patch.object(utils, "find_root_folder") as p_root:
                p_root.return_value = self.tmp_root
                _ = jc._resolve_json_resource_path(resource, TEST_RESOURCE_FOLDER_PARTS)
            result = ""  # No exception raised (unexpected)
        except Exception as e:
            result = type(e).__name__

        # ASSERT
        self.assert_equal(actual=result, expected=expected_error)


if __name__ == "__main__":
    unittest.main()
