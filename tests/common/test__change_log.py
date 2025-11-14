"""
Unit tests for the internal ChangeLog component.

These tests verify that:
    - Only non-empty messages are recorded
    - Rendering applies the latest context values
    - Output formatting and ordering are stable and deterministic

Example Usage:
    # Preferred usage via project-root invocation:
    python -m unittest tests/common/test__change_log.py

    # Direct test discovery:
    python -m unittest discover -s tests

Dependencies:
    - Python >= 3.10
    - Standard Library: unittest, typing
    - External Packages: None

Notes:
    - Direct import of src.common._change_log is intentional for testing internals.
    - Tests assert behavior and output formatting, not internal implementation details.

License:
    - Internal Use Only
"""

import unittest
# noinspection PyProtectedMember
from src.common._change_log import ChangeLog  # Direct internal import — acceptable in tests


class TestChangeLog(unittest.TestCase):
    """
    Unit test for the `ChangeLog` function.
    """

    def test_snapshot(self):
        """
        Should render each non-empty message as 'file | sheet | section | message' using the current context.
        """
        # ARRANGE
        log = ChangeLog()
        log.set_module_name("test")
        log.set_file_name("bom.xlsx")
        log.set_sheet_name("P3")
        log.set_section_name("Header")
        log.add_entry("Normalized manufacturer names")
        log.add_entry("Collapsed internal whitespace")

        expected = (
            "test | bom.xlsx | P3 | Header | Normalized manufacturer names",
            "test | bom.xlsx | P3 | Header | Collapsed internal whitespace",
        )

        # ACT
        rows = log.render()

        # ASSERT
        with self.subTest("Row Count", Out=len(rows), Exp=len(expected)):
            self.assertEqual(len(rows), len(expected))
        for out_row, exp_row in zip(rows, expected):
            with self.subTest("Row", Out=out_row, Exp=exp_row):
                self.assertEqual(out_row, exp_row)

    def test_add_empty_message(self):
        """
        Should skip blank or whitespace-only messages and keep only valid entries.
        """
        # ARRANGE
        sample_log_entry = "Applied masks"
        log = ChangeLog()
        log.set_module_name("test")
        log.set_file_name("a.xlsx")
        log.set_sheet_name("S1")
        log.set_section_name("Items")
        log.add_entry("")  # empty should be ignored
        log.add_entry(" ")  # white space should be ignored
        log.add_entry("\t")  # white space should be ignored
        log.add_entry(sample_log_entry)  # kept

        expected_len = 1

        # ACT
        log_list = log.render()

        # ASSERT
        with self.subTest("Entries", Out=len(log_list), Exp=expected_len):
            self.assertEqual(len(log_list), expected_len)
        with self.subTest("Log Entry", Out=log_list[0], Exp=sample_log_entry):
            self.assertIn(sample_log_entry, log_list[0])

    def test_context(self):
        """
        Should apply the latest file, sheet, and section context when rendering log entries at snapshot time.
        """
        # ARRANGE
        log = ChangeLog()
        log.set_module_name("test_context")
        log.set_file_name("v1.xlsx")
        log.set_sheet_name("EB0")
        log.set_section_name("Meta")
        log.add_entry("Rule A")

        # Change context after adding messages
        log.set_file_name("v2.xlsx")
        log.set_sheet_name("MP")
        log.set_section_name("Table")

        expected = ("test_context | v2.xlsx | MP | Table | Rule A",)

        # ACT
        rows = log.render()

        # ASSERT
        with self.subTest("Context After Change", Out=rows, Exp=expected):
            self.assertEqual(rows, expected)


if __name__ == "__main__":
    unittest.main()
