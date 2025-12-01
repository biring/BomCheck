"""
Unit tests for internal lookup resource loaders.

These tests validate the behavior of the private loader functions in `src.lookups._resources`, including initialization, error propagation, and correct construction of JsonCache instances.

Example Usage:
    # Preferred usage via project-root invocation:
    python -m unittest tests/lookups/test__resources.py

    # Direct discovery:
    python -m unittest discover -s tests

Dependencies:
    - Python >= 3.10
    - Standard Library: unittest, tempfile, shutil, importlib, pathlib, json
    - Internal Modules: src.lookups._resources, src.lookups._constants, src.utils

Notes:
    - Uses patching to isolate and count loader invocations.
    - Writes temporary JSON packets to validate that JsonCache loads data exactly as written.
    - Ensures errors from JsonCache construction are wrapped as RuntimeError.
    - Temporary directories prevent contamination of actual lookup resource folders.

License:
    - Internal Use Only
"""

import importlib
import shutil
import tempfile
import unittest
from unittest.mock import patch

import src.utils as util
from src.utils import folder_path
from src.utils import json_io

# noinspection PyProtectedMember
from src.lookups import _resources as resource  # Module under test

# noinspection PyProtectedMember
from src.lookups import _constants as constant


class TestLoadSettingsCache(unittest.TestCase):
    """
    Unit tests for the `load_settings_cache` function.
    """

    def test_component_type(self):
        """
        Should load component type cache once when loading settings caches.
        """
        # ARRANGE
        expected = 1

        # Patch the internal loader so we can count invocations
        with patch.object(resource, "_load_component_type_cache") as mocked_loader:
            # ACT
            resource.load_cache()
            result = mocked_loader.call_count

        # ASSERT
        with self.subTest(Out=result, Exp=expected):
            self.assertEqual(result, expected)


class TestLoadComponentTypeCache(unittest.TestCase):
    """
    Unit tests for the internal `_load_component_type_cache` function.
    """

    TEST_JSON_DATA = {
        "Alpha": "A",
        "Beta": "B",
        "Delta": "D",
        "Gamma": "G",
        "List": ["1", "2"],
    }

    tmp_project_root: str | None = None

    def setUp(self):
        """
        Prepare a temporary project root and write a single component-type JSON packet.
        """
        # Reload module to reset the module-level cache to None
        importlib.reload(resource)

        # Create an isolated project root; removed in tearDown()
        self.tmp_project_root = tempfile.mkdtemp(prefix="runtime_tmp_")

        # Mirror the on-disk runtime layout used by production code
        runtime_dir = folder_path.construct_folder_path(
            self.tmp_project_root,
            constant.FOLDER_PARTS,
        )
        folder_path.create_folder_if_missing(runtime_dir)

        # Build resource file paths and names
        resource_filename = (
                constant.JSON_PREFIX
                + constant.COMPONENT_TYPE_FILE_NAME
                + util.json_io.JSON_FILE_EXT
        )
        resource_path = util.file_path.construct_file_path(runtime_dir, resource_filename)

        # Wrap the payload in the standard packet envelope expected by the loader
        resource_packet = json_io.create_json_packet(
            self.TEST_JSON_DATA,
            source_file=resource_filename,
        )

        # Persist the packet where JsonCache will look for it
        json_io.save_json_file(resource_path, resource_packet)

    def tearDown(self):
        """
        Remove the temporary project root and all generated files.
        """
        # Best-effort cleanup to avoid leaking temp files on test failures
        if self.tmp_project_root is not None:
            shutil.rmtree(self.tmp_project_root, ignore_errors=True)

    def test_happy_path(self):
        """
        Should construct a JsonCache and populate the data map from the on-disk packet.
        """
        # ARRANGE
        expected_map = self.TEST_JSON_DATA

        # Force JsonCache to resolve its root under the temporary project root
        with patch.object(folder_path, "resolve_project_folder") as p_root:
            p_root.return_value = self.tmp_project_root

            # ACT
            resource._load_component_type_cache()
            actual_map = resource._component_type_cache.get_data_map_copy()

        # ASSERT
        with self.subTest(Out=actual_map, Exp=expected_map):
            self.assertDictEqual(actual_map, expected_map)

    def test_raise(self):
        """
        Should wrap any underlying JsonCache construction error as RuntimeError.
        """
        # ARRANGE
        expected_error = RuntimeError.__name__

        # Replace JsonCache with a stub that always raises an error
        with patch.object(resource, "JsonCache") as mock_cache_ctor:
            mock_cache_ctor.side_effect = ValueError("boom")

            # ACT
            try:
                resource._load_component_type_cache()
                actual_error = ""
            except Exception as exc:  # noqa: BLE001
                actual_error = type(exc).__name__

        # ASSERT
        with self.subTest(Out=actual_error, Exp=expected_error):
            self.assertEqual(actual_error, expected_error)


class TestGetComponentTypeCache(unittest.TestCase):
    """
    Unit tests for the `get_component_type_cache` accessor.
    """

    def setUp(self):
        """
        Reload the module before each test to reset the module-level cache.
        """
        importlib.reload(resource)

    def test_happy_path(self):
        """
        Should return the initialized JsonCache instance after `_load_component_type_cache` runs.
        """
        # ARRANGE
        # Patch JsonCache so we can control and observe the instance returned
        fake_cache = object()

        with (
            patch.object(resource, "JsonCache") as mock_cache_ctor,
            patch.object(folder_path, "resolve_project_folder") as p_root
        ):
            # We do not care about disk access here; root folder can be any placeholder
            p_root.return_value = tempfile.mkdtemp(prefix="runtime_tmp_root_")

            mock_cache_ctor.return_value = fake_cache

            # ACT
            resource._load_component_type_cache()
            result = resource.get_component_type_cache()

        # ASSERT
        with self.subTest(Out=result, Exp=fake_cache):
            self.assertIs(result, fake_cache)

    def test_raise(self):
        """
        Should raise if cache is accessed before initialization.
        """
        # ARRANGE
        expected_error = RuntimeError.__name__

        # ACT
        try:
            resource.get_component_type_cache()
            actual_error = ""
        except Exception as exc:  # noqa: BLE001
            actual_error = type(exc).__name__

        # ASSERT
        with self.subTest(Out=actual_error, Exp=expected_error):
            self.assertEqual(actual_error, expected_error)


if __name__ == "__main__":
    unittest.main()
