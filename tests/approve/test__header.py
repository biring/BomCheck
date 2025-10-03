"""
Unit tests for BOM header validators.

This suite verifies that each validator:
    - Accepts valid inputs with no side effects
    - Raises ValueError with centralized, informative messages for invalid inputs
    - Covers regex-driven fields, date formats, and numeric constraints used by parsing/approval flows

Example Usage:
    # Project-root invocation:
    python -m unittest tests/approve/test__header.py

    # Direct discovery (runs all tests):
    python -m unittest discover -s tests

Dependencies:
    - Python >= 3.10
    - Standard Library: unittest, typing
    - External Packages: None

Notes:
    - Validators are treated as pure functions: return None on success, raise ValueError on failure.
    - Fixtures provide representative good/bad values per field to ensure coverage and clear diagnostics.
    - Error text and regex patterns are owned by src.rules._constants; tests validate behavior, not implementation details.

License:
    - Internal Use Only
"""

import unittest

# noinspection PyProtectedMember
from src.approve import _header as approve  # Direct internal import — acceptable in tests
from tests.fixtures import v3_value as vfx


class TestModelNumber(unittest.TestCase):
    """
    Unit test for the `model_number` function.
    """

    def test_valid(self):
        """
        Should NOT raise an exception when input string matches the required model number pattern.
        """
        # ARRANGE
        valid_values = vfx.MODEL_NO_GOOD
        expected = ""  # No error

        for value in valid_values:
            try:
                # ACT
                approve.model_number(value)
                result = ""  # No error
            except ValueError:
                result = ValueError.__name__

            # ASSERT
            with self.subTest(In=value, Out=result, Exp=expected):
                self.assertEqual(result, expected)

    def test_invalid(self):
        """
        Should raise ValueError when input string does NOT match the required model number pattern.
        """
        # ARRANGE
        invalid_values = vfx.MODEL_NO_BAD

        expected = ValueError.__name__

        for value in invalid_values:
            try:
                # ACT
                approve.model_number(value)
                result = ""  # No error
            except ValueError:
                result = ValueError.__name__

            # ASSERT
            with self.subTest(In=value, Out=result, Exp=expected):
                self.assertEqual(result, expected)


class TestBoardName(unittest.TestCase):
    """
    Unit tests for `board_name` function.
    """

    def test_valid(self):
        """
        Should NOT raise an exception when input string matches the required board name pattern.
        """
        # ARRANGE
        valid_values = vfx.BOARD_NAME_GOOD
        expected = ""  # No error

        for value in valid_values:
            try:
                # ACT
                approve.board_name(value)
                result = ""  # No error
            except ValueError:
                result = ValueError.__name__

            # ASSERT
            with self.subTest(In=value, Out=result, Exp=expected):
                self.assertEqual(result, expected)

    def test_invalid(self):
        """
        Should raise ValueError when input string does NOT match the required board name pattern.
        """
        # ARRANGE
        invalid_values = vfx.BOARD_NAME_BAD
        expected = ValueError.__name__

        for value in invalid_values:
            try:
                # ACT
                approve.board_name(value)
                result = ""  # No error
            except ValueError:
                result = ValueError.__name__

            # ASSERT
            with self.subTest(In=value, Out=result, Exp=expected):
                self.assertEqual(result, expected)


class TestBoardSupplier(unittest.TestCase):
    """
    Unit tests for `board supplier` function.
    """

    def test_valid(self):
        """
        Should NOT raise an exception when input string matches the required board supplier name pattern.
        """
        # ARRANGE
        valid_values = vfx.BOARD_SUPPLIER_GOOD
        expected = ""  # No error

        for value in valid_values:
            try:
                # ACT
                approve.board_supplier(value)
                result = ""  # No error
            except ValueError:
                result = ValueError.__name__

            # ASSERT
            with self.subTest(In=value, Out=result, Exp=expected):
                self.assertEqual(result, expected)

    def test_invalid(self):
        """
        Should raise ValueError when input string does NOT match the required board supplier name pattern.
        """
        # ARRANGE
        invalid_values = vfx.BOARD_SUPPLIER_BAD
        expected = ValueError.__name__

        for value in invalid_values:
            try:
                # ACT
                approve.board_supplier(value)
                result = ""  # No error
            except ValueError:
                result = ValueError.__name__

            # ASSERT
            with self.subTest(In=value, Out=result, Exp=expected):
                self.assertEqual(result, expected)


class TestBuildStage(unittest.TestCase):
    """
    Unit tests for `build_stage` function.
    """

    def test_valid(self):
        """
        Should NOT raise an exception when input string matches the required build stage name pattern.
        """
        # ARRANGE
        valid_values = vfx.BUILD_STAGE_GOOD
        expected = ""  # No error

        for value in valid_values:
            try:
                # ACT
                approve.build_stage(value)
                result = ""  # No error
            except ValueError:
                result = ValueError.__name__

            # ASSERT
            with self.subTest(In=value, Out=result, Exp=expected):
                self.assertEqual(result, expected)

    def test_invalid(self):
        """
        Should raise ValueError when input string does NOT match the required build stage name pattern.
        """
        # ARRANGE
        invalid_values = vfx.BUILD_STAGE_BAD
        expected = ValueError.__name__

        for value in invalid_values:
            try:
                # ACT
                approve.build_stage(value)
                result = ""  # No error
            except ValueError:
                result = ValueError.__name__

            # ASSERT
            with self.subTest(In=value, Out=result, Exp=expected):
                self.assertEqual(result, expected)


class TestBomDate(unittest.TestCase):
    """
    Unit tests for `bom_stage` function.
    """

    def test_valid(self):
        """
        Should NOT raise an exception when input string matches the required bom date name pattern.
        """
        # ARRANGE
        valid_values = vfx.BOM_DATE_GOOD
        expected = ""  # No error

        for value in valid_values:
            try:
                # ACT
                approve.bom_date(value)
                result = ""  # No error
            except ValueError:
                result = ValueError.__name__

            # ASSERT
            with self.subTest(In=value, Out=result, Exp=expected):
                self.assertEqual(result, expected)

    def test_invalid(self):
        """
        Should raise ValueError when input string does NOT match the required bom date name pattern.
        """
        # ARRANGE
        invalid_values = vfx.BOM_DATE_BAD
        expected = ValueError.__name__

        for value in invalid_values:
            try:
                # ACT
                approve.bom_date(value)
                result = ""  # No error
            except ValueError:
                result = ValueError.__name__

            # ASSERT
            with self.subTest(In=value, Out=result, Exp=expected):
                self.assertEqual(result, expected)


class TestMaterialCost(unittest.TestCase):
    """
    Unit tests for `material_cost` function.
    """

    def test_valid(self):
        """
        Should NOT raise an exception when input string matches the required material cost pattern.
        """
        # ARRANGE
        valid_values = vfx.COST_GOOD
        expected = ""  # No error

        for value in valid_values:
            try:
                # ACT
                approve.material_cost(value)
                result = ""  # No error
            except ValueError:
                result = ValueError.__name__

            # ASSERT
            with self.subTest(In=value, Out=result, Exp=expected):
                self.assertEqual(result, expected)

    def test_invalid(self):
        """
        Should raise ValueError when input string does NOT match the required material cost pattern.
        """
        # ARRANGE
        invalid_values = vfx.COST_BAD
        expected = ValueError.__name__

        for value in invalid_values:
            try:
                # ACT
                approve.material_cost(value)
                result = ""  # No error
            except ValueError:
                result = ValueError.__name__

            # ASSERT
            with self.subTest(In=value, Out=result, Exp=expected):
                self.assertEqual(result, expected)


class TestOverheadCost(unittest.TestCase):
    """
    Unit tests for `overhead_cost` function.
    """

    def test_valid(self):
        """
        Should NOT raise an exception when input string matches the required overhead cost pattern.
        """
        # ARRANGE
        valid_values = vfx.COST_GOOD
        expected = ""  # No error

        for value in valid_values:
            try:
                # ACT
                approve.overhead_cost(value)
                result = ""  # No error
            except ValueError:
                result = ValueError.__name__

            # ASSERT
            with self.subTest(In=value, Out=result, Exp=expected):
                self.assertEqual(result, expected)

    def test_invalid(self):
        """
        Should raise ValueError when input string does NOT match the required material cost pattern.
        """
        # ARRANGE
        invalid_values = vfx.COST_BAD
        expected = ValueError.__name__

        for value in invalid_values:
            try:
                # ACT
                approve.overhead_cost(value)
                result = ""  # No error
            except ValueError:
                result = ValueError.__name__

            # ASSERT
            with self.subTest(In=value, Out=result, Exp=expected):
                self.assertEqual(result, expected)


class TestTotalCost(unittest.TestCase):
    """
    Unit tests for `total_cost` function.
    """

    def test_valid(self):
        """
        Should NOT raise an exception when input string matches the required total cost pattern.
        """
        # ARRANGE
        valid_values = vfx.COST_GOOD
        expected = ""  # No error

        for value in valid_values:
            try:
                # ACT
                approve.total_cost(value)
                result = ""  # No error
            except ValueError:
                result = ValueError.__name__

            # ASSERT
            with self.subTest(In=value, Out=result, Exp=expected):
                self.assertEqual(result, expected)

    def test_invalid(self):
        """
        Should raise ValueError when input string does NOT match the required material cost pattern.
        """
        # ARRANGE
        invalid_values = vfx.COST_BAD
        expected = ValueError.__name__

        for value in invalid_values:
            try:
                # ACT
                approve.total_cost(value)
                result = ""  # No error
            except ValueError:
                result = ValueError.__name__

            # ASSERT
            with self.subTest(In=value, Out=result, Exp=expected):
                self.assertEqual(result, expected)


if __name__ == "__main__":
    unittest.main()
