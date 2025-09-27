"""
Unit tests for BOM row reviewers.

This module validates that each reviewer in `src.review._row`:
 - Returns "" for valid inputs
 - Returns a descriptive message containing the field name for invalid inputs

Example Usage:
    # Preferred usage via project-root invocation:
    python -m unittest tests/review/test__row.py

    # Direct discovery (runs all tests, including this module):
    python -m unittest discover -s tests

Dependencies:
    - Python >= 3.10
    - Standard Library: unittest
    - External Packages: None

Notes:
    - Reviewers are pure functions: success -> "", failure -> descriptive error text.
    - Fixtures provide representative good/bad values for comprehensive coverage.
    - Tests validate reviewer behavior, not internal validator implementation.

License:
    - Internal Use Only
"""

import unittest

from src.models import interfaces as models
# noinspection PyProtectedMember
from src.review import _row as review  # Direct internal import — acceptable in tests
from tests.fixtures import row as row_fx


class TestItem(unittest.TestCase):
    """
    Unit tests for the `item` reviewer.
    """

    def test_valid(self):
        """
        Should return empty string for valid item values.
        """
        # ARRANGE
        valid_values = list(row_fx.ITEM_GOOD.values())
        expected = ""

        for value in valid_values:
            # ACT
            result = review.item(value)

            # ASSERT
            with self.subTest(In=value, Out=result, Exp=expected):
                self.assertEqual(result, expected)

    def test_invalid(self):
        """
        Should return a non-empty message containing the field name for invalid item values.
        """
        # ARRANGE
        invalid_values = list(row_fx.ITEM_BAD.values())
        expected = models.RowFields.ITEM
        expected_size = len(expected)

        for value in invalid_values:
            # ACT
            result = review.item(value)
            result_size = len(result)

            # ASSERT
            with self.subTest("Contains", Exp=expected):
                self.assertIn(expected, result)
            with self.subTest("Size greater than", Exp=expected_size):
                self.assertLess(expected_size, result_size)


class TestComponentType(unittest.TestCase):
    """
    Unit tests for the `component_type` reviewer.
    """

    def test_valid(self):
        """
        Should return empty string for valid component type values.
        """
        # ARRANGE
        valid_values = list(row_fx.COMP_TYPE_GOOD.values())
        expected = ""

        for value in valid_values:
            # ACT
            result = review.component_type(value)

            # ASSERT
            with self.subTest(In=value, Out=result, Exp=expected):
                self.assertEqual(result, expected)

    def test_invalid(self):
        """
        Should return a non-empty message containing the field name for invalid component type values.
        """
        # ARRANGE
        invalid_values = list(row_fx.COMP_TYPE_BAD.values())
        expected = models.RowFields.COMPONENT
        expected_size = len(expected)

        for value in invalid_values:
            # ACT
            result = review.component_type(value)
            result_size = len(result)

            # ASSERT
            with self.subTest("Contains", Exp=expected):
                self.assertIn(expected, result)
            with self.subTest("Size greater than", Exp=expected_size):
                self.assertLess(expected_size, result_size)


class TestDevicePackage(unittest.TestCase):
    """
    Unit tests for the `device_package` reviewer.
    """

    def test_valid(self):
        """
        Should return empty string for valid device package values.
        """
        # ARRANGE
        valid_values = list(row_fx.DEVICE_PACKAGE_GOOD.values())
        expected = ""

        for value in valid_values:
            # ACT
            result = review.device_package(value)

            # ASSERT
            with self.subTest(In=value, Out=result, Exp=expected):
                self.assertEqual(result, expected)

    def test_invalid(self):
        """
        Should return a non-empty message containing the field name for invalid device package values.
        """
        # ARRANGE
        invalid_values = list(row_fx.DEVICE_PACKAGE_BAD.values())
        expected = models.RowFields.PACKAGE
        expected_size = len(expected)

        for value in invalid_values:
            # ACT
            result = review.device_package(value)
            result_size = len(result)

            # ASSERT
            with self.subTest("Contains", Exp=expected):
                self.assertIn(expected, result)
            with self.subTest("Size greater than", Exp=expected_size):
                self.assertLess(expected_size, result_size)


class TestDescription(unittest.TestCase):
    """
    Unit tests for the `description` reviewer.
    """

    def test_valid(self):
        """
        Should return empty string for valid description values.
        """
        # ARRANGE
        valid_values = list(row_fx.DESCRIPTION_GOOD.values())
        expected = ""

        for value in valid_values:
            # ACT
            result = review.description(value)

            # ASSERT
            with self.subTest(In=value, Out=result, Exp=expected):
                self.assertEqual(result, expected)

    def test_invalid(self):
        """
        Should return a non-empty message containing the field name for invalid description values.
        """
        # ARRANGE
        invalid_values = list(row_fx.DESCRIPTION_BAD.values())
        expected = models.RowFields.DESCRIPTION
        expected_size = len(expected)

        for value in invalid_values:
            # ACT
            result = review.description(value)
            result_size = len(result)

            # ASSERT
            with self.subTest("Contains", Exp=expected):
                self.assertIn(expected, result)
            with self.subTest("Size greater than", Exp=expected_size):
                self.assertLess(expected_size, result_size)


class TestUnits(unittest.TestCase):
    """
    Unit tests for the `units` reviewer.
    """

    def test_valid(self):
        """
        Should return empty string for valid units values.
        """
        # ARRANGE
        valid_values = list(row_fx.UNITS_GOOD.values())
        expected = ""

        for value in valid_values:
            # ACT
            result = review.units(value)

            # ASSERT
            with self.subTest(In=value, Out=result, Exp=expected):
                self.assertEqual(result, expected)

    def test_invalid(self):
        """
        Should return a non-empty message containing the field name for invalid units values.
        """
        # ARRANGE
        invalid_values = list(row_fx.UNITS_BAD.values())
        expected = models.RowFields.UNITS
        expected_size = len(expected)

        for value in invalid_values:
            # ACT
            result = review.units(value)
            result_size = len(result)

            # ASSERT
            with self.subTest("Contains", Exp=expected):
                self.assertIn(expected, result)
            with self.subTest("Size greater than", Exp=expected_size):
                self.assertLess(expected_size, result_size)


class TestClassification(unittest.TestCase):
    """
    Unit tests for the `classification` reviewer.
    """

    def test_valid(self):
        """
        Should return empty string for valid classification values.
        """
        # ARRANGE
        valid_values = list(row_fx.CLASSIFICATION_GOOD.values())
        expected = ""

        for value in valid_values:
            # ACT
            result = review.classification(value)

            # ASSERT
            with self.subTest(In=value, Out=result, Exp=expected):
                self.assertEqual(result, expected)

    def test_invalid(self):
        """
        Should return a non-empty message containing the field name for invalid classification values.
        """
        # ARRANGE
        invalid_values = list(row_fx.CLASSIFICATION_BAD.values())
        expected = models.RowFields.CLASSIFICATION
        expected_size = len(expected)

        for value in invalid_values:
            # ACT
            result = review.classification(value)
            result_size = len(result)

            # ASSERT
            with self.subTest("Contains", Exp=expected):
                self.assertIn(expected, result)
            with self.subTest("Size greater than", Exp=expected_size):
                self.assertLess(expected_size, result_size)


class TestManufacturerName(unittest.TestCase):
    """
    Unit tests for the `mfg_name` reviewer.
    """

    def test_valid(self):
        """
        Should return empty string for valid manufacturer names.
        """
        # ARRANGE
        valid_values = list(row_fx.MFG_NAME_GOOD.values())
        expected = ""

        for value in valid_values:
            # ACT
            result = review.mfg_name(value)

            # ASSERT
            with self.subTest(In=value, Out=result, Exp=expected):
                self.assertEqual(result, expected)

    def test_invalid(self):
        """
        Should return a non-empty message containing the field name for invalid manufacturer names.
        """
        # ARRANGE
        invalid_values = list(row_fx.MFG_NAME_BAD.values())
        expected = models.RowFields.MANUFACTURER
        expected_size = len(expected)

        for value in invalid_values:
            # ACT
            result = review.mfg_name(value)
            result_size = len(result)

            # ASSERT
            with self.subTest("Contains", Exp=expected):
                self.assertIn(expected, result)
            with self.subTest("Size greater than", Exp=expected_size):
                self.assertLess(expected_size, result_size)


class TestMfgPartNumber(unittest.TestCase):
    """
    Unit tests for the `mfg_part_no` reviewer.
    """

    def test_valid(self):
        """
        Should return empty string for valid manufacturer part numbers.
        """
        # ARRANGE
        valid_values = list(row_fx.MFG_PART_NO_GOOD.values())
        expected = ""

        for value in valid_values:
            # ACT
            result = review.mfg_part_no(value)

            # ASSERT
            with self.subTest(In=value, Out=result, Exp=expected):
                self.assertEqual(result, expected)

    def test_invalid(self):
        """
        Should return a non-empty message containing the field name for invalid manufacturer part numbers.
        """
        # ARRANGE
        invalid_values = list(row_fx.MFG_PART_NO_BAD.values())
        expected = models.RowFields.MFG_PART_NO
        expected_size = len(expected)

        for value in invalid_values:
            # ACT
            result = review.mfg_part_no(value)
            result_size = len(result)

            # ASSERT
            with self.subTest("Contains", Exp=expected):
                self.assertIn(expected, result)
            with self.subTest("Size greater than", Exp=expected_size):
                self.assertLess(expected_size, result_size)


class TestUlVdeNumber(unittest.TestCase):
    """
    Unit tests for the `ul_vde_number` reviewer.
    """

    def test_valid(self):
        """
        Should return empty string for valid UL/VDE numbers.
        """
        # ARRANGE
        valid_values = list(row_fx.UL_VDE_NO_GOOD.values())
        expected = ""

        for value in valid_values:
            # ACT
            result = review.ul_vde_number(value)

            # ASSERT
            with self.subTest(In=value, Out=result, Exp=expected):
                self.assertEqual(result, expected)

    def test_invalid(self):
        """
        Should return a non-empty message containing the field name for invalid UL/VDE numbers.
        """
        # ARRANGE
        invalid_values = list(row_fx.UL_VDE_NO_BAD.values())
        expected = models.RowFields.UL_VDE_NUMBER
        expected_size = len(expected)

        for value in invalid_values:
            # ACT
            result = review.ul_vde_number(value)
            result_size = len(result)

            # ASSERT
            with self.subTest("Contains", Exp=expected):
                self.assertIn(expected, result)
            with self.subTest("Size greater than", Exp=expected_size):
                self.assertLess(expected_size, result_size)


class TestValidatedAt(unittest.TestCase):
    """
    Unit tests for the `validated_at` reviewer.
    """

    def test_valid(self):
        """
        Should return empty string for valid validated-at tokens.
        """
        # ARRANGE
        valid_values = list(row_fx.VALIDATED_AT_GOOD.values())
        expected = ""

        for value in valid_values:
            # ACT
            result = review.validated_at(value)

            # ASSERT
            with self.subTest(In=value, Out=result, Exp=expected):
                self.assertEqual(result, expected)

    def test_invalid(self):
        """
        Should return a non-empty message containing the field name for invalid validated-at tokens.
        """
        # ARRANGE
        invalid_values = list(row_fx.VALIDATED_AT_BAD.values())
        expected = models.RowFields.VALIDATED_AT
        expected_size = len(expected)

        for value in invalid_values:
            # ACT
            result = review.validated_at(value)
            result_size = len(result)

            # ASSERT
            with self.subTest("Contains", Exp=expected):
                self.assertIn(expected, result)
            with self.subTest("Size greater than", Exp=expected_size):
                self.assertLess(expected_size, result_size)


class TestQuantity(unittest.TestCase):
    """
    Unit tests for the `quantity` reviewer.
    """

    def test_valid(self):
        """
        Should return empty string for valid quantity values.
        """
        # ARRANGE
        valid_values = list(row_fx.QUANTITY_GOOD.values())
        expected = ""

        for value in valid_values:
            # ACT
            result = review.quantity(value)

            # ASSERT
            with self.subTest(In=value, Out=result, Exp=expected):
                self.assertEqual(result, expected)

    def test_invalid(self):
        """
        Should return a non-empty message containing the field name for invalid quantity values.
        """
        # ARRANGE
        invalid_values = list(row_fx.QUANTITY_BAD.values())
        expected = models.RowFields.QTY
        expected_size = len(expected)

        for value in invalid_values:
            # ACT
            result = review.quantity(value)
            result_size = len(result)

            # ASSERT
            with self.subTest("Contains", Exp=expected):
                self.assertIn(expected, result)
            with self.subTest("Size greater than", Exp=expected_size):
                self.assertLess(expected_size, result_size)


class TestDesignator(unittest.TestCase):
    """
    Unit tests for the `designator` reviewer.
    """

    def test_valid(self):
        """Should return empty string for valid designator values."""
        # ARRANGE
        valid_values = list(row_fx.DESIGNATOR_GOOD.values())
        expected = ""

        for value in valid_values:
            # ACT
            result = review.designator(value)

            # ASSERT
            with self.subTest(In=value, Out=result, Exp=expected):
                self.assertEqual(result, expected)

    def test_invalid(self):
        """
        Should return a non-empty message containing the field name for invalid designator values.
        """
        # ARRANGE
        invalid_values = list(row_fx.DESIGNATOR_BAD.values())
        expected = models.RowFields.DESIGNATOR
        expected_size = len(expected)

        for value in invalid_values:
            # ACT
            result = review.designator(value)
            result_size = len(result)

            # ASSERT
            with self.subTest("Contains", Exp=expected):
                self.assertIn(expected, result)
            with self.subTest("Size greater than", Exp=expected_size):
                self.assertLess(expected_size, result_size)


class TestUnitPrice(unittest.TestCase):
    """
    Unit tests for the `unit_price` reviewer.
    """

    def test_valid(self):
        """
        Should return empty string for valid unit price values.
        """
        # ARRANGE
        valid_values = list(row_fx.PRICE_GOOD.values())
        expected = ""

        for value in valid_values:
            # ACT
            result = review.unit_price(value)

            # ASSERT
            with self.subTest(In=value, Out=result, Exp=expected):
                self.assertEqual(result, expected)

    def test_invalid(self):
        """
        Should return a non-empty message containing the field name for invalid unit price values.
        """
        # ARRANGE
        invalid_values = list(row_fx.PRICE_BAD.values())
        expected = models.RowFields.UNIT_PRICE
        expected_size = len(expected)

        for value in invalid_values:
            # ACT
            result = review.unit_price(value)
            result_size = len(result)

            # ASSERT
            with self.subTest("Contains", Exp=expected):
                self.assertIn(expected, result)
            with self.subTest("Size greater than", Exp=expected_size):
                self.assertLess(expected_size, result_size)


class TestSubTotal(unittest.TestCase):
    """
    Unit tests for the `sub_total` reviewer.
    """

    def test_valid(self):
        """
        Should return empty string for valid sub-total values.
        """
        # ARRANGE
        valid_values = list(row_fx.PRICE_GOOD.values())
        expected = ""

        for value in valid_values:
            # ACT
            result = review.sub_total(value)

            # ASSERT
            with self.subTest(In=value, Out=result, Exp=expected):
                self.assertEqual(result, expected)

    def test_invalid(self):
        """
        Should return a non-empty message containing the field name for invalid sub-total values.
        """
        # ARRANGE
        invalid_values = list(row_fx.PRICE_BAD.values())
        expected = models.RowFields.SUB_TOTAL
        expected_size = len(expected)

        for value in invalid_values:
            # ACT
            result = review.sub_total(value)
            result_size = len(result)

            # ASSERT
            with self.subTest("Contains", Exp=expected):
                self.assertIn(expected, result)
            with self.subTest("Size greater than", Exp=expected_size):
                self.assertLess(expected_size, result_size)


if __name__ == "__main__":
    unittest.main()
