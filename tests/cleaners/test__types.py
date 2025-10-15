"""
Unit tests for cleaners package internal data types.

Example Usage:
    # Preferred usage via project-root invocation:
    python -m unittest tests/cleaners/test__types.py

    # Direct discovery (runs all tests, including this module):
    python -m unittest discover -s tests

Dependencies:
    - Python >= 3.10
    - Standard Library: unittest, typing
    - External Packages: None

Notes:
    - Tests treat ChangeLog as a lightweight container where entries are plain messages and context is mutable.
    - Row rendering order and formatting are part of the contract.
    - Falsy messages must be ignored to maintain clean logs for downstream reporting.

License:
    - Internal Use Only
"""

import unittest
# noinspection PyProtectedMember
from src.cleaners._types import ChangeLog  # Direct internal import — acceptable in tests


class TestChangeLog(unittest.TestCase):
    """
    Unit tests for the `ChangeLog` aggregator.
    """

    def test_snapshot(self):
        """
        Should format rows as 'file | sheet | section | message' using current context.
        """
        # ARRANGE
        log = ChangeLog()
        log.set_file_name("bom.xlsx")
        log.set_sheet_name("P3")
        log.set_section_name("Header")
        log.add_entry("Normalized manufacturer names")
        log.add_entry("Collapsed internal whitespace")

        expected = (
            "bom.xlsx | P3 | Header | Normalized manufacturer names",
            "bom.xlsx | P3 | Header | Collapsed internal whitespace",
        )

        # ACT
        rows = log.to_frozen_list()

        # ASSERT
        with self.subTest("Row Count", Out=len(rows), Exp=len(expected)):
            self.assertEqual(len(rows), len(expected))
        for out_row, exp_row in zip(rows, expected):
            with self.subTest("Row", Out=out_row, Exp=exp_row):
                self.assertEqual(out_row, exp_row)

    def test_add_empty_message(self):
        """
        Should not append entries when message is an empty string (falsy check).
        """
        # ARRANGE
        log = ChangeLog()
        log.set_file_name("a.xlsx")
        log.set_sheet_name("S1")
        log.set_section_name("Items")
        log.add_entry("")  # falsy → ignored
        log.add_entry("Applied masks")  # kept

        expected_len = 1

        # ACT
        rows = log.to_frozen_list()

        # ASSERT
        with self.subTest("Entries", Out=len(rows), Exp=expected_len):
            self.assertEqual(len(rows), expected_len)
        with self.subTest("Row0 EndsWith", Out=rows[0].endswith("Applied masks"), Exp=True):
            self.assertTrue(rows[0].endswith("Applied masks"))

    def test_context(self):
        """
        Should render all stored messages with the *current* context at snapshot time.
        (Entries store only messages; file/sheet/section are taken when snapshot is called.)
        """
        # ARRANGE
        log = ChangeLog()
        log.set_file_name("v1.xlsx")
        log.set_sheet_name("EB0")
        log.set_section_name("Meta")
        log.add_entry("Rule A")

        # Change context after adding messages
        log.set_file_name("v2.xlsx")
        log.set_sheet_name("MP")
        log.set_section_name("Table")

        expected = ("v2.xlsx | MP | Table | Rule A",)

        # ACT
        rows = log.to_frozen_list()

        # ASSERT
        with self.subTest("Context After Change", Out=rows, Exp=expected):
            self.assertEqual(rows, expected)


if __name__ == "__main__":
    unittest.main()
