"""
Integration-style unit tests for the component-type lookup loader.

This module validates the happy-path behavior and error handling of the component-type lookup API, ensuring JSON-backed lookup tables are loaded correctly from the runtime resource layout and exposed as plain dictionaries.

Example Usage:
    # Preferred usage via project-root invocation:
    python -m unittest tests/lookups/test__component_type.py

    # Direct discovery (runs all tests, including this module):
    python -m unittest discover -s tests

Dependencies:
    - Python >= 3.10
    - Standard Library: unittest, tempfile, shutil, importlib, unittest.mock
    - External Packages: None

Notes:
    - Tests are integration-oriented and exercise the real filesystem layout using a temporary project root.
    - Only the project-root resolution is patched to keep behavior close to production.
    - The lookup loader is treated as a pure read-only interface returning a dict on success.
    - Construction-time failures from the underlying cache are expected to be wrapped as RuntimeError.

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
from src.lookups import _component_type as ct  # Module under test


class TestGetComponentTypeLookupTable(unittest.TestCase):
    """
    Unit tests for the get_component_type_lookup_table lookup interface.
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
        importlib.reload(ct)

        # Create an isolated project root; removed in tearDown()
        self.tmp_project_root = tempfile.mkdtemp(prefix="runtime_tmp_")

        # Mirror the on-disk runtime layout used by production code
        runtime_dir = folder_path.construct_folder_path(
            self.tmp_project_root,
            ct.COMPONENT_TYPE_FOLDER_PARTS,
        )
        folder_path.create_folder_if_missing(runtime_dir)

        # Build resource file paths and names
        resource_filename = ct.COMPONENT_TYPE_RESOURCE_NAME + util.json_io.JSON_FILE_EXT
        resource_path = util.file_path.construct_file_path(runtime_dir, resource_filename)

        # Wrap the payload in the standard packet envelope expected by the loader
        resource_packet = json_io.create_json_packet(
            self.TEST_JSON_DATA,
            source_file=resource_filename,
        )

        # Persist the packet where CacheReadOnly will look for it
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
        Should return a dictionary of component-type mappings when the runtime resource is valid.
        """
        # ARRANGE
        expected_map = self.TEST_JSON_DATA

        # Force CacheReadOnly to resolve its root under the temporary project root
        with patch.object(folder_path, "resolve_project_folder") as p_root:
            p_root.return_value = self.tmp_project_root

            # ACT
            actual_map = ct.get_component_type_lookup_table()

        # ASSERT
        with self.subTest(Out=actual_map, Exp=expected_map):
            self.assertDictEqual(actual_map, expected_map)

    def test_raise(self):
        """
        Should raise RuntimeError when the underlying lookup cache construction fails.
        """
        # ARRANGE
        expected_error = RuntimeError.__name__

        # Replace CacheReadOnly with a stub that always raises an error
        with patch.object(ct, "CacheReadOnly") as mock_cache_ctor:
            mock_cache_ctor.side_effect = ValueError("boom")

            # ACT
            try:
                _ = ct.get_component_type_lookup_table()
                actual_error = ""
            except Exception as exc:  # noqa: BLE001
                actual_error = type(exc).__name__

        # ASSERT
        with self.subTest(Out=actual_error, Exp=expected_error):
            self.assertEqual(actual_error, expected_error)


if __name__ == '__main__':
    unittest.main()
