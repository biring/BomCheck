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

import unittest
from src.common import ChangeLog


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


if __name__ == "__main__":
    unittest.main()
