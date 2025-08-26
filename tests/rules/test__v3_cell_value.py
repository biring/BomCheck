"""
Unit tests for version 3 BOM cell value rules.

This module verifies that individual cell validators:
    - Accept valid inputs without side effects
    - Raise `ValueError` with informative messages for invalid inputs
    - Cover regex-driven fields (board name, model number, build stage), date formats, and numeric constraints (price, quantity, item, classification)

These tests are intended to guard schema/format contracts used by BOM parsing and rule-checking pipelines.

Example Usage (from project root):
    # Run test suite:
    python -m unittest tests.rules.test__v3_cell_value

Dependencies:
    - Python >= 3.9
    - Standard Library: unittest
    - Internal: src.rules._v3_cell_value, src.rules._helpers (indirect)

Notes:
    - Uses `subTest` to keep failures localized and readable.
    - Treats the target as an internal module; direct imports are acceptable in unit tests.
    - Date validation allows zero/non‑zero‑padded inputs and ignores trailing time parts (validation is for the date portion only).
    - Numeric rules: price/qty accept non-negative numeric strings (with empty allowed for price), item accepts "" or positive integers only, classification accepts "", "A", "B", or "C".
    - Error messages are part of the contract; keep assertions strict to catch regressions.

License:
 - Internal Use Only
"""

import unittest

# noinspection PyProtectedMember
import src.rules._v3_cell_value as cell_value  # Direct internal import — acceptable in tests


class TestAssertModelNumber(unittest.TestCase):
    """
    Unit test for the `assert_model_number` function.
    """

    def test_valid(self):
        """
        Should succeed silently when the input matches the required model number pattern.
        """
        # ARRANGE
        valid_values = [
            "AB123",
            "X9Y",
            "Model42X",
            "XYZ999",
            "A1",
            "abc123",
            "Z0"
        ]
        expected = ""  # No error

        for value in valid_values:
            try:
                # ACT
                cell_value.assert_model_number(value)
                result = ""  # No error
            except ValueError:
                result = ValueError.__name__

            # ASSERT
            with self.subTest(In=value, Out=result, Exp=expected):
                self.assertEqual(result, expected)

    def test_invalid(self):
        """
        Should raise ValueError when the input does not match the required model number pattern.
        """
        # ARRANGE
        invalid_values = [
            "123AB",
            "AB",
            "123",
            "A_123",
            "AB-123",
            "",
            "   "
        ]
        expected = ValueError.__name__

        for value in invalid_values:
            try:
                # ACT
                cell_value.assert_model_number(value)
                result = ""  # No error
            except ValueError:
                result = ValueError.__name__

            # ASSERT
            with self.subTest(In=value, Out=result, Exp=expected):
                self.assertEqual(result, expected)


class TestAssertBoardName(unittest.TestCase):
    """
    Unit tests for `assert_board_name`.
    """

    def test_valid(self):
        """
        Should accept names starting with a letter, using letters/digits/spaces, and ending with 'PCBA' (uppercase).
        """
        # ARRANGE
        valid_values = [
            "Control PCBA",
            "Battery 1 PCBA",
            "Headlight Left PCBA",
            "A PCBA",
            "MainBoard 2 PCBA",
        ]
        expected = ""  # No error

        for value in valid_values:
            try:
                # ACT
                cell_value.assert_board_name(value)
                result = ""  # No error
            except ValueError:
                result = ValueError.__name__

            # ASSERT
            with self.subTest(In=value, Out=result, Exp=expected):
                self.assertEqual(result, expected)

    def test_invalid(self):
        """
        Should raise ValueError for names not matching the strict pattern.
        """
        # ARRANGE
        invalid_values = [
            "1Control PCBA",  # starts with digit
            "Control pcbA",  # wrong case on suffix
            "Control-PCBA",  # hyphen not allowed
            "Control",  # missing 'PCBA' suffix
            " PCBA",  # starts with space, first char must be a letter
            "PCBA",  # does not fit the regex structure (see pattern semantics)
        ]
        expected = ValueError.__name__

        for value in invalid_values:
            try:
                # ACT
                cell_value.assert_board_name(value)
                result = ""  # No error
            except ValueError:
                result = ValueError.__name__

            # ASSERT
            with self.subTest(In=value, Out=result, Exp=expected):
                self.assertEqual(result, expected)


class TestAssertBuildStage(unittest.TestCase):
    """
    Unit tests for `assert_build_stage`.
    """

    def test_valid(self):
        """
        Should accept documented build stage formats.
        """
        # ARRANGE
        valid_values = [
            "P1", "P1.2",
            "EB2", "EB2.3",
            "ECN", "ECN12",
            "MB", "MP", "FOT",
        ]
        expected = ""  # No error

        for value in valid_values:
            try:
                # ACT
                cell_value.assert_build_stage(value)
                result = ""  # No error
            except ValueError:
                result = ValueError.__name__

            # ASSERT
            with self.subTest(In=value, Out=result, Exp=expected):
                self.assertEqual(result, expected)

    def test_invalid(self):
        """
        Should raise ValueError for patterns outside the allowed set.
        """
        # ARRANGE
        invalid_values = [
            "P", "P.", "P1.",  # incomplete decimals
            "EB", "EB.",  # missing digits
            "ECN12.3",  # ECN allows optional integer only
            "XP1",  # unknown prefix
            "MP1", "MB2",  # MB/MP must be exact
            "FOT1",  # FOT must be exact
            "", "  "
        ]
        expected = ValueError.__name__

        for value in invalid_values:
            try:
                # ACT
                cell_value.assert_build_stage(value)
                result = ""  # No error
            except ValueError:
                result = ValueError.__name__

            # ASSERT
            with self.subTest(In=value, Out=result, Exp=expected):
                self.assertEqual(result, expected)


class TestAssertDateFormat(unittest.TestCase):
    """
    Unit tests for `assert_date_format`.
    """

    def test_valid(self):
        """
        Should accept exact formats and inputs with a trailing time part (date portion only is validated).
        """
        # ARRANGE
        valid_values = [
            "2025-08-06",  # YYYY-MM-DD (zero-padded)
            "2025-8-6",  # YYYY-M-D (non-zero-padded acceptable via helper)
            "06/08/2025",  # DD/MM/YYYY (zero-padded)
            "6/8/2025",  # D/M/YYYY (non-zero-padded)
            "08/06/2025",  # MM/DD/YYYY (zero-padded)
            "8/6/2025",  # M/D/YYYY (non-zero-padded)
            "2025-08-06T12:30",
            "2025-08-06 09:15",
        ]
        expected = ""  # No error

        for value in valid_values:
            try:
                # ACT
                cell_value.assert_date_format(value)
                result = ""  # No error
            except ValueError:
                result = ValueError.__name__

            # ASSERT
            with self.subTest(In=value, Out=result, Exp=expected):
                self.assertEqual(result, expected)

    def test_invalid(self):
        """
        Should raise ValueError for non-supported formats or impossible dates.
        """
        # ARRANGE
        invalid_values = [
            "2025/08/06",  # wrong separator for YYYY-MM-DD
            "06-08-2025",  # wrong separator for DD/MM/YYYY
            "2025-13-01",  # invalid month
            "2025-00-10",  # invalid month
            "2025-02-30",  # invalid day
            "not-a-date",  # junk
            "", "   ",
        ]
        expected = ValueError.__name__

        for value in invalid_values:
            try:
                # ACT
                cell_value.assert_date_format(value)
                result = ""  # No error
            except ValueError:
                result = ValueError.__name__

            # ASSERT
            with self.subTest(In=value, Out=result, Exp=expected):
                self.assertEqual(result, expected)


class TestAssertPrice(unittest.TestCase):
    """
    Unit tests for `assert_price`.
    """

    def test_valid(self):
        """
        Should accept empty, zero and positive float representations.
        """
        # ARRANGE
        valid_values = [
            "",  # empty
            "0",  # zero int
            "0.00",  # zero float
            "12.5",  # positive gloat
            "3",  # positive float
        ]
        expected = ""  # No error

        for value in valid_values:
            try:
                # ACT
                cell_value.assert_price(value)
                result = ""  # No error
            except ValueError:
                result = ValueError.__name__

            # ASSERT
            with self.subTest(In=value, Out=result, Exp=expected):
                self.assertEqual(result, expected)

    def test_invalid(self):
        """
        Should raise ValueError for negatives or non-floats.
        """
        # ARRANGE
        invalid_values = [
            " ",  # not empty
            "a",  # not a number
            "-1",  # negative int
            "-0.01",  # negative float
            "abc",  # not a number
            "1.2.3",  # not a number
        ]
        expected = ValueError.__name__

        for value in invalid_values:
            try:
                # ACT
                cell_value.assert_price(value)
                result = ""  # No error
            except ValueError:
                result = ValueError.__name__

            # ASSERT
            with self.subTest(In=value, Out=result, Exp=expected):
                self.assertEqual(result, expected)


class TestAssertQty(unittest.TestCase):
    """
    Unit tests for `assert_qty`.
    """

    def test_valid(self):
        """
        Should accept zero and positive numerical strings.
        """
        # ARRANGE
        valid_values = ["0", "0.0", "1", "3.75", "10.000"]
        expected = ""  # No error

        for value in valid_values:
            try:
                # ACT
                cell_value.assert_qty(value)
                result = ""  # No error
            except ValueError:
                result = ValueError.__name__

            # ASSERT
            with self.subTest(In=value, Out=result, Exp=expected):
                self.assertEqual(result, expected)

    def test_invalid(self):
        """
        Should raise ValueError for negatives or non-float inputs.
        """
        # ARRANGE
        invalid_values = ["-0.001", "-1", "abc", "1.2.3", "", " "]
        expected = ValueError.__name__

        for value in invalid_values:
            try:
                # ACT
                cell_value.assert_qty(value)
                result = ""  # No error
            except ValueError:
                result = ValueError.__name__

            # ASSERT
            with self.subTest(In=value, Out=result, Exp=expected):
                self.assertEqual(result, expected)


class TestAssertItem(unittest.TestCase):
    """
    Unit tests for `assert_item`.
    """

    def test_valid(self):
        """
        Should accept empty string and positive integers.
        """
        # ARRANGE
        valid_values = ["", "1", "42", "999999"]
        expected = ""  # No error

        for value in valid_values:
            try:
                # ACT
                cell_value.assert_item(value)
                result = ""  # No error
            except ValueError:
                result = ValueError.__name__

            # ASSERT
            with self.subTest(In=value, Out=result, Exp=expected):
                self.assertEqual(result, expected)

    def test_invalid(self):
        """
        Should raise ValueError for zero, negatives, non-integers, and whitespace-only strings.
        """
        # ARRANGE
        invalid_values = ["0", "-1", "1.0", "abc", " ", "  \t"]
        expected = ValueError.__name__

        for value in invalid_values:
            try:
                # ACT
                cell_value.assert_item(value)
                result = ""  # No error
            except ValueError:
                result = ValueError.__name__

            # ASSERT
            with self.subTest(In=value, Out=result, Exp=expected):
                self.assertEqual(result, expected)


class TestAssertClassification(unittest.TestCase):
    """
    Unit tests for `assert_classification`.
    """

    def test_valid(self):
        """
        Should succeed silently when classification is A, B, C or empty.
        """
        # ARRANGE
        valid_values = [
            "A",
            "B",
            "C",
            "",
        ]
        expected = ""  # No error

        for value in valid_values:
            # ACT
            try:
                cell_value.assert_classification(value)
                result = ""  # No error
            except ValueError:
                result = ValueError.__name__

            # ASSERT
            with self.subTest(In=value, Out=result, Exp=expected):
                self.assertEqual(result, expected)

    def test_invalid(self):
        """
        Should raise ValueError when classification is not A, B, C or empty.
        """
        # ARRANGE
        invalid_values = [
            " ",  # not empty
            "a",  # small cap
            "abc",  # string
            "Y",  # From BOM template version 2
            "N",  # From BOM template version 2
            "1",  # number
            "-5.01",  # float
        ]
        expected = ValueError.__name__

        for value in invalid_values:
            # ACT
            try:
                cell_value.assert_classification(value)
                result = ""  # No error
            except ValueError:
                result = ValueError.__name__

            # ASSERT
            with self.subTest(In=value, Out=result, Exp=expected):
                self.assertEqual(result, expected)


if __name__ == "__main__":
    unittest.main()
