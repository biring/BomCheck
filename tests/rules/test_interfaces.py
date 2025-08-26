"""
Unit tests for the public interfaces of the `rules` package.

This module exercises representative valid and invalid paths across the validators exposed via `src.rules.interfaces`. It provides smoke coverage for the public API and ensures consistent exception behavior on malformed inputs.

This test module includes helpers to:
 - Verify valid inputs execute without raising exceptions
 - Verify invalid inputs consistently raise `ValueError`
 - Cover both single-cell and cross-cell (row-level) validation logic

These tests are intended as broad API-level checks and can be extended with edge-case or property-based tests as needed.

Example Usage (from project root):
    # Run test suite:
    python -m unittest tests.rules.test_interfaces

Dependencies:
    - Python >= 3.9
    - Standard Library: unittest
    - Internal: src.rules.interfaces, src.models.interfaces.Row

Notes:
    - Valid-case tests confirm silent acceptance of clearly correct examples.
    - Invalid-case tests cover common malformed or out-of-range inputs, expecting `ValueError`.
    - This module treats `src.rules.interfaces` as the public API surface; direct imports from submodules are not tested here.

License:
 - Internal Use Only
"""

import unittest

import src.rules.interfaces as rules

from src.models.interfaces import Row


class TestInterfacesCellValue(unittest.TestCase):
    """
    Smoke and negative tests for cell value validators in the public interface.

    Valid cases must run without raising exceptions. Invalid cases must raise ValueError.
    """

    def test_valid_inputs(self):
        """
        Should run without raising.
        """
        cases = [
            (rules.assert_price, "2.50"),  # non-negative numeric
            (rules.assert_qty, "3"),  # positive integer/decimal
            (rules.assert_item, "23"),  # positive integer-like
            (rules.assert_classification, "A"),  # typical single-letter class
            (rules.assert_date_format, "2025-08-06"),  # ISO-8601 date
            (rules.assert_board_name, "Main PCBA"),  # example name
            (rules.assert_model_number, "AB123"),  # example model number pattern
            (rules.assert_build_stage, "P1"),  # example build stage pattern
        ]
        expected = ""  # no error

        for func, value in cases:
            # ACT
            try:
                func(value)  # should not raise
                result = ""  # No error
            except Exception as e:  # noqa: BLE001 - explicit failure for any exception
                result = e.__class__.__name__
            # ASSERT
            with self.subTest(func=func.__name__, In=value, Out=result, Exp=expected):
                self.assertEqual(result, expected)

    def test_invalid_inputs(self):
        """
        Should raise ValueError
        """
        cases = [
            (rules.assert_price, "-1"),  # negative price
            (rules.assert_qty, "-5"),  # negative qty
            (rules.assert_item, "1.2"),  # not an integer
            (rules.assert_classification, "Z"),  # not a valid classification
            (rules.assert_date_format, "2025.08.06"),  # incorrect format with decimal separators
            (rules.assert_board_name, "Main PCB"),  # does not end with PCBA
            (rules.assert_model_number, "1A"),  # incorrect format
            (rules.assert_build_stage, "Alpha"),  # incorrect format
        ]
        expected = ValueError.__name__

        for func, value in cases:
            # ACT
            try:
                func(value)  # should not raise
                result = ""  # No error
            except Exception as e:  # noqa: BLE001 - explicit failure for any exception
                result = e.__class__.__name__
            # ASSERT
            with self.subTest(func=func.__name__, In=value, Out=result, Exp=expected):
                self.assertEqual(result, expected)


class TestInterfacesCellLogic(unittest.TestCase):
    """
    Smoke and negative tests for cross-cell logic validators in the public interface.

    Valid cases must run without raising exceptions. Invalid cases must raise ValueError.
    """

    def test_valid_inputs(self):
        """
        Should run without raising for representative valid rows.
        """
        # ARRANGE
        cases = [
            # qty > 0 when item >= 1
            (rules.assert_quantity_positive_when_item_positive, Row(item="1", qty="0.1")),

            # qty == 0 when item == ""
            (rules.assert_quantity_zero_when_item_blank, Row(item="", qty="0")),

            # designator required when item > 0 and qty >= 1
            (rules.assert_designator_required_for_positive_item_and_qty,
             Row(item="1", qty="1", designator="R1")),

            # designator count must match qty (comma-split)
            (rules.assert_designator_count_matches_quantity, Row(qty="3", designator="C1,C2,C3")),

            # unit_price > 0 when qty > 0
            (rules.assert_unit_price_positive_when_quantity_positive,
             Row(qty="2", unit_price="0.05")),

            # sub_total == 0 when qty == 0
            (rules.assert_subtotal_zero_when_quantity_zero, Row(qty="0", sub_total="0")),

            # sub_total == qty * unit_price (both > 0)
            (rules.assert_subtotal_matches_product,
             Row(qty="2", unit_price="3.25", sub_total="6.50")),
        ]
        expected = ""  # no error

        for func, row in cases:
            # ACT
            try:
                func(row)  # should not raise
                result = ""  # no error
            except Exception as e:  # noqa: BLE001
                result = e.__class__.__name__

            # ASSERT
            with self.subTest(func=func.__name__, In=row, Out=result, Exp=expected):
                self.assertEqual(result, expected)

    def test_invalid_inputs(self):
        """
        Should raise ValueError for representative invalid rows.
        """
        # ARRANGE
        cases = [
            # qty > 0 when item >= 1  → invalid: qty == 0
            (rules.assert_quantity_positive_when_item_positive, Row(item="1", qty="0")),

            # qty == 0 when item == "" → invalid: qty != 0
            (rules.assert_quantity_zero_when_item_blank, Row(item="", qty="1")),

            # designator required when item > 0 and qty >= 1 → invalid: missing designator
            (rules.assert_designator_required_for_positive_item_and_qty,
             Row(item="2", qty="1", designator="")),

            # designator count must match qty → invalid: 2 != 3
            (rules.assert_designator_count_matches_quantity, Row(qty="3", designator="C1,C2")),

            # unit_price > 0 when qty > 0 → invalid: unit_price == 0
            (rules.assert_unit_price_positive_when_quantity_positive, Row(qty="1", unit_price="0")),

            # sub_total == 0 when qty == 0 → invalid: sub_total != 0
            (rules.assert_subtotal_zero_when_quantity_zero, Row(qty="0.0", sub_total="0.01")),

            # sub_total == qty * unit_price → invalid: mismatch
            (rules.assert_subtotal_matches_product,
             Row(qty="2", unit_price="0.2", sub_total="0.5")),
        ]
        expected = ValueError.__name__

        for func, row in cases:
            # ACT
            try:
                func(row)  # should raise
                result = ""  # no error
            except Exception as e:  # noqa: BLE001
                result = e.__class__.__name__

            # ASSERT
            with self.subTest(func=func.__name__, In=row, Out=result, Exp=expected):
                self.assertEqual(result, expected)


if __name__ == "__main__":
    unittest.main()
