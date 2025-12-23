"""
Happy-path integration tests for the exporter interfaces façade.

Example Usage:
    # Via unittest runner (preferred):
    python -m unittest tests/exporters/test_interfaces.py

    # Discover and run all tests:
    python -m unittest discover -s tests

Dependencies:
    - Python >= 3.10
    - Standard Library:
    - External Packages:

Notes:
    - Tests treat the exporter façade as an integration boundary, ensuring internal helpers are invoked correctly.


License:
    - Internal Use Only
"""
import os
import tempfile
import unittest
from dataclasses import replace
from tests.fixtures import v3_bom as fixture
from src.exporters import interfaces as exporter
# noinspection PyProtectedMember
from src.exporters import _dependencies as dep


class TestInterfaces(unittest.TestCase):
    """
    Integration-style tests for the `exporters` public interface.
    """

    def test_build_checker_log_filename(self):
        """
        Should return a filename string with a reasonable minimum length.
        """
        # ARRANGE
        bom = fixture.BOM_A
        expected_type = str
        expected_min_length = 16  # Date (6) + model number (5) + build stage (2) + suffix (3) should be > 16

        # ACT
        actual = exporter.build_checker_log_filename(bom)
        actual_type = type(actual)
        actual_length = len(actual)

        # ASSERT
        with self.subTest("Type", Out=actual_type, Exp=expected_type):
            self.assertEqual(actual_type, expected_type)
        with self.subTest("Minimum length", Out=actual_length, Min=expected_min_length):
            self.assertGreater(actual_length, expected_min_length)

    def test_build_checker_log_filename_raises(self):
        """
        Should raise RuntimeError when the BOM does not contain required header metadata needed to build a checker log filename.
        """
        # ARRANGE
        bom = replace(fixture.BOM_A, boards=())  # No boards in the bom
        expected_exc = RuntimeError

        # ACT
        try:
            exporter.build_checker_log_filename(bom)
            actual = ""  # No exception raised
        except Exception as e:
            actual = type(e)

        # ASSERT
        with self.subTest(Out=actual, Exp=expected_exc):
            self.assertEqual(actual, expected_exc)


class TestWriteTextFileLines(unittest.TestCase):
    """
    Unit tests for the `write_text_file_lines` exporter interface.
    """

    def test_writes_lines_to_text_file(self):
        """
        Should write the provided lines to a UTF-8 text file with the expected extension.
        """
        # ARRANGE
        with tempfile.TemporaryDirectory() as tmp_dir:
            folder = tmp_dir
            file_name = "checker_log"
            lines = ("Line 1", "Line 2", "Line 3")

            expected_path = os.path.join(folder, file_name + dep.text_io.TEXT_FILE_TYPE)
            expected_contents = "\n".join(lines)

            # Pre-condition: file does not exist yet
            self.assertFalse(os.path.exists(expected_path))

            # ACT
            exporter.write_text_file_lines(folder, file_name, lines)

            # ASSERT
            exists = os.path.isfile(expected_path)
            with self.subTest(Out=exists, Exp=True):
                self.assertTrue(exists)

            with open(expected_path, "r", encoding="utf-8") as f:
                actual_contents = f.read()

            with self.subTest(Out=actual_contents, Exp=expected_contents):
                self.assertEqual(actual_contents, expected_contents)

    def test_does_not_overwrite_when_disabled(self):
        """
        Should raise RuntimeError when overwrite is False and the target file already exists.
        """
        # ARRANGE
        with tempfile.TemporaryDirectory() as tmp_dir:
            folder = tmp_dir
            file_name = "checker_log"
            lines_initial = ("Original",)
            lines_new = ("New content",)
            overwrite = False

            expected_path = os.path.join(folder, file_name + dep.text_io.TEXT_FILE_TYPE)
            expected_exc = RuntimeError

            # Create the initial file
            exporter.write_text_file_lines(folder, file_name, lines_initial)
            self.assertTrue(os.path.isfile(expected_path))

            # ACT
            try:
                exporter.write_text_file_lines(folder, file_name, lines_new, overwrite=overwrite)
                actual = ""  # No exception raised
            except Exception as e:
                actual = type(e)

            # ASSERT
            with self.subTest(Out=actual, Exp=expected_exc):
                self.assertEqual(actual, expected_exc)

            # Verify file contents were not changed
            with open(expected_path, "r", encoding="utf-8") as f:
                actual_contents = f.read()
            expected_contents = "\n".join(lines_initial)

            with self.subTest(Out=actual_contents, Exp=expected_contents):
                self.assertEqual(actual_contents, expected_contents)

    def test_raises(self):
        """
        Should raise RuntimeError when no lines are provided.
        """
        # ARRANGE
        with tempfile.TemporaryDirectory() as tmp_dir:
            folder = tmp_dir
            file_name = "checker_log"
            lines = ()
            expected_exc = RuntimeError

            # ACT
            try:
                exporter.write_text_file_lines(folder, file_name, lines)
                actual = ""  # No exception raised
            except Exception as e:
                actual = type(e)

            # ASSERT
            with self.subTest(Out=actual, Exp=expected_exc):
                self.assertEqual(actual, expected_exc)


if __name__ == "__main__":
    unittest.main()
