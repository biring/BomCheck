"""
Happy-path integration tests for the CLI and menu interfaces façade.

This module verifies that:
    - The file selector returns the expected CSV file when exactly one matching file exists in the target folder.
    - The folder selector returns the starting folder when the user chooses the "select current folder" option.
    - Only the CLI prompt function is patched; filesystem behavior relies on real temporary folders and files.

Example Usage:
    # Preferred usage via project-root invocation:
    python -m unittest tests/menus/test_interfaces.py

    # Direct discovery (runs all tests, including this module):
    python -m unittest discover -s tests

Dependencies:
    - Python >= 3.10
    - Standard Library: os, tempfile, unittest, pathlib, unittest.mock
    - External Packages: None

Notes:
    - Tests treat the CLI menu selection as an external dependency and patch only `cli.prompt_menu_selection` on the happy path.
    - Temporary directories and a single CSV file are created per test case to keep the filesystem isolated and self-cleaning.
    - These tests are intentionally limited to positive flows and do not exercise error-handling or invalid user input paths.

License:
    - Internal Use Only
"""

import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from src.cli import interfaces as cli
from src.menus import interfaces as menu


class TestInterfaces(unittest.TestCase):
    """
    Happy-path integration tests for the `interfaces` façade.
    """

    def setUp(self):
        """
        Create a temporary folder and a single CSV file for the tests.
        """
        # ARRANGE (shared setup)
        self._tmp_dir = tempfile.TemporaryDirectory()
        self.base_path = Path(self._tmp_dir.name)

        # Create a single CSV file in the temporary folder for the file selector
        self.selected_file = self.base_path / "example_data.csv"
        self.selected_file.write_text("dummy content", encoding="utf-8")

    def tearDown(self):
        """
        Clean up the temporary folder and files created for the tests.
        """
        # ARRANGE/TEARDOWN
        self._tmp_dir.cleanup()

    def test_file_selector(self):
        """
        Should return the full path to the single CSV file in the folder when invoked via the `interfaces` façade, using only a patched CLI response.
        """
        # ARRANGE
        folder = str(self.base_path)
        expected = os.path.normpath(str(self.selected_file))

        # Patch ONLY the CLI menu selection for the file selector.
        # With exactly one file, the valid index is 0.
        with patch.object(cli, "prompt_menu_selection") as mock_prompt:
            mock_prompt.return_value = 0
            # ACT
            result = menu.file_selector(
                folder_path_in=folder,
                extensions=(".csv",),
            )

        # Normalize paths to make the assertion robust across platforms
        normalized_result = os.path.normpath(result)

        # ASSERT
        # Verify that the selector returns the expected file path
        with self.subTest(Out=normalized_result, Exp=expected):
            self.assertEqual(normalized_result, expected)

        # Verify the CLI prompt was called exactly once on the happy path
        call_count = mock_prompt.call_count
        with self.subTest(Out=call_count, Exp=1):
            self.assertEqual(call_count, 1)

    def test_folder_selector(self):
        """
        Should return the full folder path when invoked via the façade and the user selects the 'Select current folder' option, with only CLI patched.
        """
        # ARRANGE
        start_path = str(self.base_path)
        expected = os.path.normpath(start_path)

        # Patch ONLY the CLI menu selection for the file selector.
        # With exactly one file, the valid index is 1. As 0 is always used for going up one level.
        with patch.object(cli, "prompt_menu_selection") as mock_prompt:
            mock_prompt.return_value = 1
            # ACT
            result = menu.folder_selector(start_path=start_path)

        normalized_result = os.path.normpath(result)

        # ASSERT
        # Verify that the selector returns the starting folder as the chosen folder
        with self.subTest(Out=normalized_result, Exp=expected):
            self.assertEqual(normalized_result, expected)

        # Verify the CLI prompt was called exactly once on the happy path
        call_count = mock_prompt.call_count
        with self.subTest(Out=call_count, Exp=1):
            self.assertEqual(call_count, 1)


if __name__ == "__main__":
    unittest.main()
