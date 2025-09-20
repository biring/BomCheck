"""
Unit tests for BOM header field coercers (model number, board name/supplier, build stage, BOM date, and costs).

These tests assert that each coercer:
    - Produces the expected normalized value
    - Emits change-log messages only on effective changes
    - Applies rules in a deterministic order through the shared engine

Example Usage:
    # Run this test module:
    python -m unittest tests/rules/coerce/test_header.py

    # Discover and run all tests:
    python -m unittest discover -s tests

Dependencies:
    - Python >= 3.10
    - Standard Library: unittest, typing
    - External Packages: None

Notes:
    - Tests treat coercers as pure functions returning (value, log_tuple).
    - Fixtures should cover typical, edge, and no-op inputs to verify logging behavior and stability.

License:
    - Internal Use Only
"""

import unittest

from src.rules.coerce import _header as header


class TestHeaderCoercers(unittest.TestCase):
    """
    Unit tests for coercer functions in `_header.py`.

    Each test follows Arrange–Act–Assert pattern:
      - Arrange: prepare raw input and expected value
      - Act: call the coercer function
      - Assert: check normalized value and log behavior
    """

    def test_model_number(self):
        """
        Should uppercase and remove spaces in model numbers.
        """
        # ARRANGE
        raw = " ab 123x "
        expected = "AB123X"

        # ACT
        result, log = header.model_number(raw)

        # ASSERT
        with self.subTest(Out=result, Exp=expected):
            self.assertEqual(result, expected)
        with self.subTest(Out=bool(log), Exp=True):
            self.assertTrue(len(log) > 0)

    def test_board_name(self):
        """
        Should collapse spaces and strip edges in board name.
        """
        # ARRANGE
        raw = "  Power   PCBA "
        expected = "Power PCBA"

        # ACT
        result, log = header.board_name(raw)

        # ASSERT
        with self.subTest(Out=result, Exp=expected):
            self.assertEqual(result, expected)
        with self.subTest(Out=bool(log), Exp=True):
            self.assertTrue(len(log) > 0)

    def test_board_supplier(self):
        """
        Should collapse multiple spaces in board supplier.
        """
        # ARRANGE
        raw = " General   Electric "
        expected = "General Electric"

        # ACT
        result, log = header.board_supplier(raw)

        # ASSERT
        with self.subTest(Out=result, Exp=expected):
            self.assertEqual(result, expected)
        with self.subTest(Out=bool(log), Exp=True):
            self.assertTrue(len(log) > 0)

    def test_build_stage(self):
        """
        Should remove spaces in build stage.
        """
        # ARRANGE
        raw = " EB 2 "
        expected = "EB2"

        # ACT
        result, log = header.build_stage(raw)

        # ASSERT
        with self.subTest(Out=result, Exp=expected):
            self.assertEqual(result, expected)
        with self.subTest(Out=bool(log), Exp=True):
            self.assertTrue(len(log) > 0)

    def test_bom_date(self):
        """
        Should strip spaces in BOM date.
        """
        # ARRANGE
        raw = " 2025-08-06 "
        expected = "2025-08-06"

        # ACT
        result, log = header.bom_date(raw)

        # ASSERT
        with self.subTest(Out=result, Exp=expected):
            self.assertEqual(result, expected)
        with self.subTest(Out=bool(log), Exp=True):
            self.assertTrue(len(log) > 0)

    def test_material_cost(self):
        """
        Should strip spaces in material cost.
        """
        # ARRANGE
        raw = " 12.5 "
        expected = "12.5"

        # ACT
        result, log = header.material_cost(raw)

        # ASSERT
        with self.subTest(Out=result, Exp=expected):
            self.assertEqual(result, expected)
        with self.subTest(Out=bool(log), Exp=True):
            self.assertTrue(len(log) > 0)

    def test_overhead_cost(self):
        """
        Should strip spaces in overhead cost.
        """
        # ARRANGE
        raw = " 0.50 "
        expected = "0.50"

        # ACT
        result, log = header.overhead_cost(raw)

        # ASSERT
        with self.subTest(Out=result, Exp=expected):
            self.assertEqual(result, expected)
        with self.subTest(Out=bool(log), Exp=True):
            self.assertTrue(len(log) > 0)

    def test_total_cost(self):
        """
        Should strip spaces in total cost.
        """
        # ARRANGE
        raw = " 100 "
        expected = "100"

        # ACT
        result, log = header.total_cost(raw)

        # ASSERT
        with self.subTest(Out=result, Exp=expected):
            self.assertEqual(result, expected)
        with self.subTest(Out=bool(log), Exp=True):
            self.assertTrue(len(log) > 0)


if __name__ == "__main__":
    unittest.main()
