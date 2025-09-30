"""
Unit tests for common checker helpers.

This module validates shared utilities in `_common`, ensuring consistent behavior within the module. Tests confirm that helps run correctly, errors are captured and rendered correctly.

Example Usage:
    # Preferred usage via project-root invocation:
    python -m unittest tests/checkers/test__common.py

    # Direct discovery (runs all tests in the tree):
    python -m unittest discover -s tests

Dependencies:
    - Python >= 3.10
    - Standard Library: unittest
    - External Packages: None

Notes:
    -

License:
    - Internal Use Only
"""

import unittest

# noinspection PyProtectedMember
from src.checkers import _common as common  # Direct internal import — acceptable in tests


class TestErrorMsg(unittest.TestCase):
    """
    Unit tests for the `ErrorMsg` dataclass.
    """

    def test_valid(self):
        """
        Should correctly store all provided field values.
        """
        # ARRANGE
        expected = {
            "file_name": "Test.xlsx",
            "sheet_name": "P1",
            "section": "Row:10",
            "message": "Invalid Part Number",
        }

        # ACT
        err = common.ErrorMsg(**expected)

        # ASSERT
        for field_name, expected_value in expected.items():
            result_value = getattr(err, field_name)
            with self.subTest(Field=field_name, Out=result_value, Exp=expected_value):
                self.assertEqual(result_value, expected_value)

    def test_default(self):
        """
        Should default fields to empty strings when not provided.
        """
        # ARRANGE
        msg = "General error"

        # ACT
        err = common.ErrorMsg(message=msg)

        # ASSERT
        expected = {
            "file_name": "",
            "sheet_name": "",
            "section": "",
            "message": "General error",
        }
        for field_name, expected_value in expected.items():
            result_value = getattr(err, field_name)
            with self.subTest(Field=field_name, Out=result_value, Exp=expected_value):
                self.assertEqual(result_value, expected_value)

    def test_string_rep(self):
        """
        Should produce a string containing the class name and field values.
        """
        # ARRANGE
        err = common.ErrorMsg(file_name="Test.xlsx", sheet_name="P1", section="Row:10", message="Invalid Part Number")

        # ACT
        result_str = str(err)

        # ASSERT
        # Check presence of class name and field values
        expected_substrings = [
            "Test.xlsx",
            "P1",
            "Row:10",
            "Invalid Part Number",
        ]
        for substring in expected_substrings:
            with self.subTest(Substring=substring, In=result_str):
                self.assertIn(substring, result_str)


class TestErrorLog(unittest.TestCase):
    """
    Unit tests for the `ErrorLog` class.
    """

    def test_init(self):
        """
        Should start empty with blank context and zero length.
        """
        # ARRANGE
        log = common.ErrorLog()

        # ACT
        result_len = len(log)
        result_list = list(log)

        # ASSERT
        with self.subTest(Out=log.file_name, Exp=""):
            self.assertEqual(log.file_name, "")
        with self.subTest(Out=log.sheet_name, Exp=""):
            self.assertEqual(log.sheet_name, "")
        with self.subTest(Out=log.section_name, Exp=""):
            self.assertEqual(log.section_name, "")
        with self.subTest(Out=result_len, Exp=0):
            self.assertEqual(result_len, 0)
        with self.subTest(Out=result_list, Exp=[]):
            self.assertEqual(result_list, [])

    def test_setters(self):
        """
        Should update file, sheet, and section context fields.
        """
        # ARRANGE
        log = common.ErrorLog()

        # ACT
        log.set_file_name("BOM_Master.xlsx")
        log.set_sheet_name("P3")
        log.set_section_name("Row:4")

        # ASSERT
        with self.subTest(Out=log.file_name, Exp="BOM_Master.xlsx"):
            self.assertEqual(log.file_name, "BOM_Master.xlsx")
        with self.subTest(Out=log.sheet_name, Exp="P3"):
            self.assertEqual(log.sheet_name, "P3")
        with self.subTest(Out=log.section_name, Exp="Row:4"):
            self.assertEqual(log.section_name, "Row:4")

    def test_append_error(self):
        """
        Should append an ErrorMsg capturing the current context when message is non-empty.
        """
        # ARRANGE
        log = common.ErrorLog()
        log.set_file_name("Board.xlsx")
        log.set_sheet_name("EB1")
        log.set_section_name("Header")
        message = "Invalid header field"
        expected = {
            "file_name": "Board.xlsx",
            "sheet_name": "EB1",
            "section": "Header",
            "message": "Invalid header field",
        }

        # ACT
        log.append_error(message)
        result_len = len(log)
        [err] = list(log)  # exactly one

        # ASSERT
        with self.subTest(Out=result_len, Exp=1):
            self.assertEqual(result_len, 1)

        # Field-by-field compare (custom object guideline)
        for field, exp in expected.items():
            out = getattr(err, field)
            with self.subTest(Field=field, Out=out, Exp=exp):
                self.assertEqual(out, exp)

    def test_empty_message(self):
        """
        Should not append when message is empty.
        """
        # ARRANGE
        log = common.ErrorLog()
        log.set_file_name("X.xlsx")
        log.set_sheet_name("P1")
        log.set_section_name("Row:2")

        # ACT
        log.append_error("")  # empty -> ignored
        result_len = len(log)

        # ASSERT
        with self.subTest(Out=result_len, Exp=0):
            self.assertEqual(result_len, 0)

    def test_multiple_appends_preserve_order(self):
        """
        Should preserve insertion order across multiple appends and context changes.
        """
        # ARRANGE
        log = common.ErrorLog()
        log.set_file_name("A.xlsx")

        # First error under P1/Row:1
        log.set_sheet_name("P1")
        log.set_section_name("Row:1")
        log.append_error("Missing Part Number")

        # Second error under P2/Row:2
        log.set_sheet_name("P2")
        log.set_section_name("Row:2")
        log.append_error("Quantity Not Integer")

        # ACT
        errors = list(log)
        msgs_out = [e.message for e in errors]
        msgs_exp = ["Missing Part Number", "Quantity Not Integer"]

        # ASSERT
        with self.subTest(Out=msgs_out, Exp=msgs_exp):
            self.assertEqual(msgs_out, msgs_exp)

        # Also validate contexts stayed with each appended error
        expected_seq = [
            {"file_name": "A.xlsx", "sheet_name": "P1", "section": "Row:1"},
            {"file_name": "A.xlsx", "sheet_name": "P2", "section": "Row:2"},
        ]
        for idx, (err, exp_ctx) in enumerate(zip(errors, expected_seq), start=1):
            for field, exp in exp_ctx.items():
                out = getattr(err, field)
                with self.subTest(Index=idx, Field=field, Out=out, Exp=exp):
                    self.assertEqual(out, exp)

    def test_str(self):
        """
        Should return newline-joined `ErrorMsg.__str__()` outputs in insertion order.
        """
        # ARRANGE
        log = common.ErrorLog()
        log.set_file_name("Board.xlsx")

        log.set_sheet_name("P1")
        log.set_section_name("Header")
        log.append_error("Invalid header format")

        log.set_sheet_name("P2")
        log.set_section_name("Row:3")
        log.append_error("Missing required field")

        # Build expected using the same __str__ contract: "file | sheet | section | message"
        expected_lines = [
            "Board.xlsx | P1 | Header | Invalid header format",
            "Board.xlsx | P2 | Row:3 | Missing required field",
        ]
        expected_str = "\n".join(expected_lines)

        # ACT
        result_str = str(log)

        # ASSERT
        with self.subTest(Out=result_str, Exp=expected_str):
            self.assertEqual(result_str, expected_str)


if __name__ == "__main__":
    unittest.main()
