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
from tests.fixtures import v3_value as vfx
# noinspection PyProtectedMember
from src.coerce import _header as header  # Direct internal import — acceptable in tests
# noinspection PyProtectedMember
from src.coerce import _rules as rules  # Direct internal import — acceptable in tests


@dataclass
class Cases:
    value_in: str = ""
    value_out: str = ""
    expected_log: str = ""


class TestModelNumber(unittest.TestCase):
    """
    Unit tests for `model_number` function.
    """

    def test_change(self):
        """
        Should apply the rule and record rule log entry.
        """
        # ARRANGE
        cases = [
            Cases("BA400ul", "BA400UL", rules.TO_UPPER.msg),
            Cases(" BA400 UL ", "BA400UL", rules.REMOVE_ASCII_SPACES.msg),
        ]

        for case in cases:
            # ACT
            result = header.model_number(case.value_in)
            log_list = ",".join([log.description for log in result.logs])

            # ASSERT
            with self.subTest("Value Out", In=case.value_in, Out=result.value_out, Exp=case.value_out):
                self.assertEqual(result.value_out, case.value_out)
            with self.subTest("Log Content", Out=log_list, Exp=case.expected_log):
                self.assertEqual(case.expected_log, log_list)

    def test_no_change(self):
        """
        Should return the input text unchanged and an empty log when there is no rule match.
        """
        # ARRANGE
        cases = [
            Cases("", "", ""),
        ]
        for model_number in vfx.MODEL_NO_GOOD:
            cases.append(Cases(model_number, model_number, ""))

        for case in cases:
            # ACT
            result = header.model_number(case.value_in)

            # ASSERT
            with self.subTest("Value Out", In=case.value_in, Out=result.value_out, Exp=case.value_out):
                self.assertEqual(result.value_out, case.value_out)
            with self.subTest("Log Count", Out=len(result.logs), Exp=0):
                self.assertEqual(len(result.logs), 0)


class TestBoardName(unittest.TestCase):
    """
    Unit tests for `board_name` function.
    """

    def test_change(self):
        """
        Should apply the rule and record rule log entry.
        """
        # ARRANGE
        cases = [
            Cases("Power  PCBA", "Power PCBA", rules.COLLAPSE_MULTIPLE_SPACES.msg),
            Cases(" Power PCBA ", "Power PCBA", rules.STRIP_EDGE_SPACES.msg),
        ]

        for case in cases:
            # ACT
            result = header.board_name(case.value_in)
            log_list = ",".join([log.description for log in result.logs])

            # ASSERT
            with self.subTest("Value Out", In=case.value_in, Out=result.value_out, Exp=case.value_out):
                self.assertEqual(result.value_out, case.value_out)
            with self.subTest("Log Content", Out=log_list, Exp=case.expected_log):
                self.assertEqual(case.expected_log, log_list)

    def test_no_change(self):
        """
        Should return the input text unchanged and an empty log when there is no rule match.
        """
        # ARRANGE
        cases = [
            Cases("", "", ""),
        ]
        for board_name in vfx.BOARD_NAME_GOOD:
            cases.append(Cases(board_name, board_name, ""))

        for case in cases:
            # ACT
            result = header.board_name(case.value_in)

            # ASSERT
            with self.subTest("Value Out", In=case.value_in, Out=result.value_out, Exp=case.value_out):
                self.assertEqual(result.value_out, case.value_out)
            with self.subTest("Log Count", Out=len(result.logs), Exp=0):
                self.assertEqual(len(result.logs), 0)


class TestBoardSupplier(unittest.TestCase):
    """
    Unit tests for `board_supplier` function.
    """

    def test_change(self):
        """
        Should apply the rule and record rule log entry.
        """
        # ARRANGE
        cases = [
            Cases("General  Electric", "General Electric", rules.COLLAPSE_MULTIPLE_SPACES.msg),
            Cases(" General Electric ", "General Electric", rules.STRIP_EDGE_SPACES.msg),
        ]

        for case in cases:
            # ACT
            result = header.board_supplier(case.value_in)
            log_list = ",".join([log.description for log in result.logs])

            # ASSERT
            with self.subTest("Value Out", In=case.value_in, Out=result.value_out, Exp=case.value_out):
                self.assertEqual(result.value_out, case.value_out)
            with self.subTest("Log Content", Out=log_list, Exp=case.expected_log):
                self.assertEqual(case.expected_log, log_list)

    def test_no_change(self):
        """
        Should return the input text unchanged and an empty log when there is no rule match.
        """
        # ARRANGE
        cases = [
            Cases("", "", ""),
        ]
        for board_supplier in vfx.BOARD_SUPPLIER_GOOD:
            cases.append(Cases(board_supplier, board_supplier, ""))

        for case in cases:
            # ACT
            result = header.board_supplier(case.value_in)

            # ASSERT
            with self.subTest("Value Out", In=case.value_in, Out=result.value_out, Exp=case.value_out):
                self.assertEqual(result.value_out, case.value_out)
            with self.subTest("Log Count", Out=len(result.logs), Exp=0):
                self.assertEqual(len(result.logs), 0)


class TestBuildStage(unittest.TestCase):
    """
    Unit tests for `build_stage` function.
    """

    def test_change(self):
        """
        Should apply the rule and record rule log entry.
        """
        # ARRANGE
        cases = [
            Cases("EB 1", "EB1", rules.REMOVE_ASCII_SPACES.msg),
        ]

        for case in cases:
            # ACT
            result = header.build_stage(case.value_in)
            log_list = ",".join([log.description for log in result.logs])

            # ASSERT
            with self.subTest("Value Out", In=case.value_in, Out=result.value_out, Exp=case.value_out):
                self.assertEqual(result.value_out, case.value_out)
            with self.subTest("Log Content", Out=log_list, Exp=case.expected_log):
                self.assertEqual(case.expected_log, log_list)

    def test_no_change(self):
        """
        Should return the input text unchanged and an empty log when there is no rule match.
        """
        # ARRANGE
        cases = [
            Cases("", "", ""),
        ]
        for build_stage in vfx.BUILD_STAGE_GOOD:
            cases.append(Cases(build_stage, build_stage, ""))

        for case in cases:
            # ACT
            result = header.build_stage(case.value_in)

            # ASSERT
            with self.subTest("Value Out", In=case.value_in, Out=result.value_out, Exp=case.value_out):
                self.assertEqual(result.value_out, case.value_out)
            with self.subTest("Log Count", Out=len(result.logs), Exp=0):
                self.assertEqual(len(result.logs), 0)


class TestBomDate(unittest.TestCase):
    """
    Unit tests for `bom_date` function.
    """

    def test_change(self):
        """
        Should apply the rule and record rule log entry.
        """
        # ARRANGE
        cases = [
        ]

        for case in cases:
            # ACT
            result = header.bom_date(case.value_in)
            log_list = ",".join([log.description for log in result.logs])

            # ASSERT
            with self.subTest("Value Out", In=case.value_in, Out=result.value_out, Exp=case.value_out):
                self.assertEqual(result.value_out, case.value_out)
            with self.subTest("Log Content", Out=log_list, Exp=case.expected_log):
                self.assertEqual(case.expected_log, log_list)

    def test_no_change(self):
        """
        Should return the input text unchanged and an empty log when there is no rule match.
        """
        # ARRANGE
        cases = [
            Cases("", "", ""),
        ]
        for bom_date in vfx.BOM_DATE_GOOD:
            cases.append(Cases(bom_date, bom_date, ""))

        for case in cases:
            # ACT
            result = header.bom_date(case.value_in)

            # ASSERT
            with self.subTest("Value Out", In=case.value_in, Out=result.value_out, Exp=case.value_out):
                self.assertEqual(result.value_out, case.value_out)
            with self.subTest("Log Count", Out=len(result.logs), Exp=0):
                self.assertEqual(len(result.logs), 0)


class TestMaterialCost(unittest.TestCase):
    """
    Unit tests for `material_cost` function.
    """

    def test_change(self):
        """
        Should apply the rule and record rule log entry.
        """
        # ARRANGE
        cases = [
            Cases(" 1.25 ", "1.25", rules.REMOVE_ASCII_SPACES.msg),
        ]

        for case in cases:
            # ACT
            result = header.material_cost(case.value_in)
            log_list = ",".join([log.description for log in result.logs])

            # ASSERT
            with self.subTest("Value Out", In=case.value_in, Out=result.value_out, Exp=case.value_out):
                self.assertEqual(result.value_out, case.value_out)
            with self.subTest("Log Content", Out=log_list, Exp=case.expected_log):
                self.assertEqual(case.expected_log, log_list)

    def test_no_change(self):
        """
        Should return the input text unchanged and an empty log when there is no rule match.
        """
        # ARRANGE
        cases = [
            Cases("", "", ""),
        ]
        for cost in vfx.COST_GOOD:
            cases.append(Cases(cost, cost, ""))

        for case in cases:
            # ACT
            result = header.material_cost(case.value_in)

            # ASSERT
            with self.subTest("Value Out", In=case.value_in, Out=result.value_out, Exp=case.value_out):
                self.assertEqual(result.value_out, case.value_out)
            with self.subTest("Log Count", Out=len(result.logs), Exp=0):
                self.assertEqual(len(result.logs), 0)


class TestOverheadCost(unittest.TestCase):
    """
    Unit tests for `overhead_cost` function.
    """

    def test_change(self):
        """
        Should apply the rule and record rule log entry.
        """
        # ARRANGE
        cases = [
            Cases(" 1.25 ", "1.25", rules.REMOVE_ASCII_SPACES.msg),
        ]

        for case in cases:
            # ACT
            result = header.overhead_cost(case.value_in)
            log_list = ",".join([log.description for log in result.logs])

            # ASSERT
            with self.subTest("Value Out", In=case.value_in, Out=result.value_out, Exp=case.value_out):
                self.assertEqual(result.value_out, case.value_out)
            with self.subTest("Log Content", Out=log_list, Exp=case.expected_log):
                self.assertEqual(case.expected_log, log_list)

    def test_no_change(self):
        """
        Should return the input text unchanged and an empty log when there is no rule match.
        """
        # ARRANGE
        cases = [
            Cases("", "", ""),
        ]
        for cost in vfx.COST_GOOD:
            cases.append(Cases(cost, cost, ""))

        for case in cases:
            # ACT
            result = header.overhead_cost(case.value_in)

            # ASSERT
            with self.subTest("Value Out", In=case.value_in, Out=result.value_out, Exp=case.value_out):
                self.assertEqual(result.value_out, case.value_out)
            with self.subTest("Log Count", Out=len(result.logs), Exp=0):
                self.assertEqual(len(result.logs), 0)


class TestTotalCost(unittest.TestCase):
    """
    Unit tests for `overhead_cost` function.
    """

    def test_change(self):
        """
        Should apply the rule and record rule log entry.
        """
        # ARRANGE
        cases = [
            Cases(" 1.25 ", "1.25", rules.REMOVE_ASCII_SPACES.msg),
        ]

        for case in cases:
            # ACT
            result = header.total_cost(case.value_in)
            log_list = ",".join([log.description for log in result.logs])

            # ASSERT
            with self.subTest("Value Out", In=case.value_in, Out=result.value_out, Exp=case.value_out):
                self.assertEqual(result.value_out, case.value_out)
            with self.subTest("Log Content", Out=log_list, Exp=case.expected_log):
                self.assertEqual(case.expected_log, log_list)

    def test_no_change(self):
        """
        Should return the input text unchanged and an empty log when there is no rule match.
        """
        # ARRANGE
        cases = [
            Cases("", "", ""),
        ]
        for cost in vfx.COST_GOOD:
            cases.append(Cases(cost, cost, ""))

        for case in cases:
            # ACT
            result = header.total_cost(case.value_in)

            # ASSERT
            with self.subTest("Value Out", In=case.value_in, Out=result.value_out, Exp=case.value_out):
                self.assertEqual(result.value_out, case.value_out)
            with self.subTest("Log Count", Out=len(result.logs), Exp=0):
                self.assertEqual(len(result.logs), 0)


if __name__ == "__main__":
    unittest.main()
