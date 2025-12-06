"""
Unit tests for the JSON-backed temporary settings cache and singleton accessor.

This module verifies that:
    - The Settings cache creates and maintains the temporary_settings.json file
    - REQUIRED_KEYS are initialized with DEFAULT_TEMP_SETTINGS values
    - set_value and get_value update and retrieve cache entries and persist them to disk
    - Invalid keys raise ValueError
    - get_cache_reference returns a singleton Settings instance that can reload persisted values

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
from typing import Any
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
        for key in ts.REQUIRED_KEYS:
            default_settings_map[key] = ts.DEFAULT_TEMP_SETTINGS.get(key, "")

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


class TestTemporarySettings(_Fixture):
    """
    Unit tests for the `Settings` JSON-backed temporary settings cache.
    """

    def test_create_file_when_missing(self) -> None:
        """
        Should create the temporary settings JSON file when it does not exist.
        """
        # ARRANGE
        os.remove(self.resource_path)
        exists_before = os.path.exists(self.resource_path)
        with self.subTest("No file exists", Out=exists_before, Exp=False):
            self.assertFalse(exists_before)

        # ACT
        _ = ts.TemporarySettingsCache()

        # ASSERT
        exists_after = os.path.exists(self.resource_path)
        with self.subTest("File created", Out=exists_after, Exp=True):
            self.assertTrue(exists_after)

    def test_populate_required_keys(self) -> None:
        """
        Should populate all REQUIRED_KEYS into the JSON payload on initialization.
        """
        # ARRANGE
        os.remove(self.resource_path)
        settings = ts.TemporarySettingsCache()  # noqa: F841  # force creation

        # ACT
        packet = json_io.load_json_file(self.resource_path)
        payload: dict[str, Any] = json_io.extract_payload(packet)
        actual_keys = tuple(sorted(payload.keys()))
        expected_keys = ts.REQUIRED_KEYS

        # ASSERT
        with self.subTest(Out=actual_keys, Exp=expected_keys):
            self.assertEqual(actual_keys, expected_keys)

    def test_populate_default_values(self) -> None:
        """
        Should initialize each REQUIRED_KEYS entry in JSON to DEFAULT_TEMP_SETTINGS.
        """
        # ARRANGE
        os.remove(self.resource_path)
        settings = ts.TemporarySettingsCache()  # noqa: F841

        # ACT
        packet = json_io.load_json_file(self.resource_path)
        payload: dict[str, Any] = json_io.extract_payload(packet)

        # ASSERT
        for key in ts.REQUIRED_KEYS:
            actual_value = payload.get(key)
            expected_value = ts.DEFAULT_TEMP_SETTINGS.get(key, "")
            with self.subTest(Key=key, Out=actual_value, Exp=expected_value):
                self.assertEqual(actual_value, expected_value)

    def test_cache_keys_match(self) -> None:
        """
        Should expose the same REQUIRED_KEYS via the in-memory cache API.
        """
        # ARRANGE
        settings = ts.TemporarySettingsCache()

        # ACT
        cache_keys = settings.get_keys()
        expected_keys = ts.REQUIRED_KEYS

        # ASSERT
        with self.subTest(Out=cache_keys, Exp=expected_keys):
            self.assertEqual(cache_keys, expected_keys)

    def test_set_value(self) -> None:
        """
        Should update the in-memory cache values for the specified keys.
        """
        # ARRANGE
        settings = ts.TemporarySettingsCache()
        new_source = os.path.join(self.temp_folder, "src_folder")
        new_dest = os.path.join(self.temp_folder, "dest_folder")

        # ACT
        settings.set_value(ts.KEYS.SOURCE_FILES_FOLDER, new_source)
        settings.set_value(ts.KEYS.DESTINATION_FILES_FOLDER, new_dest)

        # ASSERT
        actual_source = settings.get_value(ts.KEYS.SOURCE_FILES_FOLDER, str)
        actual_dest = settings.get_value(ts.KEYS.DESTINATION_FILES_FOLDER, str)

        with self.subTest(Out=actual_source, Exp=new_source):
            self.assertEqual(actual_source, new_source)
        with self.subTest(Out=actual_dest, Exp=new_dest):
            self.assertEqual(actual_dest, new_dest)

    def test_set_value_persist(self) -> None:
        """
        Should persist updated values to the JSON file on disk.
        """
        # ARRANGE
        settings = ts.TemporarySettingsCache()
        new_source = os.path.join(self.temp_folder, "src_folder_disk")
        new_dest = os.path.join(self.temp_folder, "dest_folder_disk")

        # ACT
        settings.set_value(ts.KEYS.SOURCE_FILES_FOLDER, new_source)
        settings.set_value(ts.KEYS.DESTINATION_FILES_FOLDER, new_dest)

        packet = json_io.load_json_file(self.resource_path)
        payload: dict[str, Any] = json_io.extract_payload(packet)
        disk_source = payload.get(ts.KEYS.SOURCE_FILES_FOLDER)
        disk_dest = payload.get(ts.KEYS.DESTINATION_FILES_FOLDER)

        # ASSERT
        with self.subTest(Out=disk_source, Exp=new_source):
            self.assertEqual(disk_source, new_source)
        with self.subTest(Out=disk_dest, Exp=new_dest):
            self.assertEqual(disk_dest, new_dest)

    def test_raise_on_invalid_key(self) -> None:
        """
        Should raise ValueError when attempting to set a key that is not in REQUIRED_KEYS.
        """
        # ARRANGE
        settings = ts.TemporarySettingsCache()
        invalid_key = "NOT_A_VALID_TEMP_KEY"
        expected_error = ValueError.__name__

        # ACT
        try:
            settings.set_value(invalid_key, "some-value")
            actual_error = ""  # No exception raised (unexpected)
        except ValueError as exc:
            actual_error = type(exc).__name__

        # ASSERT
        with self.subTest(Out=actual_error, Exp=expected_error):
            self.assertEqual(actual_error, expected_error)


class TestGetCacheReferenceSingleton(_Fixture):
    """
    Unit tests for the `get_cache_reference` singleton accessor.
    """

    def test_create(self) -> None:
        """
        Should create the temporary settings file when one does not exist.
        """
        # ARRANGE
        os.remove(self.resource_path)
        expected = ts.DEFAULT_TEMP_SETTINGS[ts.KEYS.SOURCE_FILES_FOLDER]  # Any key to test

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
        expected_type = ts.TemporarySettingsCache.__name__
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
        first.set_value(ts.KEYS.SOURCE_FILES_FOLDER, updated_value)

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
