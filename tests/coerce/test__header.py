"""
Unit tests for BOM header field coercers (model number, board name/supplier, build stage, BOM date, and costs).

These tests assert that each coercer:
    - Produces the expected normalized value
    - Emits change-log messages only on effective changes
    - Applies rules in a deterministic order through the shared engine

Example Usage:
    # Run this test module:
    python -m unittest tests/coerce/test_header.py

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
from src.coerce import _header as header  # Direct internal import — acceptable in tests
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


class TestModelNumber(Assert):
    """
    Unit tests for `model_number` function.
    """
    attr = mdl.HeaderFields.MODEL_NUMBER

    def test_change(self):
        """
        Should apply the rule and record rule log entry.
        """
        # ARRANGE
        cases = [
            CoercionCase("BA400ul", "BA400UL", rules.TO_UPPER.msg),
            CoercionCase(" BA400 UL ", "BA400UL", rules.REMOVE_SPACES_ONLY.msg),
        ]
        # ACT
        for case in cases:
            result = header.model_number(case.value_in)
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
        for model_number in vfx.MODEL_NO_GOOD:
            cases.append(CoercionCase(model_number, model_number, ""))
        # ACT
        for case in cases:
            result = header.model_number(case.value_in)
            # ASSERT
            self.assert_no_change(case=case, result=result, attr=self.attr)


class TestBoardName(Assert):
    """
    Unit tests for `board_name` function.
    """
    attr = mdl.HeaderFields.BOARD_NAME

    def test_change(self):
        """
        Should apply the rule and record rule log entry.
        """
        # ARRANGE
        cases = [
            CoercionCase("Power  PCBA", "Power PCBA", rules.COLLAPSE_MULTIPLE_SPACES.msg),
            CoercionCase(" Power PCBA ", "Power PCBA", rules.STRIP_EDGE_SPACES.msg),
        ]
        # ACT
        for case in cases:
            result = header.board_name(case.value_in)
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
        for board_name in vfx.BOARD_NAME_GOOD:
            cases.append(CoercionCase(board_name, board_name, ""))
        # ACT
        for case in cases:
            result = header.board_name(case.value_in)
            # ASSERT
            self.assert_no_change(case=case, result=result, attr=self.attr)


class TestBoardSupplier(Assert):
    """
    Unit tests for `board_supplier` function.
    """
    attr = mdl.HeaderFields.BOARD_SUPPLIER

    def test_change(self):
        """
        Should apply the rule and record rule log entry.
        """
        # ARRANGE
        cases = [
            CoercionCase("General  Electric", "General Electric", rules.COLLAPSE_MULTIPLE_SPACES.msg),
            CoercionCase(" General Electric ", "General Electric", rules.STRIP_EDGE_SPACES.msg),
        ]
        # ACT
        for case in cases:
            result = header.board_supplier(case.value_in)
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
        for board_supplier in vfx.BOARD_SUPPLIER_GOOD:
            cases.append(CoercionCase(board_supplier, board_supplier, ""))
        # ACT
        for case in cases:
            result = header.board_supplier(case.value_in)
            # ASSERT
            self.assert_no_change(case=case, result=result, attr=self.attr)


class TestBuildStage(Assert):
    """
    Unit tests for `build_stage` function.
    """
    attr = mdl.HeaderFields.BUILD_STAGE

    def test_change(self):
        """
        Should apply the rule and record rule log entry.
        """
        # ARRANGE
        cases = [
            CoercionCase("EB 1", "EB1", rules.REMOVE_SPACES_ONLY.msg),
        ]
        # ACT
        for case in cases:
            result = header.build_stage(case.value_in)
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
        for build_stage in vfx.BUILD_STAGE_GOOD:
            cases.append(CoercionCase(build_stage, build_stage, ""))
        # ACT
        for case in cases:
            result = header.build_stage(case.value_in)
            # ASSERT
            self.assert_no_change(case=case, result=result, attr=self.attr)


class TestBomDate(Assert):
    """
    Unit tests for `bom_date` function.
    """
    attr = mdl.HeaderFields.BOM_DATE

    def test_change(self):
        """
        Should apply the rule and record rule log entry.
        """
        # ARRANGE
        cases = [
            CoercionCase("\t1/1/2025\n", "1/1/2025", rules.REMOVE_WHITESPACES_EXCEPT_SPACE.msg),
        ]
        # ACT
        for case in cases:
            result = header.bom_date(case.value_in)
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
        for bom_date in vfx.BOM_DATE_GOOD:
            cases.append(CoercionCase(bom_date, bom_date, ""))
        # ACT
        for case in cases:
            result = header.bom_date(case.value_in)
            # ASSERT
            self.assert_no_change(case=case, result=result, attr=self.attr)


class TestMaterialCost(Assert):
    """
    Unit tests for `material_cost` function.
    """
    attr = mdl.HeaderFields.MATERIAL_COST

    def test_change(self):
        """
        Should apply the rule and record rule log entry.
        """
        # ARRANGE
        cases = [
            CoercionCase(" 1.25 ", "1.25", rules.REMOVE_SPACES_ONLY.msg),
        ]
        # ACT
        for case in cases:
            result = header.material_cost(case.value_in)
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
        for cost in vfx.COST_GOOD:
            cases.append(CoercionCase(cost, cost, ""))
        # ACT
        for case in cases:
            result = header.material_cost(case.value_in)
            # ASSERT
            self.assert_no_change(case=case, result=result, attr=self.attr)


class TestOverheadCost(Assert):
    """
    Unit tests for `overhead_cost` function.
    """
    attr = mdl.HeaderFields.OVERHEAD_COST

    def test_change(self):
        """
        Should apply the rule and record rule log entry.
        """
        # ARRANGE
        cases = [
            CoercionCase(" 1.25 ", "1.25", rules.REMOVE_SPACES_ONLY.msg),
        ]
        # ACT
        for case in cases:
            result = header.overhead_cost(case.value_in)
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
        for cost in vfx.COST_GOOD:
            cases.append(CoercionCase(cost, cost, ""))
        # ACT
        for case in cases:
            result = header.overhead_cost(case.value_in)
            # ASSERT
            self.assert_no_change(case=case, result=result, attr=self.attr)


class TestTotalCost(Assert):
    """
    Unit tests for `overhead_cost` function.
    """
    attr = mdl.HeaderFields.TOTAL_COST

    def test_change(self):
        """
        Should apply the rule and record rule log entry.
        """
        # ARRANGE
        cases = [
            CoercionCase(" 1.25 ", "1.25", rules.REMOVE_SPACES_ONLY.msg),
        ]
        # ACT
        for case in cases:
            result = header.total_cost(case.value_in)
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
        for cost in vfx.COST_GOOD:
            cases.append(CoercionCase(cost, cost, ""))
        # ACT
        for case in cases:
            result = header.total_cost(case.value_in)
            # ASSERT
            self.assert_no_change(case=case, result=result, attr=self.attr)


if __name__ == "__main__":
    unittest.main()
