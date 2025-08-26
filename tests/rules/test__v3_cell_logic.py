"""
Unit tests for version 3 BOM cross-cell rules.

Each test ensures that rules succeed silently when satisfied, raise `ValueError` on violation, and skip gracefully (no error) when base fields are invalid.

Example Usage (from project root):
    # Run test suite:
    python -m unittest tests.rules.test__v3_cell_logic

Dependencies:
    - Python >= 3.9
    - Standard Library: unittest
    - Internal:
        - src.models.interfaces.Row
        - src.rules._v3_cell_logic

Notes:
    - Organized into dedicated `Test*` classes, one per validator.
    - Each class groups tests into `valid_silent`, `valid_raise`, and `invalid_pass`.
    - Uses `subTest` for clearer failure diagnostics across row variations.
    - Direct import of `_v3_cell_logic` is acceptable here since this is a test module.

License:
 - Internal Use Only
"""

import unittest

from src.models.interfaces import Row

# noinspection PyProtectedMember
import src.rules._v3_cell_logic as cl  # Direct internal import — acceptable in tests


class TestAssertQuantityPositiveWhenItemPositive(unittest.TestCase):
    """
    Unit tests for `assert_quantity_positive_when_item_positive`.

    Test categories:
      - valid silent: rule satisfied → no error
      - valid raise: rule violated → ValueError
      - invalid pass: base field invalid → validation skipped (no error)
    """

    def test_valid_silent(self):
        """
        Should succeed silently when item >= 1 and qty > 0.0.
        """
        # ARRANGE
        rows = [
            Row(item="1", qty="15.7"),
            Row(item="2", qty="3"),
            Row(item="3", qty="0.1"),
        ]
        expected = ""  # No error

        for row in rows:
            # ACT
            try:
                cl.assert_quantity_positive_when_item_positive(row)
                result = ""  # No error
            except ValueError:
                result = ValueError.__name__

            # ASSERT
            with self.subTest(In={"item": row.item, "qty": row.qty}, Out=result, Exp=expected):
                self.assertEqual(result, expected)

    def test_valid_raise(self):
        """
        Should raise ValueError when item >= 1 and qty <= 0.0.
        """
        # ARRANGE
        rows = [
            Row(item="2", qty="0"),  # incorrect qty (zero)
            Row(item="5", qty="0.0"),  # incorrect qty (zero)
            Row(item="10", qty="-0.0"),  # incorrect qty (zero)
            Row(item="3", qty="-2"),  # invalid qty (negative)
        ]
        expected = ValueError.__name__

        for row in rows:
            # ACT
            try:
                cl.assert_quantity_positive_when_item_positive(row)
                result = ""  # No error
            except ValueError:
                result = ValueError.__name__

            # ASSERT
            with self.subTest(In={"item": row.item, "qty": row.qty}, Out=result, Exp=expected):
                self.assertEqual(result, expected)

    def test_invalid_pass(self):
        """
        Should skip validation (no error) when any base field is invalid.
        """
        # ARRANGE
        rows = [
            Row(item="A", qty="1"),  # invalid item (string)
            Row(item="", qty="5"),  # invalid item (empty)
            Row(item="0", qty="5"),  # invalid item (zero)
            Row(item="-1", qty="2"),  # invalid item (negative)
            Row(item="2", qty=""),  # invalid qty (empty)
            Row(item="2", qty="NaN"),  # invalid qty (not a number)
            Row(item="3", qty="abc"),  # invalid qty (string)
        ]
        expected = ""  # No error because function should early-return

        for row in rows:
            # ACT
            try:
                cl.assert_quantity_positive_when_item_positive(row)
                result = ""  # No error
            except Exception as e:
                result = type(e).__name__

            # ASSERT
            with self.subTest(In={"item": row.item, "qty": row.qty}, Out=result, Exp=expected):
                self.assertEqual(result, expected)


class TestAssertQuantityZeroWhenItemBlank(unittest.TestCase):
    """
    Unit tests for `assert_quantity_zero_when_item_blank`.

    Test categories:
      - valid silent: rule satisfied → no error
      - valid raise: rule violated → ValueError
      - invalid pass: base field invalid → validation skipped (no error)
    """

    def test_valid_silent(self):
        """
        Should succeed silently when item is blank and qty == 0.0.
        """
        # ARRANGE
        rows = [
            Row(item="", qty="0"),
            Row(item="", qty="0.0"),
        ]
        expected = ""  # No error

        for row in rows:
            # ACT
            try:
                cl.assert_quantity_zero_when_item_blank(row)
                result = ""  # No error
            except ValueError:
                result = ValueError.__name__

            # ASSERT
            with self.subTest(In={"item": row.item, "qty": row.qty}, Out=result, Exp=expected):
                self.assertEqual(result, expected)

    def test_valid_raise(self):
        """
        Should raise ValueError when item is blank and qty != 0.0.
        """
        # ARRANGE
        rows = [
            Row(item="", qty="0.01"),  # incorrect qty (not zero)
            Row(item="", qty="2"),  # incorrect qty (not zero)
            Row(item="", qty="-1"),  # incorrect qty (not zero)
        ]
        expected = ValueError.__name__

        for row in rows:
            # ACT
            try:
                cl.assert_quantity_zero_when_item_blank(row)
                result = ""  # No error (unexpected)
            except ValueError:
                result = ValueError.__name__

            # ASSERT
            with self.subTest(In={"item": row.item, "qty": row.qty}, Out=result, Exp=expected):
                self.assertEqual(result, expected)

    def test_invalid_pass(self):
        """
        Should skip validation (no error) when any base field is invalid.
        """
        # ARRANGE
        rows = [
            Row(item="1", qty="0"),  # invalid item (not zero)
            Row(item="", qty="NaN"),  # invalid qty (not float)
            Row(item="", qty=""),  # invalid qty (empty)
        ]
        expected = ""  # No error due to early return

        for row in rows:
            # ACT
            try:
                cl.assert_quantity_zero_when_item_blank(row)
                result = ""  # No error
            except Exception as e:
                result = type(e).__name__

            # ASSERT
            with self.subTest(In={"item": row.item, "qty": row.qty}, Out=result, Exp=expected):
                self.assertEqual(result, expected)


class TestAssertDesignatorRequiredForPositiveItemAndQty(unittest.TestCase):
    """
    Unit tests for `assert_designator_required_for_positive_item_and_qty`.

    Notes:
      The function validates item and qty first; if either is invalid, it returns early (invalid pass).
      When item > 0 and qty ≥ 1.0, designator must be non-empty.
    """

    def test_valid_silent(self):
        """
        Should succeed silently when item > 0, qty ≥ 1.0, and designator is non-empty.
        """
        # ARRANGE
        rows = [
            Row(item="1", qty="1", designator="R1"),
            Row(item="2", qty="3.0", designator="C1,C2,C3"),
        ]
        expected = ""  # No error

        for row in rows:
            # ACT
            try:
                cl.assert_designator_required_for_positive_item_and_qty(row)
                result = ""
            except ValueError:
                result = ValueError.__name__

            # ASSERT
            with self.subTest(In={"item": row.item, "qty": row.qty, "designator": row.designator},
                              Out=result, Exp=expected
                              ):
                self.assertEqual(result, expected)

    def test_valid_raise(self):
        """
        Should raise ValueError when item > 0, qty ≥ 1.0, and designator is empty.
        """
        # ARRANGE
        rows = [
            Row(item="1", qty="1", designator=""),
            Row(item="2", qty="3", designator=""),

        ]
        expected = ValueError.__name__

        for row in rows:
            # ACT
            try:
                cl.assert_designator_required_for_positive_item_and_qty(row)
                result = ""  # unexpected
            except ValueError:
                result = ValueError.__name__

            # ASSERT
            with self.subTest(In={"item": row.item, "qty": row.qty, "designator": row.designator},
                              Out=result, Exp=expected):
                self.assertEqual(result, expected)

    def test_invalid_pass(self):
        """
        Should skip validation (no error) when base fields are invalid.
        """
        # ARRANGE
        rows = [
            Row(item="", qty="1", designator=""),  # invalid (empty) item
            Row(item="0", qty="1", designator=""),  # invalid (zero) item
            Row(item="2.3", qty="1", designator=""),  # invalid (float) item
            Row(item="-1", qty="1", designator=""),  # invalid (negative) item
            Row(item="2", qty="", designator=""),  # invalid (empty) qty
            Row(item="2", qty="0", designator=""),  # invalid (zero) qty
            Row(item="2", qty="2.4", designator=""),  # invalid (float) qty
            Row(item="2", qty="-1", designator=""),  # float (negative) qty
        ]
        expected = ""

        for row in rows:
            # ACT
            try:
                cl.assert_designator_required_for_positive_item_and_qty(row)
                result = ""
            except Exception as e:
                result = type(e).__name__

            # ASSERT
            with self.subTest(In={"item": row.item, "qty": row.qty, "designator": row.designator},
                              Out=result, Exp=expected):
                self.assertEqual(result, expected)


class TestAssertDesignatorCountMatchesQuantity(unittest.TestCase):
    """
    Unit tests for `assert_designator_count_matches_quantity`.

    Rule: When qty ≥ 1.0, the count of comma-separated designators must equal qty.
    """

    def test_valid_silent(self):
        """
        Should succeed silently when designator count equals qty (qty ≥ 1.0).
        """
        # ARRANGE
        rows = [
            Row(qty="1", designator="R1"),
            Row(qty="2", designator="C1,C2"),
            Row(qty="3", designator="U1,U2,U3"),
        ]
        expected = ""

        for row in rows:
            # ACT
            try:
                cl.assert_designator_count_matches_quantity(row)
                result = ""
            except ValueError:
                result = ValueError.__name__

            # ASSERT
            with self.subTest(In={"qty": row.qty, "designator": row.designator}, Out=result,
                              Exp=expected):
                self.assertEqual(result, expected)

    def test_valid_raise(self):
        """
        Should raise ValueError when qty ≥ 1.0 and count(designators) != qty.
        """
        # ARRANGE
        rows = [
            Row(qty="2", designator="R1"),  # 1 != 2
            Row(qty="3", designator="C1,C2"),  # 2 != 3
            Row(qty="1", designator="U1,U2"),  # 2 != 1
        ]
        expected = ValueError.__name__

        for row in rows:
            # ACT
            try:
                cl.assert_designator_count_matches_quantity(row)
                result = ""  # unexpected
            except ValueError:
                result = ValueError.__name__

            # ASSERT
            with self.subTest(In={"qty": row.qty, "designator": row.designator}, Out=result,
                              Exp=expected):
                self.assertEqual(result, expected)

    def test_invalid_pass(self):
        """
        Should skip validation (no error) when qty is invalid.
        """
        # ARRANGE
        rows = [
            Row(qty="-1", designator="R1"),  # invalid qty (negative)
            Row(qty="1.5", designator="R1"),  # invalid float (negative)
            Row(qty="NaN", designator="R1"),  # invalid qty
            Row(qty="abc", designator="R1"),  # invalid qty
        ]
        expected = ""

        for row in rows:
            # ACT
            try:
                cl.assert_designator_count_matches_quantity(row)
                result = ""
            except Exception as e:
                result = type(e).__name__

            # ASSERT
            with self.subTest(In={"qty": row.qty, "designator": row.designator}, Out=result,
                              Exp=expected):
                self.assertEqual(result, expected)


class TestAssertUnitPricePositiveWhenQuantityPositive(unittest.TestCase):
    """
    Unit tests for `assert_unit_price_positive_when_quantity_positive`.

    Rule: If qty > 0.0, unit_price must be > 0.0.
    """

    def test_valid_silent(self):
        """
        Should succeed silently when qty > 0.0 and unit_price > 0.0.
        """
        # ARRANGE
        rows = [
            Row(qty="1", unit_price="0.01"),
            Row(qty="2.5", unit_price="3"),
        ]
        expected = ""

        for row in rows:
            # ACT
            try:
                cl.assert_unit_price_positive_when_quantity_positive(row)
                result = ""
            except ValueError:
                result = ValueError.__name__

            # ASSERT
            with self.subTest(In={"qty": row.qty, "unit_price": row.unit_price}, Out=result,
                              Exp=expected):
                self.assertEqual(result, expected)

    def test_valid_raise(self):
        """
        Should raise ValueError when qty > 0.0 and unit_price <= 0.0 (but still a valid primitive).
        """
        # ARRANGE
        rows = [
            Row(qty="1", unit_price="0"),  # incorrect price (zero)
            Row(qty="2.5", unit_price="0.0"),  # incorrect price (zero)
            Row(qty="1", unit_price="-1"),  # incorrect  price (negative)
            Row(qty="1", unit_price="-0.1"),  # invalid price (negative)
        ]
        expected = ValueError.__name__

        for row in rows:
            # ACT
            try:
                cl.assert_unit_price_positive_when_quantity_positive(row)
                result = ""  # unexpected
            except ValueError:
                result = ValueError.__name__

            # ASSERT
            with self.subTest(In={"qty": row.qty, "unit_price": row.unit_price}, Out=result,
                              Exp=expected):
                self.assertEqual(result, expected)

    def test_invalid_pass(self):
        """
        Should skip validation (no error) when any base field is invalid.
        """
        # ARRANGE
        rows = [
            Row(qty="-1", unit_price="1"),  # invalid qty (negative)
            Row(qty="", unit_price="1"),  # invalid qty (empty)
            Row(qty="0", unit_price="1"),  # invalid qty (zero)
            Row(qty="NaN", unit_price="1"),  # invalid qty (non-float)
            Row(qty="2.5", unit_price=""),  # invalid unit price (empty)
            Row(qty="1", unit_price="abc"),  # invalid price (non-float)
        ]
        expected = ""

        for row in rows:
            # ACT
            try:
                cl.assert_unit_price_positive_when_quantity_positive(row)
                result = ""
            except Exception as e:
                result = type(e).__name__

            # ASSERT
            with self.subTest(In={"qty": row.qty, "unit_price": row.unit_price}, Out=result,
                              Exp=expected):
                self.assertEqual(result, expected)


class TestAssertSubtotalZeroWhenQuantityZero(unittest.TestCase):
    """
    Unit tests for `assert_subtotal_zero_when_quantity_zero`.
    """

    def test_valid_silent(self):
        """
        Should succeed silently when qty == 0.0 and sub_total == 0.0.
        """
        # ARRANGE
        rows = [
            Row(qty="0", sub_total="0"),
            Row(qty="0.0", sub_total="0.0"),
        ]
        expected = ""

        for row in rows:
            # ACT
            try:
                cl.assert_subtotal_zero_when_quantity_zero(row)
                result = ""
            except ValueError:
                result = ValueError.__name__

            # ASSERT
            with self.subTest(In={"qty": row.qty, "sub_total": row.sub_total}, Out=result,
                              Exp=expected):
                self.assertEqual(result, expected)

    def test_valid_raise(self):
        """
        Should raise ValueError when qty == 0.0 and sub_total != 0.0.
        """
        # ARRANGE
        rows = [
            Row(qty="0", sub_total="0.01"),  # incorrect sub total (not zero)
            Row(qty="0.0", sub_total="2"),  # incorrect sub total (not zero)
            Row(qty="0", sub_total="-1"),  # incorrect sub total (not zero)
        ]
        expected = ValueError.__name__

        for row in rows:
            # ACT
            try:
                cl.assert_subtotal_zero_when_quantity_zero(row)
                result = ""  # unexpected
            except ValueError:
                result = ValueError.__name__

            # ASSERT
            with self.subTest(In={"qty": row.qty, "sub_total": row.sub_total}, Out=result,
                              Exp=expected):
                self.assertEqual(result, expected)

    def test_invalid_pass(self):
        """
        Should skip validation (no error) when any base field is invalid.
        """
        # ARRANGE
        rows = [
            Row(qty="-1", sub_total="0"),  # invalid qty
            Row(qty="NaN", sub_total="0"),  # invalid qty
            Row(qty="0", sub_total="oops"),  # invalid sub total
        ]
        expected = ""

        for row in rows:
            # ACT
            try:
                cl.assert_subtotal_zero_when_quantity_zero(row)
                result = ""
            except Exception as e:
                result = type(e).__name__

            # ASSERT
            with self.subTest(In={"qty": row.qty, "sub_total": row.sub_total}, Out=result,
                              Exp=expected):
                self.assertEqual(result, expected)


class TestAssertSubtotalMatchesProduct(unittest.TestCase):
    """
    Unit tests for `assert_subtotal_matches_product`.
    """

    def test_valid_silent(self):
        """
        Should succeed silently when subtotal matches the product (or qty == 0.0).
        """
        # ARRANGE
        rows = [
            Row(qty="2", unit_price="0.25", sub_total="0.50"),
            Row(qty="3.5", unit_price="2", sub_total="7.0"),
            Row(qty="0.001", unit_price="0.002", sub_total="0.000002"),
        ]
        expected = ""

        for row in rows:
            # ACT
            try:
                cl.assert_subtotal_matches_product(row)
                result = ""
            except ValueError:
                result = ValueError.__name__

            # ASSERT
            with self.subTest(
                    In={"qty": row.qty, "unit_price": row.unit_price, "sub_total": row.sub_total},
                    Out=result, Exp=expected):
                self.assertEqual(result, expected)

    def test_valid_raise(self):
        """
        Should raise ValueError when qty != 0.0 and sub_total != qty * unit_price (beyond tolerance).
        """
        # ARRANGE
        rows = [
            Row(qty="2", unit_price="0.25", sub_total="0.55"),  # 0.5 expected
            Row(qty="1.5", unit_price="3.0", sub_total="4.60"),  # 4.5 expected
        ]
        expected = ValueError.__name__

        for row in rows:
            # ACT
            try:
                cl.assert_subtotal_matches_product(row)
                result = ""  # unexpected
            except ValueError:
                result = ValueError.__name__

            # ASSERT
            with self.subTest(
                    In={"qty": row.qty, "unit_price": row.unit_price, "sub_total": row.sub_total},
                    Out=result, Exp=expected):
                self.assertEqual(result, expected)

    def test_invalid_pass(self):
        """
        Should not raise an error when any base field is invalid.
        """
        # ARRANGE
        rows = [
            Row(qty="0", unit_price="1", sub_total="1"),  # invalid qty
            Row(qty="-1", unit_price="2", sub_total="-1"),  # invalid qty
            Row(qty="NaN", unit_price="1", sub_total="0"),  # invalid qty
            Row(qty="2", unit_price="-0.1", sub_total="5"),  # invalid unit_price
            Row(qty="5", unit_price="-5", sub_total="5"),  # invalid unit_price
        ]
        expected = ""

        for row in rows:
            # ACT
            try:
                cl.assert_subtotal_matches_product(row)
                result = ""
            except Exception as e:
                result = type(e).__name__

            # ASSERT
            with self.subTest(
                    In={"qty": row.qty, "unit_price": row.unit_price, "sub_total": row.sub_total},
                    Out=result, Exp=expected):
                self.assertEqual(result, expected)


if __name__ == "__main__":
    unittest.main()
