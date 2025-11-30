"""
Unit tests for the public API of the `src.common` package.

Example Usage:
    # Preferred usage via project-root invocation:
    python -m unittest tests/common/test_api.py

    # Direct discovery of all tests:
    python -m unittest discover -s tests

Dependencies:
    - Python >= 3.10
    - Standard Library: unittest, typing

Notes:
    - Tests validate only the public API exported by `src.common`.
    - Internal implementation details (modules prefixed with "_") are intentionally not imported.
    - Provides baseline confidence that the package interface resolves and operates correctly.

License:
    - Internal Use Only
"""
import os
import shutil
import tempfile
import unittest
from typing import Any
from unittest.mock import patch

from src import utils
from src.common import ChangeLog, JsonCache

import src.utils.folder_path as folder
import src.utils.json_io as json_io


class TestChangeLog(unittest.TestCase):
    """
    Unit test for the public ChangeLog API exposed via `src.common`.
    """

    def test_basic_usage(self) -> None:
        """
        Should record only non-empty entries and render rows using the active (module, file, sheet, section) context.
        """

        # ARRANGE
        log = ChangeLog()

        # Set context through public API
        log.set_module_name("parser")
        log.set_file_name("test.xlsx")
        log.set_sheet_name("Sheet1")
        log.set_section_name("Row:4")

        # ACT
        log.add_entry("Invalid Quantity")
        log.add_entry("")  # ignored by implementation
        log.add_entry("Missing Part Number")

        result = log.render()

        # ASSERT
        expected = [
            "parser | test.xlsx | Sheet1 | Row:4 | Invalid Quantity",
            "parser | test.xlsx | Sheet1 | Row:4 | Missing Part Number",
        ]

        with self.subTest(Out=len(result), Exp=len(expected)):
            self.assertEqual(len(result), len(expected))

        # Field-by-field comparison for each row
        for idx, (out_row, exp_row) in enumerate(zip(result, expected)):
            with self.subTest(Row=idx, Out=out_row, Exp=exp_row):
                self.assertEqual(out_row, exp_row)


class TestJsonCacheInterface(unittest.TestCase):
    """
    Interface-level unit tests for JsonCache via `src.common`.

    These tests focus on:
        - get_data_map_copy: returns a copy of the JSON payload.
        - get_keys: returns all keys as a sorted tuple.
        - get_value: returns typed values for existing keys.

    Error paths (missing keys, type mismatches, etc.) are validated in the internal unit tests and are not re-tested here.
    """

    TEST_RESOURCE_PREFIX: str = "_"
    TEST_RESOURCE_FOLDER_PARTS: tuple[str, ...] = ("a", "b")

    TEST_JSON_PAYLOAD: dict[str, Any] = {
        "app_name": "BomCheck",
        "log_level": "DEBUG",
        "retry_count": -3,
        "error_types": ["Info", "Warning", "Error"],
    }

    def setUp(self) -> None:
        """
        Prepare a temporary project root and runtime folder, and write a JSON
        resource packet for use by JsonCache interface tests.
        """
        # ARRANGE: create isolated project root; removed in tearDown()
        self.tmp_project_root = tempfile.mkdtemp(prefix="runtime_api_tmp_")

        # Mirror the on-disk runtime layout used by production code
        self.runtime_dir = folder.construct_folder_path(
            self.tmp_project_root,
            self.TEST_RESOURCE_FOLDER_PARTS,
        )
        os.makedirs(self.runtime_dir, exist_ok=True)

        # Build resource filename and path
        self.resource_name = "settings"
        resource_filename = (
                self.TEST_RESOURCE_PREFIX + self.resource_name + utils.JSON_FILE_EXT
        )
        resource_path = os.path.join(self.runtime_dir, resource_filename)

        # Wrap payload in the standard packet envelope expected by the loader
        packet = json_io.create_json_packet(
            self.TEST_JSON_PAYLOAD,
            source_file=resource_filename,
        )

        # Persist packet where JsonCache will look for it
        json_io.save_json_file(resource_path, packet)

        # Patch `find_root_folder` so runtime resolution points at our temp root
        self._root_patcher = patch.object(
            folder,
            "resolve_project_folder",
            return_value=self.tmp_project_root,
        )
        self._root_patcher.start()

        # Pre-compute required keys used in these tests
        self.required_keys: tuple[str, ...] = tuple(self.TEST_JSON_PAYLOAD.keys())

    def tearDown(self) -> None:
        """
        Restore patched functions and remove the temporary project root.
        """
        # Stop patching find_root_folder
        self._root_patcher.stop()

        # Best-effort cleanup of temporary directories
        shutil.rmtree(self.tmp_project_root, ignore_errors=True)

    def test_get_data_map_method(self) -> None:
        """
        Should return a dictionary containing the validated JSON payload.
        """
        # ARRANGE
        cache = JsonCache(
            resource_name=self.resource_name,
            resource_folder_parts=self.TEST_RESOURCE_FOLDER_PARTS,
            required_keys=self.required_keys,
            resource_prefix=self.TEST_RESOURCE_PREFIX,
        )

        # ACT
        data_copy = cache.get_data_map_copy()

        # ASSERT
        with self.subTest(Scenario="data_map", Out=data_copy, Exp=self.TEST_JSON_PAYLOAD):
            self.assertEqual(data_copy, self.TEST_JSON_PAYLOAD)

    def test_get_keys_method(self) -> None:
        """
        Should return all JSON keys as a sorted tuple.
        """
        # ARRANGE
        cache = JsonCache(
            resource_name=self.resource_name,
            resource_folder_parts=self.TEST_RESOURCE_FOLDER_PARTS,
            required_keys=self.required_keys,
            resource_prefix=self.TEST_RESOURCE_PREFIX,
        )
        expected_keys = tuple(sorted(self.TEST_JSON_PAYLOAD.keys()))

        # ACT
        actual_keys = cache.get_keys()

        # ASSERT
        with self.subTest(Out=actual_keys, Exp=expected_keys):
            self.assertEqual(actual_keys, expected_keys)

    def test_get_value_method(self) -> None:
        """
        Should return the stored value when the key exists and the requested
        type matches the stored value type.
        """
        # ARRANGE
        cache = JsonCache(
            resource_name=self.resource_name,
            resource_folder_parts=self.TEST_RESOURCE_FOLDER_PARTS,
            required_keys=self.required_keys,
            resource_prefix=self.TEST_RESOURCE_PREFIX,
        )

        cases = (
            (str, "app_name", self.TEST_JSON_PAYLOAD["app_name"]),  # String
            (int, "retry_count", self.TEST_JSON_PAYLOAD["retry_count"]),  # Integer
            (list, "error_types", self.TEST_JSON_PAYLOAD["error_types"]),  # List
        )

        # ACT + ASSERT
        for data_type, key, expected_value in cases:
            actual_value = cache.get_value(key, data_type)

            with self.subTest(Key=key, Out=actual_value, Exp=expected_value):
                self.assertEqual(actual_value, expected_value)


if __name__ == "__main__":
    unittest.main()
