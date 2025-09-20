"""
Unit tests for BOM header reviewers.

This module validates that each reviewer in `src.rules.review.header`:
 - Returns "" for valid inputs
 - Returns a descriptive message containing the field name for invalid inputs
 - Covers regex-driven fields (model number, board name, build stage), dates, and numeric costs

Example Usage:
    # Preferred usage via project-root invocation:
    python -m unittest tests/rules/review/test__header.py

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
from src.rules.review import _header as review  # Direct internal import — acceptable in tests
from tests.fixtures import rows as row_fixture


class TestModelNumber(unittest.TestCase):
    """
    Unit tests for the `model_number` reviewer.
    """

    def test_valid(self):
        """
        Should return "" for valid model numbers.
        """
        # ARRANGE
        valid_values = [
            row_fixture.MODEL_NO_GOOD_1,
            row_fixture.MODEL_NO_GOOD_2,
            row_fixture.MODEL_NO_GOOD_3,
            row_fixture.MODEL_NO_GOOD_4,
            row_fixture.MODEL_NO_GOOD_5,
            row_fixture.MODEL_NO_GOOD_6,
        ]
        expected = ""  # No message

        for value in valid_values:
            # ACT
            result = review.model_number(value)

            # ASSERT
            with self.subTest(In=value, Out=result, Exp=expected):
                self.assertEqual(result, expected)

    def test_invalid(self):
        """
        Should return a non-empty message containing the field name for invalid model numbers.
        """
        # ARRANGE
        invalid_values = [
            row_fixture.MODEL_NO_BAD_1,
            row_fixture.MODEL_NO_BAD_2,
            row_fixture.MODEL_NO_BAD_3,
            row_fixture.MODEL_NO_BAD_4,
            row_fixture.MODEL_NO_BAD_5,
            row_fixture.MODEL_NO_BAD_6,
            row_fixture.MODEL_NO_BAD_7,
            row_fixture.MODEL_NO_BAD_8,
            row_fixture.MODEL_NO_BAD_9,
            row_fixture.MODEL_NO_BAD_10,
            row_fixture.MODEL_NO_BAD_11,
            row_fixture.MODEL_NO_BAD_12,
        ]
        expected = models.HeaderFields.MODEL_NUMBER
        expected_size = len(expected)

        for value in invalid_values:
            # ACT
            result = review.model_number(value)
            result_size = len(result)

            # ASSERT
            with self.subTest("Contains", Exp=expected):
                self.assertTrue(expected in result)
            with self.subTest("Size greater than", Exp=expected_size):
                self.assertLess(expected_size, result_size)


class TestBoardName(unittest.TestCase):
    """
    Unit tests for the `board_name` reviewer.
    """

    def test_valid(self):
        """
        Should return "" for valid board names.
        """
        # ARRANGE
        valid_values = [
            row_fixture.BOARD_NAME_GOOD_1,
            row_fixture.BOARD_NAME_GOOD_2,
            row_fixture.BOARD_NAME_GOOD_3,
            row_fixture.BOARD_NAME_GOOD_4,
            row_fixture.BOARD_NAME_GOOD_5,
        ]
        expected = ""  # No message

        for value in valid_values:
            # ACT
            result = review.board_name(value)

            # ASSERT
            with self.subTest(In=value, Out=result, Exp=expected):
                self.assertEqual(result, expected)

    def test_invalid(self):
        """
        Should return a non-empty message containing the field name for invalid board names.
        """
        # ARRANGE
        invalid_values = [
            row_fixture.BOARD_NAME_BAD_1,
            row_fixture.BOARD_NAME_BAD_2,
            row_fixture.BOARD_NAME_BAD_3,
            row_fixture.BOARD_NAME_BAD_4,
            row_fixture.BOARD_NAME_BAD_5,
            row_fixture.BOARD_NAME_BAD_6,
            row_fixture.BOARD_NAME_BAD_7,
            row_fixture.BOARD_NAME_BAD_8,
            row_fixture.BOARD_NAME_BAD_9,
        ]
        expected = models.HeaderFields.BOARD_NAME
        expected_size = len(expected)

        for value in invalid_values:
            # ACT
            result = review.board_name(value)
            result_size = len(result)

            # ASSERT
            with self.subTest("Contains", Exp=expected):
                self.assertTrue(expected in result)
            with self.subTest("Size greater than", Exp=expected_size):
                self.assertLess(expected_size, result_size)


class TestBoardSupplier(unittest.TestCase):
    """
    Unit tests for the `board_supplier` reviewer.
    """

    def test_valid(self):
        """
        Should return "" for valid board supplier names.
        """
        # ARRANGE
        valid_values = [
            row_fixture.BOARD_SUPPLIER_GOOD_1,
            row_fixture.BOARD_SUPPLIER_GOOD_2,
            row_fixture.BOARD_SUPPLIER_GOOD_3,
            row_fixture.BOARD_SUPPLIER_GOOD_4,
            row_fixture.BOARD_SUPPLIER_GOOD_5,
            row_fixture.BOARD_SUPPLIER_GOOD_6,
            row_fixture.BOARD_SUPPLIER_GOOD_7,
            row_fixture.BOARD_SUPPLIER_GOOD_8,
        ]
        expected = ""  # No message

        for value in valid_values:
            # ACT
            result = review.board_supplier(value)

            # ASSERT
            with self.subTest(In=value, Out=result, Exp=expected):
                self.assertEqual(result, expected)

    def test_invalid(self):
        """
        Should return a non-empty message containing the field name for invalid board supplier names.
        """
        # ARRANGE
        invalid_values = [
            row_fixture.BOARD_SUPPLIER_BAD_1,
            row_fixture.BOARD_SUPPLIER_BAD_2,
            row_fixture.BOARD_SUPPLIER_BAD_3,
            row_fixture.BOARD_SUPPLIER_BAD_4,
            row_fixture.BOARD_SUPPLIER_BAD_5,
            row_fixture.BOARD_SUPPLIER_BAD_6,
            row_fixture.BOARD_SUPPLIER_BAD_7,
            row_fixture.BOARD_SUPPLIER_BAD_8,
            row_fixture.BOARD_SUPPLIER_BAD_9,
            row_fixture.BOARD_SUPPLIER_BAD_10,

        ]
        expected = models.HeaderFields.BOARD_SUPPLIER
        expected_size = len(expected)

        for value in invalid_values:
            # ACT
            result = review.board_supplier(value)
            result_size = len(result)

            # ASSERT
            with self.subTest("Contains", Exp=expected):
                self.assertTrue(expected in result)
            with self.subTest("Size greater than", Exp=expected_size):
                self.assertLess(expected_size, result_size)


class TestBuildStage(unittest.TestCase):
    """
    Unit tests for the `build_stage` reviewer.
    """

    def test_valid(self):
        """
        Should return "" for valid build stages.
        """
        # ARRANGE
        valid_values = [
            row_fixture.BUILD_STAGE_GOOD_1,
            row_fixture.BUILD_STAGE_GOOD_2,
            row_fixture.BUILD_STAGE_GOOD_3,
            row_fixture.BUILD_STAGE_GOOD_4,
            row_fixture.BUILD_STAGE_GOOD_5,
            row_fixture.BUILD_STAGE_GOOD_6,
            row_fixture.BUILD_STAGE_GOOD_7,
            row_fixture.BUILD_STAGE_GOOD_8,
            row_fixture.BUILD_STAGE_GOOD_9,
            row_fixture.BUILD_STAGE_GOOD_10,
        ]
        expected = ""  # No message

        for value in valid_values:
            # ACT
            result = review.build_stage(value)

            # ASSERT
            with self.subTest(In=value, Out=result, Exp=expected):
                self.assertEqual(result, expected)

    def test_invalid(self):
        """
        Should return a non-empty message containing the field name for invalid build stages.
        """
        # ARRANGE
        invalid_values = [
            row_fixture.BUILD_STAGE_BAD_1,
            row_fixture.BUILD_STAGE_BAD_2,
            row_fixture.BUILD_STAGE_BAD_3,
            row_fixture.BUILD_STAGE_BAD_4,
            row_fixture.BUILD_STAGE_BAD_5,
            row_fixture.BUILD_STAGE_BAD_6,
            row_fixture.BUILD_STAGE_BAD_7,
            row_fixture.BUILD_STAGE_BAD_8,
            row_fixture.BUILD_STAGE_BAD_9,
            row_fixture.BUILD_STAGE_BAD_10,
            row_fixture.BUILD_STAGE_BAD_11,
            row_fixture.BUILD_STAGE_BAD_12,
        ]
        expected = models.HeaderFields.BUILD_STAGE
        expected_size = len(expected)

        for value in invalid_values:
            # ACT
            result = review.build_stage(value)
            result_size = len(result)

            # ASSERT
            with self.subTest("Contains", Exp=expected):
                self.assertTrue(expected in result)
            with self.subTest("Size greater than", Exp=expected_size):
                self.assertLess(expected_size, result_size)


class TestBomDate(unittest.TestCase):
    """
    Unit tests for the `bom_date` reviewer.
    """

    def test_valid(self):
        """
        Should return "" for valid BOM dates.
        """
        # ARRANGE
        valid_values = [
            row_fixture.GOOD_BOM_DATE_1,
            row_fixture.GOOD_BOM_DATE_2,
            row_fixture.GOOD_BOM_DATE_3,
            row_fixture.GOOD_BOM_DATE_4,
            row_fixture.GOOD_BOM_DATE_5,
            row_fixture.GOOD_BOM_DATE_6,
            row_fixture.GOOD_BOM_DATE_7,
            row_fixture.GOOD_BOM_DATE_8,
        ]
        expected = ""  # No message

        for value in valid_values:
            # ACT
            result = review.bom_date(value)

            # ASSERT
            with self.subTest(In=value, Out=result, Exp=expected):
                self.assertEqual(result, expected)

    def test_invalid(self):
        """
        Should return a non-empty message containing the field name for invalid BOM dates.
        """
        # ARRANGE
        invalid_values = [
            row_fixture.BAD_BOM_DATE_1,
            row_fixture.BAD_BOM_DATE_2,
            row_fixture.BAD_BOM_DATE_3,
            row_fixture.BAD_BOM_DATE_4,
            row_fixture.BAD_BOM_DATE_5,
            row_fixture.BAD_BOM_DATE_6,
            row_fixture.BAD_BOM_DATE_7,
            row_fixture.BAD_BOM_DATE_8,
            row_fixture.BAD_BOM_DATE_9,
        ]
        expected = models.HeaderFields.BOM_DATE
        expected_size = len(expected)

        for value in invalid_values:
            # ACT
            result = review.bom_date(value)
            result_size = len(result)

            # ASSERT
            with self.subTest("Contains", Exp=expected):
                self.assertTrue(expected in result)
            with self.subTest("Size greater than", Exp=expected_size):
                self.assertLess(expected_size, result_size)


class TestMaterialCost(unittest.TestCase):
    """
    Unit tests for the `material_cost` reviewer.
    """

    def test_valid(self):
        """
        Should return "" for valid material costs.
        """
        # ARRANGE
        valid_values = [
            row_fixture.GOOD_COST_1,
            row_fixture.GOOD_COST_2,
            row_fixture.GOOD_COST_3,
            row_fixture.GOOD_COST_4,
            row_fixture.GOOD_COST_5,
            row_fixture.GOOD_COST_6,
            row_fixture.GOOD_COST_7,
            row_fixture.GOOD_COST_8,
        ]
        expected = ""  # No message

        for value in valid_values:
            # ACT
            result = review.material_cost(value)

            # ASSERT
            with self.subTest(In=value, Out=result, Exp=expected):
                self.assertEqual(result, expected)

    def test_invalid(self):
        """
        Should return a non-empty message containing the field name for invalid material costs.
        """
        # ARRANGE
        invalid_values = [
            row_fixture.BAD_COST_1,
            row_fixture.BAD_COST_2,
            row_fixture.BAD_COST_3,
            row_fixture.BAD_COST_4,
            row_fixture.BAD_COST_5,
            row_fixture.BAD_COST_6,
            row_fixture.BAD_COST_7,
            row_fixture.BAD_COST_8,
        ]
        expected = models.HeaderFields.MATERIAL_COST
        expected_size = len(expected)

        for value in invalid_values:
            # ACT
            result = review.material_cost(value)
            result_size = len(result)

            # ASSERT
            with self.subTest("Contains", Exp=expected):
                self.assertTrue(expected in result)
            with self.subTest("Size greater than", Exp=expected_size):
                self.assertLess(expected_size, result_size)


class TestOverheadCost(unittest.TestCase):
    """
    Unit tests for the `overhead_cost` reviewer.
    """

    def test_valid(self):
        """
        Should return "" for valid overhead costs.
        """
        # ARRANGE
        valid_values = [
            row_fixture.GOOD_COST_1,
            row_fixture.GOOD_COST_2,
            row_fixture.GOOD_COST_3,
            row_fixture.GOOD_COST_4,
            row_fixture.GOOD_COST_5,
            row_fixture.GOOD_COST_6,
            row_fixture.GOOD_COST_7,
            row_fixture.GOOD_COST_8,
        ]
        expected = ""  # No message

        for value in valid_values:
            # ACT
            result = review.overhead_cost(value)

            # ASSERT
            with self.subTest(In=value, Out=result, Exp=expected):
                self.assertEqual(result, expected)

    def test_invalid(self):
        """
        Should return a non-empty message containing the field name for invalid overhead costs.
        """
        # ARRANGE
        invalid_values = [
            row_fixture.BAD_COST_1,
            row_fixture.BAD_COST_2,
            row_fixture.BAD_COST_3,
            row_fixture.BAD_COST_4,
            row_fixture.BAD_COST_5,
            row_fixture.BAD_COST_6,
            row_fixture.BAD_COST_7,
            row_fixture.BAD_COST_8,
        ]
        expected = models.HeaderFields.OVERHEAD_COST
        expected_size = len(expected)

        for value in invalid_values:
            # ACT
            result = review.overhead_cost(value)
            result_size = len(result)

            # ASSERT
            with self.subTest("Contains", Exp=expected):
                self.assertTrue(expected in result)
            with self.subTest("Size greater than", Exp=expected_size):
                self.assertLess(expected_size, result_size)


class TestTotalCost(unittest.TestCase):
    """
    Unit tests for the `total_cost` reviewer.
    """

    def test_valid(self):
        """
        Should return "" for valid total costs.
        """
        # ARRANGE
        valid_values = [
            row_fixture.GOOD_COST_1,
            row_fixture.GOOD_COST_2,
            row_fixture.GOOD_COST_3,
            row_fixture.GOOD_COST_4,
            row_fixture.GOOD_COST_5,
            row_fixture.GOOD_COST_6,
            row_fixture.GOOD_COST_7,
            row_fixture.GOOD_COST_8,
        ]
        expected = ""  # No message

        for value in valid_values:
            # ACT
            result = review.total_cost(value)

            # ASSERT
            with self.subTest(In=value, Out=result, Exp=expected):
                self.assertEqual(result, expected)

    def test_invalid(self):
        """
        Should return a non-empty message containing the field name for invalid total costs.
        """
        # ARRANGE
        invalid_values = [
            row_fixture.BAD_COST_1,
            row_fixture.BAD_COST_2,
            row_fixture.BAD_COST_3,
            row_fixture.BAD_COST_4,
            row_fixture.BAD_COST_5,
            row_fixture.BAD_COST_6,
            row_fixture.BAD_COST_7,
            row_fixture.BAD_COST_8,
        ]
        expected = models.HeaderFields.TOTAL_COST
        expected_size = len(expected)

        for value in invalid_values:
            # ACT
            result = review.total_cost(value)
            result_size = len(result)

            # ASSERT
            with self.subTest("Contains", Exp=expected):
                self.assertTrue(expected in result)
            with self.subTest("Size greater than", Exp=expected_size):
                self.assertLess(expected_size, result_size)


if __name__ == "__main__":
    unittest.main()
