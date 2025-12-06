"""
Unit tests for the read/write JSON cache wrapper (CacheReadWrite).

This module verifies that CacheReadWrite:
    - Creates a new JSON cache file when none exists
    - Populates required keys and default values on initialization
    - Provides correct key/value access through get_value() and get_keys()
    - Persists updates via set_value() and enforces allowed keys
    - Maintains a clean, isolated environment through temp-folder fixtures

Example Usage:
    # Run this specific test module:
    python -m unittest tests.common.test__cache_read_write

    # Run the full test suite (includes this module):
    python -m unittest discover -s tests

Dependencies:
    - Python >= 3.10
    - Standard Library: unittest, tempfile, shutil, os
    - External Packages: None
    - Internal Modules Under Test: src.common._cache_read_write, src.utils.folder_path, src.utils.json_io

Notes:
    - A patched temp-folder path isolates the file system per test.
    - Tests validate behavior, not internal implementation details of CacheReadWrite.
    - Singleton module-level cache is reset before and after each test for correctness.

License:
    - Internal Use Only
"""
import os
import shutil
import tempfile
import unittest
from dataclasses import dataclass, asdict

from typing import Any
from unittest.mock import patch

from src.utils import folder_path
from src.utils import json_io

# noinspection PyProtectedMember
from src.common import _cache_read_write as crw  # module under test


@dataclass(frozen=True)
class _TestKeys:
    TEST_LIST: str = "TEST_LIST"
    TEST_STRING: str = "TEST_STRING"


# MODULE_CONSTANTS
_KEYS = _TestKeys()
_TEST_FOLDER_PREFIX: str = "test_crw_"
_TEST_RESOURCE_NAME: str = "test_resource"
_TEST_REQ_KEYS: tuple[str, ...] = tuple(sorted(asdict(_KEYS).values()))
_TEST_DEFAULT_VALUES: dict[str, Any] = {
    _KEYS.TEST_LIST: ['cat', 'dog', 'horse'],
    _KEYS.TEST_STRING: "List of animals",
}


class _Fixture(unittest.TestCase):
    """
    Test fixture providing an isolated temporary folder and patched environment for CacheReadWrite tests.
    """

    def setUp(self) -> None:
        # ARRANGE
        # Create an isolated temp directory for this test case
        self.temp_folder = tempfile.mkdtemp(prefix=_TEST_FOLDER_PREFIX)

        # Patch get_temp_folder() to point at our temp dir
        self._patcher_temp = patch.object(folder_path, "get_temp_folder", return_value=self.temp_folder)
        self._patcher_temp.start()

        # Pre-compute the expected JSON file path for temporary settings
        resource_filename = _TEST_RESOURCE_NAME + json_io.JSON_FILE_EXT
        self.resource_path = os.path.join(self.temp_folder, resource_filename)

        # Reset the module-level singleton cache before each test
        crw._temporary_settings_cache = None

        # Generate default payload for temporary settings file
        default_settings_map: dict[str, str] = {}
        for key in _TEST_REQ_KEYS:
            default_settings_map[key] = _TEST_DEFAULT_VALUES.get(key, "")

        # Wrap the raw key-value map in a metadata packet (e.g., version, checksum) before saving
        json_packet = json_io.create_json_packet(default_settings_map, resource_filename)
        json_io.save_json_file(self.resource_path, json_packet, indent_spaces=4)

    def tearDown(self) -> None:
        # Stop the patch
        self._patcher_temp.stop()

        # Clear temporary folder
        shutil.rmtree(self.temp_folder, ignore_errors=True)

        # Reset the module-level singleton cache after each test
        crw._temporary_settings_cache = None


class TestCacheReadWrite(_Fixture):
    """
    Unit test for the CacheReadWrite read/write JSON cache.
    """

    def test_create_file_when_missing(self) -> None:
        """
        Should create a new JSON cache file when none exists.
        """
        # ARRANGE
        os.remove(self.resource_path)
        exists_before = os.path.exists(self.resource_path)
        with self.subTest("No file exists", Out=exists_before, Exp=False):
            self.assertFalse(exists_before)

        # ACT
        _ = crw.CacheReadWrite(
            resource_folder_path=self.temp_folder,
            resource_name=_TEST_RESOURCE_NAME,
            required_keys=_TEST_REQ_KEYS,
            default_values=_TEST_DEFAULT_VALUES,
        )

        # ASSERT
        exists_after = os.path.exists(self.resource_path)
        with self.subTest("File created", Out=exists_after, Exp=True):
            self.assertTrue(exists_after)

    def test_populate_required_keys(self) -> None:
        """
        Should populate all required keys when creating a new cache file.
        """
        # ARRANGE
        os.remove(self.resource_path)
        settings = crw.CacheReadWrite(
            resource_folder_path=self.temp_folder,
            resource_name=_TEST_RESOURCE_NAME,
            required_keys=_TEST_REQ_KEYS,
            default_values=_TEST_DEFAULT_VALUES,
        )

        # ACT
        packet = json_io.load_json_file(self.resource_path)
        payload: dict[str, Any] = json_io.extract_payload(packet)
        actual_keys = tuple(sorted(payload.keys()))
        expected_keys = _TEST_REQ_KEYS

        # ASSERT
        with self.subTest(Out=actual_keys, Exp=expected_keys):
            self.assertEqual(actual_keys, expected_keys)

    def test_populate_default_values(self) -> None:
        """
        Should apply default values for all required keys.
        """
        # ARRANGE
        os.remove(self.resource_path)
        settings = crw.CacheReadWrite(
            resource_folder_path=self.temp_folder,
            resource_name=_TEST_RESOURCE_NAME,
            required_keys=_TEST_REQ_KEYS,
            default_values=_TEST_DEFAULT_VALUES,
        )

        # ACT
        packet = json_io.load_json_file(self.resource_path)
        payload: dict[str, Any] = json_io.extract_payload(packet)

        # ASSERT
        for key in _TEST_REQ_KEYS:
            actual_value = payload.get(key)
            expected_value = _TEST_DEFAULT_VALUES.get(key, "")
            with self.subTest(Key=key, Out=actual_value, Exp=expected_value):
                self.assertEqual(actual_value, expected_value)

    def test_cache_keys_match(self) -> None:
        """
        Should return all required keys through get_keys().
        """
        # ARRANGE
        settings = crw.CacheReadWrite(
            resource_folder_path=self.temp_folder,
            resource_name=_TEST_RESOURCE_NAME,
            required_keys=_TEST_REQ_KEYS,
            default_values=_TEST_DEFAULT_VALUES,
        )
        # ACT
        cache_keys = settings.get_keys()
        expected_keys = _TEST_REQ_KEYS

        # ASSERT
        with self.subTest(Out=cache_keys, Exp=expected_keys):
            self.assertEqual(cache_keys, expected_keys)

    def test_set_value(self) -> None:
        """
        Should update in-memory values through update_value().
        """
        # ARRANGE
        settings = crw.CacheReadWrite(
            resource_folder_path=self.temp_folder,
            resource_name=_TEST_RESOURCE_NAME,
            required_keys=_TEST_REQ_KEYS,
            default_values=_TEST_DEFAULT_VALUES,
        )
        new_list = ['Boston', 'New York', 'Dallas']
        new_string = "List of cities"

        # ACT
        settings.update_value(_KEYS.TEST_LIST, new_list)
        settings.update_value(_KEYS.TEST_STRING, new_string)

        # ASSERT
        actual_list = settings.get_value(_KEYS.TEST_LIST, list)
        actual_string = settings.get_value(_KEYS.TEST_STRING, str)

        with self.subTest(Out=actual_list, Exp=new_list):
            self.assertEqual(actual_list, new_list)
        with self.subTest(Out=actual_string, Exp=new_string):
            self.assertEqual(actual_string, new_string)

    def test_set_value_persist(self) -> None:
        """
        Should persist updated values to disk after update_value().
        """
        # ARRANGE
        settings = crw.CacheReadWrite(
            resource_folder_path=self.temp_folder,
            resource_name=_TEST_RESOURCE_NAME,
            required_keys=_TEST_REQ_KEYS,
            default_values=_TEST_DEFAULT_VALUES,
        )
        new_list = ['Boston', 'New York', 'Dallas']
        new_string = "List of cities"

        # ACT
        settings.update_value(_KEYS.TEST_LIST, new_list)
        settings.update_value(_KEYS.TEST_STRING, new_string)

        packet = json_io.load_json_file(self.resource_path)
        payload: dict[str, Any] = json_io.extract_payload(packet)
        disk_list = payload.get(_KEYS.TEST_LIST)
        disk_string = payload.get(_KEYS.TEST_STRING)

        # ASSERT
        with self.subTest(Out=disk_list, Exp=new_list):
            self.assertEqual(disk_list, new_list)
        with self.subTest(Out=disk_string, Exp=new_string):
            self.assertEqual(disk_string, new_string)

    def test_raise_on_invalid_key(self) -> None:
        """
        Should raise ValueError when updating a key not in required_keys.
        """
        # ARRANGE
        settings = crw.CacheReadWrite(
            resource_folder_path=self.temp_folder,
            resource_name=_TEST_RESOURCE_NAME,
            required_keys=_TEST_REQ_KEYS,
            default_values=_TEST_DEFAULT_VALUES,
        )
        invalid_key = "NOT_A_VALID_TEMP_KEY"
        expected_error = ValueError.__name__

        # ACT
        try:
            settings.update_value(invalid_key, "some-value")
            actual_error = ""  # No exception raised (unexpected)
        except ValueError as exc:
            actual_error = type(exc).__name__

        # ASSERT
        with self.subTest(Out=actual_error, Exp=expected_error):
            self.assertEqual(actual_error, expected_error)


if __name__ == '__main__':
    unittest.main()
