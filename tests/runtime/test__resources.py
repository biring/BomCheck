import importlib
import os
import shutil
import tempfile
import unittest
from typing import Any
from unittest.mock import patch, PropertyMock

# noinspection PyProtectedMember
from src.runtime import _resources as resources  # Module under test

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


class _TestFixture:
    """
    Test fixture that provisions a temporary runtime root with a JSON resource and cleans it up.
    """

    tmp_project_root: str = None

    def set_up(self, resource_name: str):
        """
        Prepare a temporary project root and runtime folder, write a JSON resource packet, and create a Cache under test.
        """
        # Reload module to clear memory
        importlib.reload(resources)

        # Create an isolated project root; deleted in tearDown()
        self.tmp_project_root = tempfile.mkdtemp(prefix="runtime_tmp_")

        # Mirror the on-disk runtime layout used by production code
        runtime_dir = utils.construct_folder_path(self.tmp_project_root, hlp.RUNTIME_FOLDER)
        os.makedirs(runtime_dir, exist_ok=True)

        # Build resource file paths and names
        resource_filename = hlp.RUNTIME_JSON_PREFIX + resource_name + utils.JSON_FILE_EXT
        resource_path = os.path.join(runtime_dir, resource_filename)

        # Wrap the payload in the standard packet envelope expected by the loader
        resource_packet = utils.create_json_packet(TEST_DATA_JSON, source_file=resource_filename)

        # Persist the packet where Cache.load() will look for it
        utils.save_json_file(resource_path, resource_packet)

    def tear_down(self):
        """
        Remove the temporary project root and all generated files.
        """
        # Best-effort cleanup to avoid leaking temp files on test failures
        shutil.rmtree(self.tmp_project_root, ignore_errors=True)


class TestLoadAllResources(_Asserts):
    """
    Unit test for the `load_all_resources` function.

    Focus: Ensure it triggers each category loader (currently: component type).
    """

    def test_invokes_component_type_loader(self):
        """
        Should call the internal `_load_component_type` exactly once.
        """
        # ARRANGE
        expected = 1

        with patch.object(resources, "_load_component_type") as mocked_loader:
            # ACT
            resources.load_all_resources()
            result = mocked_loader.call_count

            # ASSERT
            self.assert_equal(actual=result, expected=expected)


class TestLoadComponentType(_Asserts, _TestFixture):
    """
    Unit test for the `_load_component_type` function.
    """

    def setUp(self):
        self.set_up(resources.COMPONENT_TYPE_SOURCE)

    def tearDown(self):
        self.tear_down()

    def test_valid(self):
        """
        Should load runtime resources.
        """
        # ARRANGE
        expected_map = TEST_DATA_JSON

        with patch.object(utils, "find_root_folder") as p_root:
            p_root.return_value = self.tmp_project_root
            # ACT
            resources._load_component_type()
            actual_map = resources.component_type_cache.data_map

        # ASSERT
        self.assert_equal(actual=actual_map, expected=expected_map)

    def test_not_loaded(self):
        """
        Should raise when resource fails to load.
        """
        # ARRANGE
        expected_error = RuntimeError.__name__

        # ACT
        try:
            resources._load_component_type()
            actual_error = ""
        except Exception as e:
            actual_error = type(e).__name__

        # ASSERT
        self.assert_equal(actual=actual_error, expected=expected_error)


class TestGetComponentTypeKeys(_Asserts, _TestFixture):
    """
    Unit test for the `get_component_type_keys` function.
    """

    def setUp(self):
        self.set_up(resources.COMPONENT_TYPE_SOURCE)

    def tearDown(self):
        self.tear_down()

    def test_valid(self):
        """
        Should return an immutable tuple of keys after successful load.
        """
        # ARRANGE
        expected_all_keys = tuple(TEST_DATA_JSON.keys())

        with patch.object(utils, "find_root_folder") as p_root:
            p_root.return_value = self.tmp_project_root
            # ACT
            resources._load_component_type()
            actual_all_keys = resources.get_component_type_keys()

        # ASSERT
        self.assert_equal(actual=actual_all_keys, expected=expected_all_keys)

    def test_invalid(self):
        """
        Should raise if keys are requested before the resource is loaded.
        """
        # ARRANGE
        expected_error = RuntimeError.__name__

        # clean load of resource
        with patch.object(utils, "find_root_folder") as p_root:
            p_root.return_value = self.tmp_project_root
            resources._load_component_type()

        # ACT
        with patch.object(type(resources.component_type_cache), "data_map", new_callable=PropertyMock) as p_map:
            p_map.return_value = None
            try:
                _ = resources.get_component_type_keys()
                actual_error = ""
            except Exception as e:
                actual_error = type(e).__name__
                print(e)

        # ASSERT
        self.assert_equal(actual=actual_error, expected=expected_error)


class TestGetComponentTypeValues(_Asserts, _TestFixture):
    """
    Unit test for the `get_component_type_values` function.
    """

    def setUp(self):
        self.set_up(resources.COMPONENT_TYPE_SOURCE)

    def tearDown(self):
        self.tear_down()

    def test_valid(self):
        """
        Should return an immutable tuple of value for the request key.
        """
        # ARRANGE
        requested_value_key = "Alpha"
        expected_value = tuple("A")

        with patch.object(utils, "find_root_folder") as p_root:
            p_root.return_value = self.tmp_project_root
            # ACT
            resources._load_component_type()
            actual_value = resources.get_component_type_values(requested_value_key)

        # ASSERT
        self.assert_equal(actual=actual_value, expected=expected_value)

    def test_invalid(self):
        """
        Should raise when the requested key does not exist in the resource.
        """
        # ARRANGE
        requested_value_key = "InvalidName"
        expected_error = RuntimeError.__name__

        with patch.object(utils, "find_root_folder") as p_root:
            p_root.return_value = self.tmp_project_root
            # ACT
            resources._load_component_type()
            try:
                _ = resources.get_component_type_values(requested_value_key)
                actual_error = ""
            except Exception as e:
                actual_error = type(e).__name__

        # ASSERT
        self.assert_equal(actual=actual_error, expected=expected_error)


if __name__ == "__main__":
    unittest.main()
