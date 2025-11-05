"""
Unit tests for the public runtime interfaces module.

These tests validate that the runtime interface:
    - Exposes stable public constants that mirror internal helpers
    - Loads component-type JSON resources correctly through the public API
    - Returns accurate keys and normalized tuple[str] values
    - Raises RuntimeError for invalid or missing keys

Example Usage:
    # Preferred usage via unittest discovery:
    python -m unittest tests/runtime/test_interfaces.py

    # Run all runtime interface tests:
    python -m unittest discover -s tests/runtime

Dependencies:
    - Python >= 3.10
    - Standard Library: unittest, importlib, tempfile, shutil, typing, os
    - Internal Modules: src.runtime.interfaces, src.runtime._resources, src.runtime._helpers, src.utils

Notes:
    - Tests simulate real runtime folder creation using temporary directories.
    - Public API is exercised end-to-end without patching internal modules.
    - Error conditions are verified with safe RuntimeError assertions.
    - Designed to ensure forward compatibility of the runtime interface layer.

License:
    - Internal Use Only
"""
import importlib
import os
import shutil
import tempfile
import unittest
from typing import Any
from unittest.mock import patch
import src.utils as utils  # Internal helpers used only for temp file creation
# noinspection PyProtectedMember
import src.runtime._helpers as hlp  # Internal helpers used only for comparison
# noinspection PyProtectedMember
from src.runtime import _resources as resources  # Internal helper to clean cache between test runs
# Module under test
from src.runtime import interfaces as rt


class _Asserts(unittest.TestCase):
    """
    Common assertion helpers for test cases.
    """

    def assert_equal(self, *, actual: Any, expected: Any):
        """
        Assert that two values are equal when compared as strings.
        """
        val_out = str(actual)
        val_exp = str(expected)
        with self.subTest(Actual=val_out, Expected=val_exp):
            self.assertEqual(val_out, val_exp)


class _Fixture:
    """
    Provisions a temporary runtime root with a JSON resource and cleans it up.
    """

    tmp_root: str | None = None
    runtime_dir: str | None = None

    # Realistic sample data: mix of str and list[str]
    TEST_DATA = {
        "Capacitor": ["Electrolytic", "Ceramic", "Film"],
        "Connector": "Connector",
        "Buzzer": ["Buzzer", "Speaker"],
    }

    def set_up(self, resource_name: str):
        """
        Prepare a temporary project root and runtime folder with JSON resource.
        """
        # Reload module to clear memory
        importlib.reload(resources)

        # Fresh temp project root
        self.tmp_root = tempfile.mkdtemp(prefix="runtime_public_api_")

        # Build runtime dir …/src/runtime
        self.runtime_dir = utils.construct_folder_path(self.tmp_root, hlp.RUNTIME_FOLDER)
        os.makedirs(self.runtime_dir, exist_ok=True)

        # File name: "_component_type.json"
        filename = rt.RUNTIME_JSON_PREFIX + resource_name + utils.JSON_FILE_EXT
        filepath = os.path.join(self.runtime_dir, filename)

        # Wrap payload in standard packet with checksum/meta via utils
        packet = utils.create_json_packet(self.TEST_DATA, source_file=filename)

        # Persist packet to disk
        utils.save_json_file(filepath, packet)

    def tear_down(self):
        """
        Remove the temporary project root and all generated files.
        """
        shutil.rmtree(self.tmp_root, ignore_errors=True)


class TestConstants(_Asserts):
    """
    Unit test for public constants exposed by the runtime interface.
    """

    def test_constants(self):
        """
        Should expose public constants that match the internal contract.
        """
        # ARRANGE
        # Expected values are taken from internal helpers to avoid hard-coding.
        exp_prefix = hlp.RUNTIME_JSON_PREFIX
        exp_folder = hlp.RUNTIME_FOLDER
        exp_component_src = resources.COMPONENT_TYPE_SOURCE

        # ACT
        got_prefix = rt.RUNTIME_JSON_PREFIX
        got_folder = rt.RUNTIME_FOLDER
        got_component_src = rt.COMPONENT_TYPE_SOURCE

        # ASSERT
        self.assert_equal(actual=got_prefix, expected=exp_prefix)
        self.assert_equal(actual=got_folder, expected=exp_folder)
        self.assert_equal(actual=got_component_src, expected=exp_component_src)


class TestComponentTypeResourceInterfaces(_Asserts, _Fixture):
    """
    Unit tests for the component-type interfaces via the public API.
    """
    resource_name: str = resources.COMPONENT_TYPE_SOURCE

    def setUp(self):
        # Provision a real on-disk JSON resource
        self.set_up(self.resource_name)

    def tearDown(self):
        self.tear_down()

    def test_component_type_roundtrip(self):
        """
        Should load the resource and return correct keys and normalized tuple[str] values.
        """
        # ARRANGE
        # Keys should match the payload's top-level keys.
        expected_keys = tuple(self.TEST_DATA.keys())

        # For a representative field, validate normalization to tuple[str, ...]
        requested_key = expected_keys[0]
        expected_values = tuple(self.TEST_DATA[requested_key])  # list[str] -> tuple[str, ...]

        with patch.object(utils, "find_root_folder") as p_root:
            p_root.return_value = self.tmp_root

            # ACT
            # Load everything via the public surface
            rt.load_all_resources()

            # Fetch keys
            out_keys = rt.get_component_type_keys()

            # Fetch values
            out_vals = rt.get_component_type_values(requested_key)

        # ASSERT (keys)
        self.assert_equal(actual=out_keys, expected=expected_keys)

        # ASSERT (values)
        self.assert_equal(actual=out_vals, expected=expected_values)

    def test_component_type_raises(self):
        """
        Should raise RuntimeError when requesting values for a missing key.
        """
        # ARRANGE
        missing_key = "NotARealKey"
        expected_error = RuntimeError.__name__

        with patch.object(utils, "find_root_folder") as p_root:
            p_root.return_value = self.tmp_root

            # Load once so that getters exercise the cache path end-to-end
            rt.load_all_resources()

            # ACT
            try:
                _ = rt.get_component_type_values(missing_key)
                actual_error = ""
            except Exception as e:
                actual_error = type(e).__name__

        # ASSERT
        self.assert_equal(actual=actual_error, expected=expected_error)


if __name__ == "__main__":
    unittest.main()
