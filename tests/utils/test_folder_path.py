"""
Unit tests for the folder path utility functions.

This module verifies the correctness and robustness of the functions in `src.utils.folder_path`, which provide a platform-independent interface for path normalization, folder creation, sub folder listing, and execution context resolution.

Example Usage:
    # Preferred usage from project root:
    python -m unittest tests/utils/test_folder_path.py

    # Run all tests via discovery:
    python -m unittest discover -s tests

Dependencies:
    - Python >= 3.9
    - Standard Library: os, sys, shutil, tempfile, unittest
    - External Packages: None

Notes:
    - Tests validate both functional output and side effects (e.g., folder creation).
    - Platform-specific checks (Windows drive handling) use conditional skips.
    - Temporary directories ensure isolation and avoid filesystem pollution.
    - Internal-only behavior is tested via direct module imports.

License:
    - Internal Use Only
"""

import unittest
import os
import sys
import shutil
import tempfile

# noinspection PyProtectedMember
from src.utils.folder_path import *


class TestConstructFolderPath(unittest.TestCase):
    """
    Unit test for the `construct_folder_path` function in the `folder_path` module.

    This test ensures that a base path and a sequence of sub folders are properly joined and normalized into a consistent, platform-independent folder path.
    """

    def test_windows_style_drive_path(self):
        """
        Should normalize a Windows-style drive path with subfolders and redundant slashes.
        """
        # ARRANGE
        base_path = "C:/home"
        subfolders = ("test", "folder")

        # Expected output after join and normalization
        expected = normalize_folder_path(os.path.join("C:/home", "test", "folder"))

        # ACT
        result = construct_folder_path(base_path, subfolders)

        # ASSERT
        with self.subTest(Out=result, Exp=expected):
            self.assertEqual(result, expected)

    def test_constructs_correct_normalized_path(self):
        """
        Should join base path with subfolders and return a normalized folder path.
        """
        # ARRANGE
        # Input data setup
        base_path = "/home/user"
        subfolders = ("projects", "data")

        # Expected output
        expected = normalize_folder_path(os.path.join(base_path, *subfolders))

        # ACT
        # Call the function under test
        result = construct_folder_path(base_path, subfolders)

        # ASSERT
        # Validate results
        with self.subTest(Out=result, Exp=expected):
            self.assertEqual(result, expected)

    def test_with_empty_subfolders(self):
        """
        Should return normalized base path when no subfolders are provided.
        """
        # ARRANGE
        base_path = "/var/log"
        subfolders = ()

        expected = normalize_folder_path(base_path)

        # ACT
        result = construct_folder_path(base_path, subfolders)

        # ASSERT
        with self.subTest(Out=result, Exp=expected):
            self.assertEqual(result, expected)


class TestCreateFolderIfMissing(unittest.TestCase):
    """
    Unit test for the `create_folder_if_missing` function in the `folder_path` module.

    This test ensures that a folder is created if it does not exist, and that the function returns `True` if the folder already exists.
    """

    def setUp(self):
        """
        Prepare temporary folder paths for testing.
        """
        self.test_dir = os.path.join(os.getcwd(), "temp_test_dir")
        self.nested_dir = os.path.join(self.test_dir, "nested", "path")

        # Ensure cleanup before test
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def tearDown(self):
        """
        Clean up any folders created during tests.
        """
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_create_new_folder(self):
        """
        Should create the folder path when it does not already exist.
        """
        # ARRANGE
        dir_path = self.nested_dir

        # ASSERT pre-condition
        self.assertFalse(os.path.exists(dir_path))

        # ACT
        result = create_folder_if_missing(dir_path)
        exists = os.path.exists(dir_path)

        # ASSERT
        with self.subTest(Out=result, Exp=True):
            self.assertTrue(result)

        # Confirm that the folder actually exists on disk after function call,
        # even though the function performs this check internally.
        # This makes the test independent and validates the expected side effect.
        with self.subTest(Out=exists, Exp=True):
            self.assertTrue(os.path.isdir(dir_path))

    def test_folder_already_exists(self):
        """
        Should return True and make no changes when folder already exists.
        """
        # ARRANGE
        os.makedirs(self.nested_dir)
        self.assertTrue(os.path.isdir(self.nested_dir))

        # ACT
        result = create_folder_if_missing(self.nested_dir)
        still_exists = os.path.exists(self.nested_dir)

        # ASSERT
        with self.subTest(Out=result, Exp=True):
            self.assertTrue(result)
        with self.subTest(Out=still_exists, Exp=True):
            self.assertTrue(os.path.isdir(self.nested_dir))

    def test_invalid_path_raises_error(self):
        """
        Should raise OSError if the path is invalid (e.g., forbidden characters on Windows).
        """
        # ARRANGE
        # Use known-invalid path: reserved name on Windows or a protected path on Unix
        if os.name == "nt":
            invalid_path = "CON\\invalid"
        else:
            invalid_path = "/dev/null/invalid"

        expected = OSError.__name__

        # ACT
        # Capture the raised exception type without stopping the test
        try:
            create_folder_if_missing(invalid_path)
            result = ""  # No exception raised
        except OSError as e:
            result = type(e).__name__

        # ASSERT
        # Compare exception type name to expected
        with self.subTest(Out=result, Exp=expected):
            self.assertEqual(result, expected)


class TestGoUpOneFolder(unittest.TestCase):
    """
    Unit tests for the `go_up_one_folder` function in the folder_path module.
    """

    def test_happy_path(self):
        """
        Should return the parent folder when given a nested path.
        """
        # ARRANGE
        start_path = os.path.join(os.sep, "usr", "local", "bin")
        expected = normalize_folder_path(os.path.join(os.sep, "usr", "local"))

        # ACT
        result = go_up_one_folder(start_path)

        # ASSERT
        with self.subTest(Out=result, Exp=expected):
            self.assertEqual(result, expected)

    def test_root_path_stays_at_root(self):
        """
        Should return the same path when already at filesystem root.
        """
        # ARRANGE
        if os.name == "nt":
            # Use the current drive as root, e.g., 'C:\\'
            drive, _ = os.path.splitdrive(os.getcwd())
            root_path = normalize_folder_path(drive + os.sep)
        else:
            # POSIX root is '/'
            root_path = normalize_folder_path(os.sep)

        expected = root_path

        # ACT
        result = go_up_one_folder(root_path)

        # ASSERT
        with self.subTest(Out=result, Exp=expected):
            self.assertEqual(result, expected)

    def test_normalized(self):
        """
        Should normalize the input path before computing the parent.
        """
        # ARRANGE
        raw_path = os.path.join(os.sep, "usr", "local", "bin", "..", ".")
        # After normalization, parent should be '<sep>usr' on all platforms
        expected = normalize_folder_path(os.path.join(os.sep, "usr"))

        # ACT
        result = go_up_one_folder(raw_path)

        # ASSERT
        with self.subTest(Out=result, Exp=expected):
            self.assertEqual(result, expected)

    def test_raise(self):
        """
        Should raise TypeError when given a non-string input.
        """
        # ARRANGE
        bad_input = 12345
        expected = TypeError.__name__

        # ACT
        try:
            go_up_one_folder(bad_input)  # type: ignore[arg-type]
            result = None  # No exception raised
        except TypeError as e:
            result = type(e).__name__

        # ASSERT
        with self.subTest(Out=result, Exp=expected):
            self.assertEqual(result, expected)


class TestIsFolderPath(unittest.TestCase):
    """
    Unit test for the `is_folder_path` function in the folder_path module.

    This test ensures that various types of paths (valid folder path, file path, non-existent)
    are correctly evaluated to determine if they are existing folders.
    """

    def test_folder_path(self):
        """
        Should return True when given an existing folder path.
        """
        # ARRANGE
        with tempfile.TemporaryDirectory() as temp_dir:
            # ACT
            result = is_folder_path(temp_dir)

            # ASSERT
            with self.subTest(Out=result, Exp=True):
                self.assertTrue(result)

    def test_file_path(self):
        """
        Should return False when given a path to an existing file.
        """
        # ARRANGE
        with tempfile.TemporaryDirectory() as temp_dir:
            file_path = os.path.join(temp_dir, "file.txt")
            with open(file_path, "w") as f:
                f.write("test")

            # ACT
            result = is_folder_path(file_path)

            # ASSERT
            with self.subTest(Out=result, Exp=False):
                self.assertFalse(result)

    def test_non_existent_path(self):
        """
        Should return False when given a non-existent path.
        """
        # ARRANGE
        with tempfile.TemporaryDirectory() as temp_dir:
            non_existent = os.path.join(temp_dir, "does_not_exist")

            # ACT
            result = is_folder_path(non_existent)

            # ASSERT
            with self.subTest(Out=result, Exp=False):
                self.assertFalse(result)

    def test_empty_string_path(self):
        """
        Should return False when given an empty string as path.
        """
        # ACT
        result = is_folder_path("")

        # ASSERT
        with self.subTest(Out=result, Exp=False):
            self.assertFalse(result)


class TestListImmediateSubFolders(unittest.TestCase):
    """
    Unit test for the `list_immediate_sub_folders` function in the folder module.

    This test ensures the function returns the correct set of immediate sub folders,
    and raises appropriate errors for invalid paths.
    """

    def setUp(self):
        """
        Create a temporary folder structure for testing.
        """
        self.temp_dir = tempfile.TemporaryDirectory()
        self.base_path = self.temp_dir.name

        # Create sub folders and files
        os.mkdir(os.path.join(self.base_path, "subdir1"))
        os.mkdir(os.path.join(self.base_path, "subdir2"))
        with open(os.path.join(self.base_path, "file1.txt"), "w") as f:
            f.write("dummy")

    def tearDown(self):
        """
        Clean up the temporary folder structure.
        """
        self.temp_dir.cleanup()

    def test_sub_folder(self):
        """
        Should return only the names of immediate sub folders, excluding files.
        """
        # ARRANGE
        expected = ("subdir1", "subdir2")

        # ACT
        result = list_immediate_sub_folders(self.base_path)

        # ASSERT
        with self.subTest(Out=result, Exp=expected):
            self.assertCountEqual(result, expected)

    def test_no_sub_folders(self):
        """
        Should return an empty tuple when the folder has no sub folders.
        """
        # ARRANGE
        empty_dir = os.path.join(self.base_path, "empty")
        os.mkdir(empty_dir)

        # ACT
        result = list_immediate_sub_folders(empty_dir)

        # ASSERT
        with self.subTest(Out=result, Exp=()):
            self.assertEqual(result, ())

    def test_not_folder_path(self):
        """
        Should raise FileNotFoundError when the given path is not a folder.
        """
        # ARRANGE
        file_path = os.path.join(self.base_path, "file1.txt")
        expected = FileNotFoundError.__name__

        # ACT
        try:
            list_immediate_sub_folders(file_path)
            result = None  # No exception raised
        except FileNotFoundError as e:
            result = type(e).__name__

        # ASSERT
        with self.subTest(Out=result, Exp=expected):
            self.assertEqual(result, expected)

    def test_non_existent_path(self):
        """
        Should raise FileNotFoundError when the path does not exist.
        """
        # ARRANGE
        non_existent = os.path.join(self.base_path, "does_not_exist")
        expected = FileNotFoundError.__name__

        # ACT
        try:
            list_immediate_sub_folders(non_existent)
            result = None
        except FileNotFoundError as e:
            result = type(e).__name__

        # ASSERT
        with self.subTest(Out=result, Exp=expected):
            self.assertEqual(result, expected)


class TestNormalizeFolderPath(unittest.TestCase):
    """
    Unit test for the `normalize_dir_path` function in the folder module.

    This test verifies that various raw paths are normalized correctly and that
    invalid inputs raise appropriate errors.
    """

    def test_expand_folder(self):
        """
        Should expand '~' to the absolute home folder and normalize the result.
        """
        # ARRANGE
        raw_path = "~/test/folder"
        expected = os.path.normpath(os.path.expanduser(raw_path))

        # ACT
        result = normalize_folder_path(raw_path)

        # ASSERT
        with self.subTest(Out=result, Exp=expected):
            self.assertEqual(result, expected)

    def test_redundant_path_components(self):
        """
        Should normalize paths with one dot, two dots and duplicate slashes.
        """
        # ARRANGE
        raw_path = "./a/./b/../c//./../c/d/../e///"
        expected = os.path.normpath("a/c/e")

        # ACT
        result = normalize_folder_path(raw_path)

        # ASSERT
        with self.subTest(Out=result, Exp=expected):
            self.assertEqual(result, expected)

    def test_normalized_paths(self):
        """
        Should leave already normalized absolute paths unchanged.
        """
        # ARRANGE
        abs_path = os.path.join(os.sep, "usr", "local", "bin")
        expected = os.path.normpath(abs_path)

        # ACT
        result = normalize_folder_path(abs_path)

        # ASSERT
        with self.subTest(Out=result, Exp=expected):
            self.assertEqual(result, expected)

    def test_non_string_input(self):
        """
        Should raise TypeError if input is not a string.
        """
        # ARRANGE
        bad_input = 12345
        expected = TypeError.__name__

        # ACT
        try:
            normalize_folder_path(bad_input)  # type: ignore[arg-type]
            result = None
        except TypeError as e:
            result = type(e).__name__

        # ASSERT
        with self.subTest(Out=result, Exp=expected):
            self.assertEqual(result, expected)


class TestResolveDriveLetter(unittest.TestCase):
    """
    Unit test for the `resolve_drive_letter` function in the folder_path module.
    """

    def test_on_windows(self):
        """
        Should return the correct normalized drive letter when running on Windows.
        """
        if os.name != "nt":
            self.skipTest("resolve_drive_letter() is only supported on Windows systems.")

        # ARRANGE
        current_path = os.getcwd()
        expected_drive, _ = os.path.splitdrive(current_path)
        expected = normalize_folder_path(expected_drive + os.sep)

        # ACT
        result = resolve_drive_letter()

        # ASSERT
        with self.subTest(Out=result, Exp=expected):
            self.assertEqual(result, expected)


class TestResolveExeFolder(unittest.TestCase):
    """
    Unit test for the `resolve_exe_folder` function in the folder_path module.
    """

    def test_returns_valid_executable_folder(self):
        """
        Should return the folder containing the Python executable as a path.
        """
        # ARRANGE
        expected = normalize_folder_path(os.path.dirname(sys.executable))

        # ACT
        result = resolve_exe_folder()

        # ASSERT
        with self.subTest(Out=result, Exp=expected):
            self.assertEqual(result, expected)

    def test_raises_error_when_executable_folder_invalid(self):
        """
        Should raise FileNotFoundError if the executable folder does not exist or is invalid.

        This simulates an error by temporarily overriding `sys.executable`.
        """
        # ARRANGE
        original_executable = sys.executable
        sys.executable = "/invalid/fake/path/to/executable"
        expected = FileNotFoundError.__name__

        # ACT
        try:
            resolve_exe_folder()
            result = None  # No exception raised
        except FileNotFoundError as e:
            result = type(e).__name__
        finally:
            # CLEANUP
            sys.executable = original_executable

        # ASSERT
        with self.subTest(Out=result, Exp=expected):
            self.assertEqual(result, expected)


class TestResolveProjectFolder(unittest.TestCase):
    """
    Unit test for the `resolve_project_folder` function in the folder_path module.
    """

    def test_returns_existing_folder(self):
        """
        Should return an existing folder path as the project root.
        """
        # ACT
        result = resolve_project_folder()

        # ASSERT
        with self.subTest(Out=result, Exp="existing folder path"):
            self.assertTrue(is_folder_path(result))


if __name__ == "__main__":
    unittest.main()
