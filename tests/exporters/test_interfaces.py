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
import unittest
from dataclasses import replace

from tests.fixtures import v3_bom as fixture

from src.exporters import interfaces as exporter


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


if __name__ == "__main__":
    unittest.main()
