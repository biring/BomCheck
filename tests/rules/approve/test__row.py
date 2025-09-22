"""
Unit tests for BOM row validators.

Example Usage:
    # Project-root invocation:
    python -m unittest tests/rules/approve/test__row.py

    # Direct discovery (runs all tests):
    python -m unittest discover -s tests

Dependencies:
    - Python >= 3.10
    - Standard Library: unittest, typing
    - External Packages: None

Notes:
    - Validators are treated as pure functions: return None on success, raise ValueError on failure.
    - Fixtures provide representative good/bad values per field to ensure coverage and clear diagnostics.

License:
    - Internal Use Only
"""

import unittest

# noinspection PyProtectedMember
from src.rules.approve import _row as approve  # Direct internal import — acceptable in tests
from tests.fixtures import row as rfx


class TestItem(unittest.TestCase):
    """
    Unit tests for `item` function.
    """

    def test_valid(self):
        """
        Should NOT raise an exception when input string matches the required item pattern.
        """
        # ARRANGE
        valid_values = rfx.ITEM_GOOD
        expected = ""  # No error

        for value in valid_values.values():
            try:
                # ACT
                approve.item(value)
                result = ""  # No error
            except ValueError:
                result = ValueError.__name__

            # ASSERT
            with self.subTest(In=value, Out=result, Exp=expected):
                self.assertEqual(result, expected)

    def test_invalid(self):
        """
        Should raise ValueError when input string does NOT match the required item pattern.
        """
        # ARRANGE
        invalid_values = rfx.ITEM_BAD
        expected = ValueError.__name__

        for value in invalid_values.values():
            try:
                # ACT
                approve.item(value)
                result = ""  # No error
            except ValueError:
                result = ValueError.__name__

            # ASSERT
            with self.subTest(In=value, Out=result, Exp=expected):
                self.assertEqual(result, expected)


class TestComponentType(unittest.TestCase):
    """
    Unit tests for `component_type` function.
    """

    def test_valid(self):
        """
        Should NOT raise an exception when input string matches the required component_type pattern.
        """
        # ARRANGE
        valid_values = rfx.COMP_TYPE_GOOD
        expected = ""

        for value in valid_values.values():
            try:
                # ACT
                approve.component_type(value)
                result = ""
            except ValueError:
                result = ValueError.__name__

            # ASSERT
            with self.subTest(In=value, Out=result, Exp=expected):
                self.assertEqual(result, expected)

    def test_invalid(self):
        """
        Should raise ValueError when input string does NOT match the required component_type pattern.
        """
        # ARRANGE
        invalid_values = rfx.COMP_TYPE_BAD
        expected = ValueError.__name__

        for value in invalid_values.values():
            try:
                # ACT
                approve.component_type(value)
                result = ""
            except ValueError:
                result = ValueError.__name__

            # ASSERT
            with self.subTest(In=value, Out=result, Exp=expected):
                self.assertEqual(result, expected)


class TestDevicePackage(unittest.TestCase):
    """
    Unit tests for `device_package` function.
    """

    def test_valid(self):
        """
        Should NOT raise an exception when input string matches the required device_package pattern.
        """
        # ARRANGE
        valid_values = rfx.DEVICE_PACKAGE_GOOD
        expected = ""

        for value in valid_values.values():
            try:
                # ACT
                approve.device_package(value)
                result = ""
            except ValueError:
                result = ValueError.__name__

            # ASSERT
            with self.subTest(In=value, Out=result, Exp=expected):
                self.assertEqual(result, expected)

    def test_invalid(self):
        """
        Should raise ValueError when input string does NOT match the required device_package pattern.
        """
        # ARRANGE
        invalid_values = rfx.DEVICE_PACKAGE_BAD
        expected = ValueError.__name__

        for value in invalid_values.values():
            try:
                # ACT
                approve.device_package(value)
                result = ""
            except ValueError:
                result = ValueError.__name__

            # ASSERT
            with self.subTest(In=value, Out=result, Exp=expected):
                self.assertEqual(result, expected)


class TestDescription(unittest.TestCase):
    """
    Unit tests for `description` function.
    """

    def test_valid(self):
        """
        Should NOT raise an exception when input string matches the required description pattern.
        """
        # ARRANGE
        valid_values = rfx.DESCRIPTION_GOOD
        expected = ""

        for value in valid_values.values():
            try:
                # ACT
                approve.description(value)
                result = ""
            except ValueError:
                result = ValueError.__name__

            # ASSERT
            with self.subTest(In=value, Out=result, Exp=expected):
                self.assertEqual(result, expected)

    def test_invalid(self):
        """
        Should raise ValueError when input string does NOT match the required description pattern.
        """
        # ARRANGE
        invalid_values = rfx.DESCRIPTION_BAD
        expected = ValueError.__name__

        for value in invalid_values.values():
            try:
                # ACT
                approve.description(value)
                result = ""
            except ValueError:
                result = ValueError.__name__

            # ASSERT
            with self.subTest(In=value, Out=result, Exp=expected):
                self.assertEqual(result, expected)


class TestUnits(unittest.TestCase):
    """
    Unit tests for `units` function.
    """

    def test_valid(self):
        """
        Should NOT raise an exception when input string matches the required units pattern.
        """
        # ARRANGE
        valid_values = rfx.UNITS_GOOD
        expected = ""

        for value in valid_values.values():
            try:
                # ACT
                approve.units(value)
                result = ""
            except ValueError:
                result = ValueError.__name__
            # ASSERT
            with self.subTest(In=value, Out=result, Exp=expected):
                self.assertEqual(result, expected)

    def test_invalid(self):
        """
        Should raise ValueError when input string does NOT match the required units pattern.
        """
        # ARRANGE
        invalid_values = rfx.UNITS_BAD
        expected = ValueError.__name__

        for value in invalid_values.values():
            try:
                # ACT
                approve.units(value)
                result = ""
            except ValueError:
                result = ValueError.__name__
            # ASSERT
            with self.subTest(In=value, Out=result, Exp=expected):
                self.assertEqual(result, expected)


class TestClassification(unittest.TestCase):
    """
    Unit tests for `classification` function.
    """

    def test_valid(self):
        """
        Should NOT raise an exception when input string matches the required classification pattern.
        """
        # ARRANGE
        valid_values = rfx.CLASSIFICATION_GOOD
        expected = ""

        for value in valid_values.values():
            try:
                # ACT
                approve.classification(value)
                result = ""
            except ValueError:
                result = ValueError.__name__
            # ASSERT
            with self.subTest(In=value, Out=result, Exp=expected):
                self.assertEqual(result, expected)

    def test_invalid(self):
        """
        Should raise ValueError when input string does NOT match the required classification pattern.
        """
        # ARRANGE
        invalid_values = rfx.CLASSIFICATION_BAD
        expected = ValueError.__name__

        for value in invalid_values.values():
            try:
                # ACT
                approve.classification(value)
                result = ""
            except ValueError:
                result = ValueError.__name__
            # ASSERT
            with self.subTest(In=value, Out=result, Exp=expected):
                self.assertEqual(result, expected)


class TestMfgName(unittest.TestCase):
    """
    Unit tests for `mfg_name` function.
    """

    def test_valid(self):
        """
        Should NOT raise an exception when input string matches the required mfg_name pattern.
        """
        # ARRANGE
        valid_values = rfx.MFG_NAME_GOOD
        expected = ""

        for value in valid_values.values():
            try:
                # ACT
                approve.mfg_name(value)
                result = ""
            except ValueError:
                result = ValueError.__name__
            # ASSERT
            with self.subTest(In=value, Out=result, Exp=expected):
                self.assertEqual(result, expected)

    def test_invalid(self):
        """
        Should raise ValueError when input string does NOT match the required mfg_name pattern.
        """
        # ARRANGE
        invalid_values = rfx.MFG_NAME_BAD
        expected = ValueError.__name__

        for value in invalid_values.values():
            try:
                # ACT
                approve.mfg_name(value)
                result = ""
            except ValueError:
                result = ValueError.__name__
            # ASSERT
            with self.subTest(In=value, Out=result, Exp=expected):
                self.assertEqual(result, expected)


class TestMfgPartNo(unittest.TestCase):
    """
    Unit tests for `mfg_part_no` function.
    """

    def test_valid(self):
        """
        Should NOT raise an exception when input string matches the required mfg_part_no pattern.
        """
        # ARRANGE
        valid_values = rfx.MFG_PART_NO_GOOD
        expected = ""

        for value in valid_values.values():
            try:
                # ACT
                approve.mfg_part_no(value)
                result = ""
            except ValueError:
                result = ValueError.__name__
            # ASSERT
            with self.subTest(In=value, Out=result, Exp=expected):
                self.assertEqual(result, expected)

    def test_invalid(self):
        """
        Should raise ValueError when input string does NOT match the required mfg_part_no pattern.
        """
        # ARRANGE
        invalid_values = rfx.MFG_PART_NO_BAD
        expected = ValueError.__name__

        for value in invalid_values.values():
            try:
                # ACT
                approve.mfg_part_no(value)
                result = ""
            except ValueError:
                result = ValueError.__name__
            # ASSERT
            with self.subTest(In=value, Out=result, Exp=expected):
                self.assertEqual(result, expected)


class TestUlVdeNumber(unittest.TestCase):
    """
    Unit tests for `ul_vde_number` function.
    """

    def test_valid(self):
        """
        Should NOT raise an exception when input string matches the required ul_vde_number pattern.
        """
        # ARRANGE
        valid_values = rfx.UL_VDE_NO_GOOD
        expected = ""

        for value in valid_values.values():
            try:
                # ACT
                approve.ul_vde_number(value)
                result = ""
            except ValueError:
                result = ValueError.__name__
            # ASSERT
            with self.subTest(In=value, Out=result, Exp=expected):
                self.assertEqual(result, expected)

    def test_invalid(self):
        """
        Should raise ValueError when input string does NOT match the required ul_vde_number pattern.
        """
        # ARRANGE
        invalid_values = rfx.UL_VDE_NO_BAD
        expected = ValueError.__name__

        for value in invalid_values.values():
            try:
                # ACT
                approve.ul_vde_number(value)
                result = ""
            except ValueError:
                result = ValueError.__name__
            # ASSERT
            with self.subTest(In=value, Out=result, Exp=expected):
                self.assertEqual(result, expected)


class TestValidatedAt(unittest.TestCase):
    """
    Unit tests for `validated_at` function.
    """

    def test_valid(self):
        """
        Should NOT raise an exception when input string matches the required validated_at pattern.
        """
        # ARRANGE
        valid_values = rfx.VALIDATED_AT_GOOD
        expected = ""

        for value in valid_values.values():
            try:
                # ACT
                approve.validated_at(value)
                result = ""
            except ValueError:
                result = ValueError.__name__
            # ASSERT
            with self.subTest(In=value, Out=result, Exp=expected):
                self.assertEqual(result, expected)

    def test_invalid(self):
        """
        Should raise ValueError when input string does NOT match the required validated_at pattern.
        """
        # ARRANGE
        invalid_values = rfx.VALIDATED_AT_BAD
        expected = ValueError.__name__

        for value in invalid_values.values():
            try:
                # ACT
                approve.validated_at(value)
                result = ""
            except ValueError:
                result = ValueError.__name__
            # ASSERT
            with self.subTest(In=value, Out=result, Exp=expected):
                self.assertEqual(result, expected)


class TestQuantity(unittest.TestCase):
    """
    Unit tests for `quantity` function.
    """

    def test_valid(self):
        """
        Should NOT raise an exception when input string matches the required quantity pattern.
        """
        # ARRANGE
        valid_values = rfx.QUANTITY_GOOD
        expected = ""

        for value in valid_values.values():
            try:
                # ACT
                approve.quantity(value)
                result = ""
            except ValueError:
                result = ValueError.__name__

            # ASSERT
            with self.subTest(In=value, Out=result, Exp=expected):
                self.assertEqual(result, expected)

    def test_invalid(self):
        """
        Should raise ValueError when input string does NOT match the required quantity pattern.
        """
        # ARRANGE
        invalid_values = rfx.QUANTITY_BAD
        expected = ValueError.__name__

        for value in invalid_values.values():
            try:
                # ACT
                approve.quantity(value)
                result = ""
            except ValueError:
                result = ValueError.__name__

            # ASSERT
            with self.subTest(In=value, Out=result, Exp=expected):
                self.assertEqual(result, expected)


class TestDesignator(unittest.TestCase):
    """
    Unit tests for `designator` function.
    """

    def test_valid(self):
        """
        Should NOT raise an exception when input string matches the required designator pattern.
        """
        # ARRANGE
        valid_values = rfx.DESIGNATOR_GOOD
        expected = ""

        for value in valid_values.values():
            try:
                # ACT
                approve.designator(value)
                result = ""
            except ValueError:
                result = ValueError.__name__

            # ASSERT
            with self.subTest(In=value, Out=result, Exp=expected):
                self.assertEqual(result, expected)

    def test_invalid(self):
        """
        Should raise ValueError when input string does NOT match the required designator pattern.
        """
        # ARRANGE
        invalid_values = rfx.DESIGNATOR_BAD
        expected = ValueError.__name__

        for value in invalid_values.values():
            try:
                # ACT
                approve.designator(value)
                result = ""
            except ValueError:
                result = ValueError.__name__

            # ASSERT
            with self.subTest(In=value, Out=result, Exp=expected):
                self.assertEqual(result, expected)


class TestUnitPrice(unittest.TestCase):
    """
    Unit tests for `unit_price` function.
    """

    def test_valid(self):
        """
        Should NOT raise an exception when input string matches the required unit_price pattern.
        """
        # ARRANGE
        valid_values = rfx.PRICE_GOOD
        expected = ""

        for value in valid_values.values():
            try:
                # ACT
                approve.unit_price(value)
                result = ""
            except ValueError:
                result = ValueError.__name__

            # ASSERT
            with self.subTest(In=value, Out=result, Exp=expected):
                self.assertEqual(result, expected)

    def test_invalid(self):
        """
        Should raise ValueError when input string does NOT match the required unit_price pattern.
        """
        # ARRANGE
        invalid_values = rfx.PRICE_BAD
        expected = ValueError.__name__

        for value in invalid_values.values():
            try:
                # ACT
                approve.unit_price(value)
                result = ""
            except ValueError:
                result = ValueError.__name__

            # ASSERT
            with self.subTest(In=value, Out=result, Exp=expected):
                self.assertEqual(result, expected)


class TestSubTotal(unittest.TestCase):
    """
    Unit tests for `sub_total` function.
    """

    def test_valid(self):
        """
        Should NOT raise an exception when input string matches the required sub_total pattern.
        """
        # ARRANGE
        valid_values = rfx.PRICE_GOOD
        expected = ""

        for value in valid_values.values():
            try:
                # ACT
                approve.sub_total(value)
                result = ""
            except ValueError:
                result = ValueError.__name__

            # ASSERT
            with self.subTest(In=value, Out=result, Exp=expected):
                self.assertEqual(result, expected)

    def test_invalid(self):
        """
        Should raise ValueError when input string does NOT match the required sub_total pattern.
        """
        # ARRANGE
        invalid_values = rfx.PRICE_BAD
        expected = ValueError.__name__

        for value in invalid_values.values():
            try:
                # ACT
                approve.sub_total(value)
                result = ""
            except ValueError:
                result = ValueError.__name__

            # ASSERT
            with self.subTest(In=value, Out=result, Exp=expected):
                self.assertEqual(result, expected)


if __name__ == "__main__":
    unittest.main()
