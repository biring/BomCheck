"""
Unit tests for BOM row field coercers.

These tests assert that each coercer:
    - Produces the expected normalized value
    - Emits change-log messages only on effective changes
    - Applies rules in a deterministic order through the shared engine

Example Usage:
    # Run this test module:
    python -m unittest tests/coerce/test_row.py

    # Discover and run all tests:
    python -m unittest discover -s tests

Dependencies:
    - Python >= 3.10
    - Standard Library: unittest, typing
    - External Packages: None

Notes:
    - Tests treat coercers as pure functions returning (value_tuple).
    - Fixtures should cover typical, edge, and no-op inputs to verify logging behavior and stability.

License:
    - Internal Use Only
"""
import unittest
from dataclasses import dataclass
from src.models import interfaces as mdl
from tests.fixtures import v3_value as vfx
# noinspection PyProtectedMember
from src.coerce import _common as common  # Direct internal import — acceptable in tests
# noinspection PyProtectedMember
from src.coerce import _row as row  # Direct internal import — acceptable in tests
# noinspection PyProtectedMember
from src.coerce import _rules as rules  # Direct internal import — acceptable in tests


@dataclass
class CoercionCase:
    """
    Test fixture container for a single coercion scenario.

    Holds the input value, the expected normalized output, and the
    expected log message (if any) produced during coercion. Used by
    shared assertion helpers to verify deterministic behavior.

    Args:
        value_in (str): The raw input value before coercion.
        value_out (str): The expected normalized output value after coercion.
        expected_log (str): The expected log message describing the applied rule.
    """
    value_in: str = ""
    value_out: str = ""
    expected_log: str = ""


class Assert(unittest.TestCase):
    """
    Abstract base class providing common assertions for row coercer tests.
    """

    def assert_change(self, case: CoercionCase, result: common.Result, attr: str):
        """
        Assert that a coercion changed the value and produced exactly one expected log entry.

        Args:
            case (CoercionCase): Input/output fixture holding value_in, value_out, and expected_log.
            result (common.Result): Coercion result to validate.
            attr (str): Expected attribute name associated with the result.

        Returns:
            None: Raises on assertion failure.
        """
        # Single-log invariant: result.logs must contain exactly one entry.
        # We still join to keep the comparer stable if multi-log support returns later.
        log_list = ",".join(log.description for log in result.logs)

        self._assert_common(case=case, result=result, attr=attr)
        with self.subTest("Log Count", Out=len(result.logs), Exp=1):
            self.assertEqual(len(result.logs), 1)
        with self.subTest("Log message", Out=log_list, Exp=case.expected_log):
            self.assertEqual(case.expected_log, log_list)

    def assert_no_change(self, case: CoercionCase, result: common.Result, attr: str):
        """
        Assert that no coercion was applied and no logs were produced.

        Args:
            case (CoercionCase): Input/output fixture holding value_in and value_out.
            result (common.Result): Coercion result to validate.
            attr (str): Expected attribute name associated with the result.

        Returns:
            None: Raises on assertion failure.
        """
        self._assert_common(case=case, result=result, attr=attr)
        with self.subTest("Log Count", Out=len(result.logs), Exp=0):
            self.assertEqual(len(result.logs), 0)

    def _assert_common(self, case: CoercionCase, result: common.Result, attr: str):
        """
        Assert shared invariants for both change and no-change cases.

        Args:
            case (CoercionCase): Input/output fixture with expected values.
            result (common.Result): Coercion result to validate.
            attr (str): Expected attribute name.

        Returns:
            None: Raises on assertion failure.
        """
        with self.subTest("Attribute", Out=result.attr_name, Exp=attr):
            self.assertEqual(result.attr_name, attr)
        with self.subTest("Value In", Out=result.value_in, Exp=case.value_in):
            self.assertEqual(result.value_in, case.value_in)
        with self.subTest("Value Out", Out=result.value_out, Exp=case.value_out):
            self.assertEqual(result.value_out, case.value_out)


class TestItem(Assert):
    """
    Unit tests for `item` function.
    """
    attr = mdl.RowFields.ITEM

    def test_change(self):
        """
        Should apply the rule and record rule log entry.
        """
        # ARRANGE
        cases = [
            CoercionCase(" \t1\n", "1", rules.REMOVE_WHITESPACES.msg),
        ]
        # ACT
        for case in cases:
            result = row.item(case.value_in)
            # ASSERT
            self.assert_change(case=case, result=result, attr=self.attr)

    def test_no_change(self):
        """
        Should return the input text unchanged and an empty log when there is no rule match.
        """
        # ARRANGE
        cases = [
            CoercionCase("", "", ""),
        ]
        for value in vfx.ITEM_GOOD:
            cases.append(CoercionCase(value, value, ""))
        # ACT
        for case in cases:
            result = row.item(case.value_in)
            # ASSERT
            self.assert_no_change(case=case, result=result, attr=self.attr)


class TestComponentType(Assert):
    """
    Unit tests for `component_type` function.
    """
    attr = mdl.RowFields.COMPONENT

    def test_change(self):
        """
        Should apply the rule and record rule log entry.
        """
        # ARRANGE
        cases = [
            CoercionCase("\tSilicon Diode\n", "Silicon Diode", rules.REMOVE_WHITESPACES_EXCEPT_SPACE.msg),
        ]
        # ACT
        for case in cases:
            result = row.component_type(case.value_in)
            # ASSERT
            self.assert_change(case=case, result=result, attr=self.attr)

    def test_no_change(self):
        """
        Should return the input text unchanged and an empty log when there is no rule match.
        """
        # ARRANGE
        cases = [
            CoercionCase("", "", ""),
        ]
        for value in vfx.COMP_TYPE_GOOD:
            cases.append(CoercionCase(value, value, ""))
        # ACT
        for case in cases:
            result = row.component_type(case.value_in)
            # ASSERT
            self.assert_no_change(case=case, result=result, attr=self.attr)


class TestDevicePackage(Assert):
    """
    Unit tests for `device_package` function.
    """
    attr = mdl.RowFields.PACKAGE

    def test_change(self):
        """
        Should apply the rule and record rule log entry.
        """
        # ARRANGE
        cases = [
            CoercionCase("\tSOIC \n8", "SOIC 8", rules.REMOVE_WHITESPACES_EXCEPT_SPACE.msg),
        ]
        # ACT
        for case in cases:
            result = row.device_package(case.value_in)
            # ASSERT
            self.assert_change(case=case, result=result, attr=self.attr)

    def test_no_change(self):
        """
        Should return the input text unchanged and an empty log when there is no rule match.
        """
        # ARRANGE
        cases = [
            CoercionCase("", "", ""),
        ]
        for value in vfx.DEVICE_PACKAGE_GOOD:
            cases.append(CoercionCase(value, value, ""))
        # ACT
        for case in cases:
            result = row.device_package(case.value_in)
            # ASSERT
            self.assert_no_change(case=case, result=result, attr=self.attr)


class TestDescription(Assert):
    """
    Unit tests for `description` function.
    """
    attr = mdl.RowFields.DESCRIPTION

    def test_change(self):
        """
        Should apply the rule and record rule log entry.
        """
        # ARRANGE
        cases = [
            CoercionCase("\nRes, 1k,\t 0603", "Res, 1k, 0603", rules.REMOVE_WHITESPACES_EXCEPT_SPACE.msg),
        ]
        # ACT
        for case in cases:
            result = row.description(case.value_in)
            # ASSERT
            self.assert_change(case=case, result=result, attr=self.attr)

    def test_no_change(self):
        """
        Should return the input text unchanged and an empty log when there is no rule match.
        """
        # ARRANGE
        cases = [
            CoercionCase("", "", ""),
        ]
        for value in vfx.DESCRIPTION_GOOD:
            cases.append(CoercionCase(value, value, ""))
        # ACT
        for case in cases:
            result = row.description(case.value_in)
            # ASSERT
            self.assert_no_change(case=case, result=result, attr=self.attr)


class TestUnits(Assert):
    """
    Unit tests for `units` function.
    """
    attr = mdl.RowFields.UNITS

    def test_change(self):
        """
        Should apply the rule and record rule log entry.
        """
        # ARRANGE
        cases = [
            CoercionCase(" \nPCS\t. ", "PCS.", rules.REMOVE_WHITESPACES.msg),
        ]
        # ACT
        for case in cases:
            result = row.units(case.value_in)
            # ASSERT
            self.assert_change(case=case, result=result, attr=self.attr)

    def test_no_change(self):
        """
        Should return the input text unchanged and an empty log when there is no rule match.
        """
        # ARRANGE
        cases = [
            CoercionCase("", "", ""),
        ]
        for value in vfx.UNITS_GOOD:
            cases.append(CoercionCase(value, value, ""))
        # ACT
        for case in cases:
            result = row.units(case.value_in)
            # ASSERT
            self.assert_no_change(case=case, result=result, attr=self.attr)


class TestClassification(Assert):
    """
    Unit tests for `classification` function.
    """
    attr = mdl.RowFields.CLASSIFICATION

    def test_change(self):
        """
        Should apply the rule and record rule log entry.
        """
        # ARRANGE
        cases = [
            CoercionCase(" \nZ\t ", "Z", rules.REMOVE_WHITESPACES.msg),
        ]
        # ACT
        for case in cases:
            result = row.classification(case.value_in)
            # ASSERT
            self.assert_change(case=case, result=result, attr=self.attr)

    def test_no_change(self):
        """
        Should return the input text unchanged and an empty log when there is no rule match.
        """
        # ARRANGE
        cases = [
            CoercionCase("", "", ""),
        ]
        for value in vfx.CLASSIFICATION_GOOD:
            cases.append(CoercionCase(value, value, ""))
        # ACT
        for case in cases:
            result = row.classification(case.value_in)
            # ASSERT
            self.assert_no_change(case=case, result=result, attr=self.attr)


class TestManufacturer(Assert):
    """
    Unit tests for `manufacturer` function.
    """
    attr = mdl.RowFields.MANUFACTURER

    def test_change(self):
        """
        Should apply the rule and record rule log entry.
        """
        # ARRANGE
        cases = [
            CoercionCase("\nDelta\t Systems Inc.", "Delta Systems Inc.", rules.REMOVE_WHITESPACES_EXCEPT_SPACE.msg),
        ]
        # ACT
        for case in cases:
            result = row.manufacturer(case.value_in)
            # ASSERT
            self.assert_change(case=case, result=result, attr=self.attr)

    def test_no_change(self):
        """
        Should return the input text unchanged and an empty log when there is no rule match.
        """
        # ARRANGE
        cases = [
            CoercionCase("", "", ""),
        ]
        for value in vfx.MFG_NAME_GOOD:
            cases.append(CoercionCase(value, value, ""))
        # ACT
        for case in cases:
            result = row.manufacturer(case.value_in)
            # ASSERT
            self.assert_no_change(case=case, result=result, attr=self.attr)


class TestManufacturerPartNumber(Assert):
    """
    Unit tests for `manufacturer_part_number` function.
    """
    attr = mdl.RowFields.MFG_PART_NO

    def test_change(self):
        """
        Should apply the rule and record rule log entry.
        """
        # ARRANGE
        cases = [
            CoercionCase("\nTCS-34\t ACS", "TCS-34 ACS", rules.REMOVE_WHITESPACES_EXCEPT_SPACE.msg),
        ]
        # ACT
        for case in cases:
            result = row.mfg_part_number(case.value_in)
            # ASSERT
            self.assert_change(case=case, result=result, attr=self.attr)

    def test_no_change(self):
        """
        Should return the input text unchanged and an empty log when there is no rule match.
        """
        # ARRANGE
        cases = [
            CoercionCase("", "", ""),
        ]
        for value in vfx.MFG_PART_NO_GOOD:
            cases.append(CoercionCase(value, value, ""))
        # ACT
        for case in cases:
            result = row.mfg_part_number(case.value_in)
            # ASSERT
            self.assert_no_change(case=case, result=result, attr=self.attr)


class TestUlVdeNumber(Assert):
    """
    Unit tests for `ul_vde_number` function.
    """
    attr = mdl.RowFields.UL_VDE_NUMBER

    def test_change(self):
        """
        Should apply the rule and record rule log entry.
        """
        # ARRANGE
        cases = [
            CoercionCase("\nABC:\t 123", "ABC: 123", rules.REMOVE_WHITESPACES_EXCEPT_SPACE.msg),
        ]
        # ACT
        for case in cases:
            result = row.ul_vde_number(case.value_in)
            # ASSERT
            self.assert_change(case=case, result=result, attr=self.attr)

    def test_no_change(self):
        """
        Should return the input text unchanged and an empty log when there is no rule match.
        """
        # ARRANGE
        cases = [
            CoercionCase("", "", ""),
        ]
        for value in vfx.UL_VDE_NO_GOOD:
            cases.append(CoercionCase(value, value, ""))
        # ACT
        for case in cases:
            result = row.ul_vde_number(case.value_in)
            # ASSERT
            self.assert_no_change(case=case, result=result, attr=self.attr)


class TestValidationAt(Assert):
    """
    Unit tests for `validated_at` function.
    """
    attr = mdl.RowFields.VALIDATED_AT

    def test_change(self):
        """
        Should apply the rule and record rule log entry.
        """
        # ARRANGE
        cases = [
            CoercionCase(" EB1,\nEB2,\tMP ", "EB1,EB2,MP", rules.REMOVE_WHITESPACES.msg),
        ]
        # ACT
        for case in cases:
            result = row.validated_at(case.value_in)
            # ASSERT
            self.assert_change(case=case, result=result, attr=self.attr)

    def test_no_change(self):
        """
        Should return the input text unchanged and an empty log when there is no rule match.
        """
        # ARRANGE
        cases = [
            CoercionCase("", "", ""),
        ]
        for value in vfx.VALIDATED_AT_GOOD:
            cases.append(CoercionCase(value, value, ""))
        # ACT
        for case in cases:
            result = row.validated_at(case.value_in)
            # ASSERT
            self.assert_no_change(case=case, result=result, attr=self.attr)


class TestQuantity(Assert):
    """
    Unit tests for `quantity` function.
    """
    attr = mdl.RowFields.QTY

    def test_change(self):
        """
        Should apply the rule and record rule log entry.
        """
        # ARRANGE
        cases = [
            CoercionCase("\n1 \t", "1", rules.REMOVE_WHITESPACES.msg),
        ]
        # ACT
        for case in cases:
            result = row.quantity(case.value_in)
            # ASSERT
            self.assert_change(case=case, result=result, attr=self.attr)

    def test_no_change(self):
        """
        Should return the input text unchanged and an empty log when there is no rule match.
        """
        # ARRANGE
        cases = [
            CoercionCase("", "", ""),
        ]
        for value in vfx.QUANTITY_GOOD:
            cases.append(CoercionCase(value, value, ""))
        # ACT
        for case in cases:
            result = row.quantity(case.value_in)
            # ASSERT
            self.assert_no_change(case=case, result=result, attr=self.attr)


class TestDesignator(Assert):
    """
    Unit tests for `designator` function.
    """
    attr = mdl.RowFields.DESIGNATOR

    def test_change(self):
        """
        Should apply the rule and record rule log entry.
        """
        # ARRANGE
        cases = [
            CoercionCase("\nR1, \tR2, ", "R1,R2,", rules.REMOVE_WHITESPACES.msg),
        ]
        # ACT
        for case in cases:
            result = row.designator(case.value_in)
            # ASSERT
            self.assert_change(case=case, result=result, attr=self.attr)

    def test_no_change(self):
        """
        Should return the input text unchanged and an empty log when there is no rule match.
        """
        # ARRANGE
        cases = [
            CoercionCase("", "", ""),
        ]
        for value in vfx.DESIGNATOR_GOOD:
            cases.append(CoercionCase(value, value, ""))
        # ACT
        for case in cases:
            result = row.designator(case.value_in)
            # ASSERT
            self.assert_no_change(case=case, result=result, attr=self.attr)


class TestUnitPrice(Assert):
    """
    Unit tests for `unit_price` function.
    """
    attr = mdl.RowFields.UNIT_PRICE

    def test_change(self):
        """
        Should apply the rule and record rule log entry.
        """
        # ARRANGE
        cases = [
            CoercionCase("\n1.24\t ", "1.24", rules.REMOVE_WHITESPACES.msg),
        ]
        # ACT
        for case in cases:
            result = row.unit_price(case.value_in)
            # ASSERT
            self.assert_change(case=case, result=result, attr=self.attr)

    def test_no_change(self):
        """
        Should return the input text unchanged and an empty log when there is no rule match.
        """
        # ARRANGE
        cases = [
            CoercionCase("", "", ""),
        ]
        for value in vfx.PRICE_GOOD:
            cases.append(CoercionCase(value, value, ""))
        # ACT
        for case in cases:
            result = row.unit_price(case.value_in)
            # ASSERT
            self.assert_no_change(case=case, result=result, attr=self.attr)


class TestSubTotal(Assert):
    """
    Unit tests for `sub_total` function.
    """
    attr = mdl.RowFields.SUB_TOTAL

    def test_change(self):
        """
        Should apply the rule and record rule log entry.
        """
        # ARRANGE
        cases = [
            CoercionCase("\n1.24\t ", "1.24", rules.REMOVE_WHITESPACES.msg),
        ]
        # ACT
        for case in cases:
            result = row.sub_total(case.value_in)
            # ASSERT
            self.assert_change(case=case, result=result, attr=self.attr)

    def test_no_change(self):
        """
        Should return the input text unchanged and an empty log when there is no rule match.
        """
        # ARRANGE
        cases = [
            CoercionCase("", "", ""),
        ]
        for value in vfx.PRICE_GOOD:
            cases.append(CoercionCase(value, value, ""))
        # ACT
        for case in cases:
            result = row.sub_total(case.value_in)
            # ASSERT
            self.assert_no_change(case=case, result=result, attr=self.attr)


if __name__ == "__main__":
    unittest.main()
