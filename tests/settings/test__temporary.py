"""
Unit tests for the JSON-backed temporary settings cache and singleton accessor.

This module verifies that:
    - The temporary settings cache creates and maintains the temporary_settings.json file
    - All required keys are initialized with values from _DEFAULT_TEMP_SETTINGS
    - get_value retrieves cache entries from the JSON-backed cache
    - update_value persists updated entries to disk
    - get_temp_settings() returns a singleton cache instance that can reload persisted values

Example Usage:
    # Preferred usage via project-root invocation:
    python -m unittest tests.settings.test__temporary

    # Direct discovery (runs all tests, including this module):
    python -m unittest discover -s tests

Dependencies:
    - Python >= 3.10
    - Standard Library: os, shutil, tempfile, unittest, unittest.mock, typing
    - Internal Packages: src.utils.folder_path, src.utils.json_io, src.settings._temporary

Notes:
    - Tests patch folder_path.get_temp_folder to isolate each test in its own temporary directory.
    - The module-level _temporary_settings_cache is reset in setUp and tearDown to validate singleton behavior.
    - JSON files are created via json_io helpers to include metadata packets (e.g., version and checksum) around the payload.

License:
    - Internal Use Only
"""

import os
import shutil
import tempfile
import unittest
from unittest.mock import patch

from src.utils import folder_path
from src.utils import json_io

# noinspection PyProtectedMember
from src.settings import _temporary as ts  # module under test


class _Fixture(unittest.TestCase):
    """
    Test fixture that isolates temporary settings in a per-test temporary directory.
    """

    def setUp(self) -> None:
        """
        Set up an isolated temp directory and reset the temporary settings singleton cache.
        """
        # ARRANGE
        # Create an isolated temp directory for this test case
        self.temp_folder = tempfile.mkdtemp(prefix=ts._TEMP_FILE_NAME)

        # Patch get_temp_folder() to point at our temp dir
        self._patcher_temp = patch.object(folder_path, "get_temp_folder", return_value=self.temp_folder)
        self._patcher_temp.start()

        # Pre-compute the expected JSON file path for temporary settings
        resource_filename = ts._TEMP_FILE_NAME + json_io.JSON_FILE_EXT
        self.resource_path = os.path.join(self.temp_folder, resource_filename)

        # Reset the module-level singleton cache before each test
        ts._temporary_settings_cache = None

        # Generate default payload for temporary settings file
        default_settings_map: dict[str, str] = {}
        for key in ts._REQUIRED_KEYS:
            default_settings_map[key] = ts._DEFAULT_TEMP_SETTINGS.get(key, "")

        # Wrap the raw key-value map in a metadata packet (e.g., version, checksum) before saving
        json_packet = json_io.create_json_packet(default_settings_map, resource_filename)
        json_io.save_json_file(self.resource_path, json_packet, indent_spaces=4)

    def tearDown(self) -> None:
        """
        Tear down the temporary directory and clear the temporary settings singleton cache.
        """
        # Stop the patch
        self._patcher_temp.stop()

        # Clear temporary folder
        shutil.rmtree(self.temp_folder, ignore_errors=True)

        # Reset the module-level singleton cache after each test
        ts._temporary_settings_cache = None


class TestGetCacheReferenceSingleton(_Fixture):
    """
    Unit tests for the `get_temp_settings` singleton accessor.
    """

    def test_create(self) -> None:
        """
        Should create the temporary settings file when one does not exist.
        """
        # ARRANGE
        os.remove(self.resource_path)
        expected = ts._DEFAULT_TEMP_SETTINGS[ts.KEYS.SOURCE_FILES_FOLDER]  # Any key to test

        # ACT
        cache = ts.get_temp_settings()
        actual = cache.get_value(ts.KEYS.SOURCE_FILES_FOLDER, str)

        # ASSERT
        with self.subTest(Out=actual, Exp=expected):
            self.assertEqual(actual, expected)

    def test_singleton(self) -> None:
        """
        Should return the same Settings instance when called multiple times.
        """
        # ARRANGE
        # Singleton cache is reset in setUp.

        # ACT
        first = ts.get_temp_settings()
        second = ts.get_temp_settings()

        # ASSERT
        same_identity = first is second
        with self.subTest(Out=same_identity, Exp=True):
            self.assertTrue(same_identity)

        instance_type = type(first).__name__
        expected_type = type(ts.get_temp_settings()).__name__
        with self.subTest(Out=instance_type, Exp=expected_type):
            self.assertEqual(instance_type, expected_type)

    def test_persist(self) -> None:
        """
        Should persist values to disk so that a new singleton instance can reload them after cache reset.
        """
        # ARRANGE
        first = ts.get_temp_settings()
        updated_value = os.path.join(self.temp_folder, "reloaded_src")

        # ACT
        # Update a key via the first singleton instance
        first.update_value(ts.KEYS.SOURCE_FILES_FOLDER, updated_value)

        # Simulate a fresh process by clearing the module-level cache
        ts._temporary_settings_cache = None

        # Create a new singleton instance, which should reload from disk
        second = ts.get_temp_settings()
        actual_value = second.get_value(ts.KEYS.SOURCE_FILES_FOLDER, str)

        # ASSERT
        with self.subTest(Out=actual_value, Exp=updated_value):
            self.assertEqual(actual_value, updated_value)


if __name__ == "__main__":
    unittest.main()
