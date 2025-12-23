"""
Unit tests for internal UTF-8 text file writing helpers.

This module validates that the text file exporter:
    - Writes newline-joined UTF-8 text correctly
    - Rejects empty input and non-string lines
    - Enforces overwrite behavior consistently
    - Operates correctly using real filesystem paths

Example Usage:
    # Preferred usage via project-root invocation:
    python -m unittest tests/exporters/test__text_file.py

    # Direct discovery:
    python -m unittest discover -s tests

Dependencies:
    - Python >= 3.10
    - Standard Library: unittest, tempfile, os, shutil

Notes:
    - Tests use real temporary directories to validate filesystem side effects.
    - No mocking is used; behavior is verified end-to-end.
    - Exceptions are asserted by type, not message, to preserve refactor safety.

License:
    - Internal Use Only
"""

import os
import shutil
import tempfile
import unittest

# noinspection PyProtectedMember
from src.exporters import _text_file as tf, _dependencies as dep


class TestWriteTextFileLines(unittest.TestCase):
    """
    Unit tests for `write_text_file_lines` using a real temporary directory.

    These tests validate the function's input checks, orchestration, and expected side effects
    (writing a UTF-8 text file with newline-joined content) using a temp folder created per test.
    """

    def setUp(self):
        """
        Create a temporary directory for each test case.
        """
        # ARRANGE
        self.folder_path = tempfile.mkdtemp(prefix="test_text_file_")
        self.file_name: str | None = None
        self.file_path: str | None = None
        self.write_lines: tuple[str, ...] | None = None
        self.read_string: str | None = None

    def tearDown(self):
        """
        Remove the temporary directory after each test case.
        """
        if os.path.exists(self.folder_path):
            shutil.rmtree(self.folder_path)

    def generate_text_file_path(self):
        self.file_path = os.path.join(self.folder_path, self.file_name + dep.text_io.TEXT_FILE_TYPE)

    def read_text_file(self):
        with open(self.file_path, "r", encoding="utf-8") as f:
            self.read_string = f.read()

    def write_text_file(self):
        with open(self.file_path, "w", encoding="utf-8") as f:
            f.write("\n".join(self.write_lines))

    def test_happy_path(self):
        """
        Should write date to text file in the destination folder.
        """
        # ARRANGE
        self.file_name = "output"
        self.write_lines = ("line 1", "line 2")
        self.generate_text_file_path()
        expected_contents = "\n".join(self.write_lines)

        # ACT
        tf.write_text_file_lines(self.folder_path, self.file_name, self.write_lines)
        self.read_text_file()

        # ASSERT
        with self.subTest(Out=self.read_string, Exp=expected_contents):
            self.assertEqual(self.read_string, expected_contents)

    def test_empty_lines_raises(self):
        """
        Should raise an error when no text data is provided.
        """
        # ARRANGE
        self.file_name = "empty"
        self.write_lines = ()
        expected = RuntimeError.__name__

        # ACT
        try:
            tf.write_text_file_lines(self.folder_path, self.file_name, self.write_lines)
            result = ""
        except RuntimeError as e:
            result = type(e).__name__

        # ASSERT
        with self.subTest(Out=result, Exp=expected):
            self.assertEqual(result, expected)

    def test_non_string_line_raises(self):
        """
        Should raise an error when non-string data is provided.
        """
        # ARRANGE
        self.file_name = "bad"
        self.write_lines = ("ok", 123)
        expected = RuntimeError.__name__

        # ACT
        try:
            tf.write_text_file_lines(self.folder_path, self.file_name, self.write_lines)  # type: ignore[arg-type]
            result = ""
        except RuntimeError as e:
            result = type(e).__name__

        # ASSERT
        with self.subTest(Out=result, Exp=expected):
            self.assertEqual(result, expected)

    def test_overwrite_raise(self):
        """
        Should raise an error when overwrite is False and the target file already exists.
        """
        # ARRANGE
        self.file_name = "existing"
        self.write_lines = ("existing", "data")

        self.generate_text_file_path()
        self.write_text_file()

        self.write_lines = ("new data", "should not be written")
        expected = RuntimeError.__name__

        # ACT
        try:
            tf.write_text_file_lines(self.folder_path, self.file_name, self.write_lines, overwrite=False)
            result = ""
        except RuntimeError as e:
            result = type(e).__name__

        # ASSERT
        with self.subTest(Out=result, Exp=expected):
            self.assertEqual(result, expected)

    def test_overwrite(self):
        """
        Should overwrite an existing file when overwrite is True.
        """
        # ARRANGE
        self.file_name = "overwrite_me"
        self.write_lines = ("original", "data")

        self.generate_text_file_path()
        self.write_text_file()

        self.write_lines = ("new", "content")
        expected_contents = "\n".join(self.write_lines)

        # ACT
        tf.write_text_file_lines(self.folder_path, self.file_name, self.write_lines, overwrite=True)
        self.read_text_file()

        # ASSERT
        with self.subTest(Out=self.read_string, Exp=expected_contents):
            self.assertEqual(self.read_string, expected_contents)


if __name__ == '__main__':
    unittest.main()
