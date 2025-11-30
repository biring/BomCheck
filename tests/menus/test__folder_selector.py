"""
Unit tests for the interactive folder selector menu workflow.

This module verifies that folder_selector:
    - Uses a valid start_path when provided
    - Raises ValueError for invalid starting folders
    - Returns the current folder when the user selects "Select current folder"
    - Updates to the parent folder when "Go up one level" is chosen
    - Ignores out-of-range menu indices and keeps the loop stable

Example Usage:
    # Preferred usage via project-root invocation:
    python -m unittest tests.menus.test__folder_selector

    # Direct discovery (runs all tests, including this module):
    python -m unittest discover -s tests

Dependencies:
    - Python >= 3.10
    - Standard Library: unittest, unittest.mock
    - External Packages: None

Notes:
    - Tests patch src.menus._folder_selector.folder_path and cli to isolate I/O and filesystem behavior.
    - Subtests wrap assertions to provide clearer diagnostics on expected vs actual folder paths.

License:
    - Internal Use Only
"""

import unittest
from unittest.mock import patch

# noinspection PyProtectedMember
from src.menus import _folder_selector as folder_selector

MODULE_PATH = folder_selector.__name__  # Used to build patch paths dynamically


class TestFolderSelector(unittest.TestCase):
    """
    Unit tests for the interactive `folder_selector` function.
    """

    def test_valid_start_path_uses_provided_folder(self):
        """
        Should use the provided start_path as the initial folder when it is a valid directory.
        """
        # ARRANGE
        start_path = "/custom/start"

        # Patch folder_path and cli to control environment and user interaction
        with patch(f"{MODULE_PATH}.folder_path") as mock_folder_path, \
                patch(f"{MODULE_PATH}.cli") as mock_cli:
            # Simulate a valid start_path
            mock_folder_path.resolve_project_folder.return_value = "/project/root"
            mock_folder_path.is_folder_path.return_value = True

            # Ensure folder traversal helpers are safe to call
            mock_folder_path.go_up_one_folder.return_value = "/project"
            mock_folder_path.list_immediate_sub_folders.return_value = []

            # Make normalize_folder_path act like a simple identity helper
            mock_folder_path.normalize_folder_path.side_effect = lambda p: p

            # User immediately selects "Select current folder"
            mock_cli.prompt_menu_selection.return_value = 1

            # ACT
            result = folder_selector.folder_selector(start_path)

        # ASSERT
        expected = start_path
        with self.subTest(Out=result, Exp=expected):
            self.assertEqual(result, expected)

    def test_invalid_start_path_raises_value_error(self):
        """
        Should raise ValueError when start_path does not represent a valid folder path.
        """
        # ARRANGE
        invalid_path = "/invalid/start"
        expected = ValueError.__name__

        with patch(f"{MODULE_PATH}.folder_path") as mock_folder_path, \
                patch(f"{MODULE_PATH}.cli"):
            # Force invalid folder detection
            mock_folder_path.is_folder_path.return_value = False

            # ACT
            # Capture the raised exception type name instead of letting it fail the test directly
            try:
                folder_selector.folder_selector(invalid_path)
                result = ""  # No exception raised
            except ValueError as exc:
                result = type(exc).__name__

        # ASSERT
        with self.subTest(Out=result, Exp=expected):
            self.assertEqual(result, expected)

    def test_select_current_folder_returns_current_path(self):
        """
        Should return the current folder path when the user selects the 'Select current folder' menu option.
        """
        # ARRANGE
        project_root = "/project/root"

        with patch(f"{MODULE_PATH}.folder_path") as mock_folder_path, \
                patch(f"{MODULE_PATH}.cli") as mock_cli:
            # Default project folder when no start_path is provided
            mock_folder_path.resolve_project_folder.return_value = project_root

            # Safe defaults for traversal helpers
            mock_folder_path.go_up_one_folder.return_value = "/project"
            mock_folder_path.list_immediate_sub_folders.return_value = []

            # Make normalize_folder_path act like a simple identity helper
            mock_folder_path.normalize_folder_path.side_effect = lambda p: p

            # User immediately chooses "Select current folder"
            mock_cli.prompt_menu_selection.return_value = 1

            # ACT
            result = folder_selector.folder_selector()

        # ASSERT
        expected = project_root
        with self.subTest(Out=result, Exp=expected):
            self.assertEqual(result, expected)

    def test_go_up_one_level_updates_current_path(self):
        """
        Should update the current folder path to its parent when the user selects the 'Go up one level' menu option.
        """
        # ARRANGE
        child_folder = "/project/root/child"
        parent_folder = "/project/root"

        with patch(f"{MODULE_PATH}.folder_path") as mock_folder_path, \
                patch(f"{MODULE_PATH}.cli") as mock_cli:
            # Start inside a child directory
            mock_folder_path.resolve_project_folder.return_value = child_folder

            # First call moves from child to parent; second call from parent to higher-level folder
            mock_folder_path.go_up_one_folder.side_effect = [parent_folder, "/project"]
            mock_folder_path.list_immediate_sub_folders.return_value = []

            # Make normalize_folder_path act like a simple identity helper
            mock_folder_path.normalize_folder_path.side_effect = lambda p: p

            # First selection: "Go up one level" (0)
            # Second selection: "Select current folder" (1)
            mock_cli.prompt_menu_selection.side_effect = [0, 1]

            # ACT
            result = folder_selector.folder_selector()

        # ASSERT
        expected = parent_folder
        with self.subTest(Out=result, Exp=expected):
            self.assertEqual(result, expected)

    def test_out_of_range_menu_index_is_ignored(self):
        """
        Should ignore out-of-range menu indices and continue the selection loop without crashing.
        """
        # ARRANGE
        project_root = "/project/root"

        with patch(f"{MODULE_PATH}.folder_path") as mock_folder_path, \
                patch(f"{MODULE_PATH}.cli") as mock_cli:
            # Start at a known project root
            mock_folder_path.resolve_project_folder.return_value = project_root

            # Parent folder is stable for both loop iterations
            mock_folder_path.go_up_one_folder.side_effect = ["/project", "/project"]
            mock_folder_path.list_immediate_sub_folders.return_value = []

            # Make normalize_folder_path act like a simple identity helper
            mock_folder_path.normalize_folder_path.side_effect = lambda p: p

            # First selection: out-of-range index (e.g., 99)
            # Second selection: "Select current folder" (1) to exit cleanly
            mock_cli.prompt_menu_selection.side_effect = [99, 1]

            # ACT
            # If out-of-range handling is incorrect, this call might raise or misbehave
            result = folder_selector.folder_selector()

        # ASSERT
        expected = project_root
        with self.subTest(Out=result, Exp=expected):
            self.assertEqual(result, expected)

    def test_custom_menu_title_is_passed_to_cli(self):
        """
        Should pass the caller-supplied menu_title to cli.prompt_menu_selection().
        """
        custom_title = "Select Input File Folder"

        with patch(f"{MODULE_PATH}.folder_path") as mock_folder_path, \
                patch(f"{MODULE_PATH}.cli") as mock_cli:
            # Setup basic folder_path behavior
            mock_folder_path.resolve_project_folder.return_value = "/project/root"
            mock_folder_path.go_up_one_folder.return_value = "/project"
            mock_folder_path.list_immediate_sub_folders.return_value = []
            mock_folder_path.normalize_folder_path.side_effect = lambda p: p

            # User selects "Select current folder"
            mock_cli.prompt_menu_selection.return_value = 1

            # ACT
            folder_selector.folder_selector(
                menu_title=custom_title,
            )

        # ASSERT
        # Expect cli.prompt_menu_selection called with custom title
        call_args = mock_cli.prompt_menu_selection.call_args[0]
        actual_title = call_args[1]  # (options, title, prompt)

        with self.subTest(Out=actual_title, Exp=custom_title):
            self.assertEqual(actual_title, custom_title)

    def test_custom_menu_prompt_is_passed_to_cli(self):
        """
        Should pass the caller-supplied menu_prompt to cli.prompt_menu_selection().
        """
        custom_prompt = "Enter a number for input folder: "

        with patch(f"{MODULE_PATH}.folder_path") as mock_folder_path, \
                patch(f"{MODULE_PATH}.cli") as mock_cli:
            # Setup basic folder_path behavior
            mock_folder_path.resolve_project_folder.return_value = "/project/root"
            mock_folder_path.go_up_one_folder.return_value = "/project"
            mock_folder_path.list_immediate_sub_folders.return_value = []
            mock_folder_path.normalize_folder_path.side_effect = lambda p: p

            # User selects "Select current folder"
            mock_cli.prompt_menu_selection.return_value = 1

            # ACT
            folder_selector.folder_selector(
                menu_prompt=custom_prompt,
            )

        # ASSERT
        # Expect cli.prompt_menu_selection called with custom prompt
        call_args = mock_cli.prompt_menu_selection.call_args[0]
        actual_prompt = call_args[2]  # (options, title, prompt)

        with self.subTest(Out=actual_prompt, Exp=custom_prompt):
            self.assertEqual(actual_prompt, custom_prompt)

    def test_defaults_are_used_when_no_title_or_prompt_provided(self):
        """
        Should use the module's default title and prompt when the caller does not
        provide menu_title or menu_prompt.
        """
        # Import defaults directly from the module under test
        default_title = folder_selector._DEFAULT_MENU_TITLE
        default_prompt = folder_selector._DEFAULT_MENU_PROMPT

        with patch(f"{MODULE_PATH}.folder_path") as mock_folder_path, \
                patch(f"{MODULE_PATH}.cli") as mock_cli:
            # Setup basic folder_path behavior
            mock_folder_path.resolve_project_folder.return_value = "/project/root"
            mock_folder_path.go_up_one_folder.return_value = "/project"
            mock_folder_path.list_immediate_sub_folders.return_value = []
            mock_folder_path.normalize_folder_path.side_effect = lambda p: p

            # User selects "Select current folder"
            mock_cli.prompt_menu_selection.return_value = 1

            # ACT
            folder_selector.folder_selector()

        # ASSERT
        # Validate the default title and default prompt were passed through
        call_args = mock_cli.prompt_menu_selection.call_args[0]
        actual_title = call_args[1]  # (options, title, prompt)
        actual_prompt = call_args[2]

        with self.subTest(Field="title", Out=actual_title, Exp=default_title):
            self.assertEqual(actual_title, default_title)

        with self.subTest(Field="prompt", Out=actual_prompt, Exp=default_prompt):
            self.assertEqual(actual_prompt, default_prompt)


if __name__ == '__main__':
    unittest.main()
