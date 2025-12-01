"""
Unit tests for the interactive file selector workflow.

Example Usage:
    # Preferred usage via project-root invocation:
    python -m unittest tests.menus.test__file_selector

    # Direct discovery (runs all tests, including this module):
    python -m unittest discover -s tests

Dependencies:
    - Python >= 3.10
    - Standard Library: unittest, unittest.mock
    - External Packages: None

License:
    - Internal Use Only
"""

import unittest
from unittest.mock import patch

# noinspection PyProtectedMember
from src.menus import _file_selector as file_selector

MODULE_PATH = file_selector.__name__  # Used to build patch paths dynamically


class TestFileSelector(unittest.TestCase):
    """
    Unit tests for the interactive `file_selector` function.
    """

    def test_happy_path(self):
        """
        Should return a normalized full file path for the user-selected file.
        """
        # ARRANGE
        folder = "/data/input"

        # Files returned by the helper (unsorted on purpose to exercise sorting)
        helper_files = ["b.csv", "a.csv"]
        expected_file = "b.csv"
        expected_full_path = f"{folder}/{expected_file}"

        with patch(f"{MODULE_PATH}.folder_path") as mock_folder_path, \
                patch(f"{MODULE_PATH}.file_path") as mock_file_path, \
                patch(f"{MODULE_PATH}.cli") as mock_cli:
            # Folder is valid and normalized as-is
            mock_folder_path.is_folder_path.return_value = True
            mock_folder_path.normalize_folder_path.side_effect = lambda p: p

            # Helper returns an unsorted set of file names
            mock_file_path.get_files_in_folder.return_value = tuple(helper_files)

            # Build and normalize the full path in a predictable way
            mock_file_path.construct_file_path.side_effect = (
                lambda base, name: f"{base}/{name}"
            )
            mock_file_path.normalize_file_path.side_effect = lambda p: p

            # User selects index 1 → second entry in the *sorted* list = "b.csv"
            mock_cli.prompt_menu_selection.return_value = 1

            # ACT
            result = file_selector.file_selector(folder_path_in=folder)

        # ASSERT
        with self.subTest(Out=result, Exp=expected_full_path):
            self.assertEqual(result, expected_full_path)

    def test_menu_index_out_of_range(self):
        """
        Should ignore out-of-range menu indices and continue the selection loop.
        """
        # ARRANGE
        folder = "/data/input"
        helper_files = ["b.csv", "a.csv"]
        # Sorted list will be ["a.csv", "b.csv"]; we will eventually select index 0.
        expected_full_path = f"{folder}/a.csv"

        with patch(f"{MODULE_PATH}.folder_path") as mock_folder_path, \
                patch(f"{MODULE_PATH}.file_path") as mock_file_path, \
                patch(f"{MODULE_PATH}.cli") as mock_cli:
            mock_folder_path.is_folder_path.return_value = True
            mock_folder_path.normalize_folder_path.side_effect = lambda p: p

            mock_file_path.get_files_in_folder.return_value = tuple(helper_files)
            mock_file_path.construct_file_path.side_effect = (
                lambda base, name: f"{base}/{name}"
            )
            mock_file_path.normalize_file_path.side_effect = lambda p: p

            # First selection: out-of-range index (e.g., 99)
            # Second selection: valid index 0
            mock_cli.prompt_menu_selection.side_effect = [99, 0]

            # ACT
            result = file_selector.file_selector(folder_path_in=folder)

        # ASSERT
        with self.subTest(Out=result, Exp=expected_full_path):
            self.assertEqual(result, expected_full_path)

    def test_msg_custom(self):
        """
        Should pass caller-supplied menu_title and menu_prompt to cli.prompt_menu_selection().
        """
        # ARRANGE
        folder = "/data/input"
        custom_title = "Select Input File"
        custom_prompt = "Enter number for input file: "

        helper_files = ["b.csv", "a.csv"]

        with patch(f"{MODULE_PATH}.folder_path") as mock_folder_path, \
                patch(f"{MODULE_PATH}.file_path") as mock_file_path, \
                patch(f"{MODULE_PATH}.cli") as mock_cli:
            mock_folder_path.is_folder_path.return_value = True
            mock_folder_path.normalize_folder_path.side_effect = lambda p: p

            mock_file_path.get_files_in_folder.return_value = tuple(helper_files)
            mock_file_path.construct_file_path.side_effect = (
                lambda base, name: f"{base}/{name}"
            )
            mock_file_path.normalize_file_path.side_effect = lambda p: p

            # User selects the first file to exit the loop
            mock_cli.prompt_menu_selection.return_value = 0

            # ACT
            file_selector.file_selector(
                folder_path_in=folder,
                menu_title=custom_title,
                menu_prompt=custom_prompt,
            )

        # ASSERT
        call_args = mock_cli.prompt_menu_selection.call_args[0]
        options, actual_title, actual_prompt = call_args

        # Options should be the sorted file list
        expected_options = sorted(helper_files)

        with self.subTest(Field="options", Out=options, Exp=expected_options):
            self.assertEqual(options, expected_options)

        with self.subTest(Field="title", Out=actual_title, Exp=custom_title):
            self.assertEqual(actual_title, custom_title)

        with self.subTest(Field="prompt", Out=actual_prompt, Exp=custom_prompt):
            self.assertEqual(actual_prompt, custom_prompt)

    def test_msg_default(self):
        """
        Should use module defaults for title and prompt when caller omits them.
        """
        # ARRANGE
        folder = "/data/input"
        helper_files = ["b.csv", "a.csv"]

        # Import defaults from the module under test
        default_title = file_selector._DEFAULT_MENU_TITLE
        default_prompt = file_selector._DEFAULT_MENU_PROMPT

        with patch(f"{MODULE_PATH}.folder_path") as mock_folder_path, \
                patch(f"{MODULE_PATH}.file_path") as mock_file_path, \
                patch(f"{MODULE_PATH}.cli") as mock_cli:
            mock_folder_path.is_folder_path.return_value = True
            mock_folder_path.normalize_folder_path.side_effect = lambda p: p

            mock_file_path.get_files_in_folder.return_value = tuple(helper_files)
            mock_file_path.construct_file_path.side_effect = (
                lambda base, name: f"{base}/{name}"
            )
            mock_file_path.normalize_file_path.side_effect = lambda p: p

            # User selects first file
            mock_cli.prompt_menu_selection.return_value = 0

            # ACT
            file_selector.file_selector(folder_path_in=folder)

        # ASSERT
        call_args = mock_cli.prompt_menu_selection.call_args[0]
        _, actual_title, actual_prompt = call_args

        with self.subTest(Field="title", Out=actual_title, Exp=default_title):
            self.assertEqual(actual_title, default_title)

        with self.subTest(Field="prompt", Out=actual_prompt, Exp=default_prompt):
            self.assertEqual(actual_prompt, default_prompt)

    def test_raise_by_helper(self):
        """
        Should wrap error from get_files_in_folder.
        """
        # ARRANGE
        folder = "/data/input"
        expected = ValueError.__name__

        with patch(f"{MODULE_PATH}.folder_path") as mock_folder_path, \
                patch(f"{MODULE_PATH}.file_path") as mock_file_path, \
                patch(f"{MODULE_PATH}.cli"):
            # Consider the folder valid at the folder-path layer
            mock_folder_path.is_folder_path.return_value = True
            mock_folder_path.normalize_folder_path.side_effect = lambda p: p

            # Simulate a low-level filesystem error from the file-path helper
            mock_file_path.get_files_in_folder.side_effect = FileNotFoundError("missing")

            # ACT
            try:
                file_selector.file_selector(folder_path_in=folder)
                result = ""  # No exception raised
            except ValueError as exc:
                result = type(exc).__name__

        # ASSERT
        with self.subTest(Out=result, Exp=expected):
            self.assertEqual(result, expected)

    def test_raise_for_folder_path_value(self):
        """
        Should raise error when folder path does not represent a valid directory.
        """
        # ARRANGE
        folder = "/invalid/path"
        expected = ValueError.__name__

        # Patch folder + file helpers and CLI to isolate behavior
        with patch(f"{MODULE_PATH}.folder_path") as mock_folder_path, \
                patch(f"{MODULE_PATH}.file_path"), \
                patch(f"{MODULE_PATH}.cli"):
            # Force invalid folder detection
            mock_folder_path.is_folder_path.return_value = False

            # ACT
            try:
                file_selector.file_selector(folder_path_in=folder)
                result = ""  # No exception raised
            except ValueError as exc:
                result = type(exc).__name__

        # ASSERT
        with self.subTest(Out=result, Exp=expected):
            self.assertEqual(result, expected)

    def test_raise_no_files_available(self):
        """
        Should raise error when no files are available in the folder for the given filter.
        """
        # ARRANGE
        folder = "/data/empty"
        expected = ValueError.__name__

        with patch(f"{MODULE_PATH}.folder_path") as mock_folder_path, \
                patch(f"{MODULE_PATH}.file_path") as mock_file_path, \
                patch(f"{MODULE_PATH}.cli"):
            # Folder is valid but contains no files
            mock_folder_path.is_folder_path.return_value = True
            mock_folder_path.normalize_folder_path.side_effect = lambda p: p
            mock_file_path.get_files_in_folder.return_value = ()

            # ACT
            try:
                file_selector.file_selector(folder_path_in=folder, extensions=(".csv",))
                result = ""  # No exception raised
            except ValueError as exc:
                result = type(exc).__name__

        # ASSERT
        with self.subTest(Out=result, Exp=expected):
            self.assertEqual(result, expected)


if __name__ == "__main__":
    unittest.main()
