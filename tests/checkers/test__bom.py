"""
Unit tests for the Version 3 BOM checker.

Covers row, header, and BOM-level validations, ensuring value checks and cross-field logic integrate correctly.

Example Usage:
    # Preferred usage via project-root invocation:
    python -m unittest tests/checkers/test__bom.py

    # Direct discovery (runs all tests in the tree):
    python -m unittest discover -s tests

Dependencies:
    - Python >= 3.9

Design Notes & Assumptions:
    - Valid BOMs must yield an empty string.
    - Invalid BOMs must yield a non-empty diagnostics string.
    - Tests assert surface behavior only, not internal ErrorLog details.

License:
 - Internal Use Only
"""

import unittest
from dataclasses import replace
from src.models import interfaces as mdl
# noinspection PyProtectedMember
from src.checkers import _bom as bck
# noinspection PyProtectedMember
from src.checkers import _common as cmn
from tests.fixtures import v3_bom as bfx
from tests.fixtures import v3_value as vfx


class TestCheckRowValue(unittest.TestCase):
    """
    Unit tests for `_check_row_value` (cell-level validations only).
    """

    def setUp(self):
        self.errors = cmn.ErrorLog()

        self.errors.set_file_name("test.xlsx")
        self.errors.set_sheet_name("Power PCBA")
        self.errors.set_section_name("Row:3")

    def test_valid_rows(self):
        """
        Should return no errors when all row cell values are valid.
        """
        # ARRANGE
        rows = bfx.BOARD_A.rows
        expected = 0  # No errors

        for row in rows:
            # ACT
            bck._check_row_value(self.errors, row)
            result = len(self.errors)
            # ASSERT
            with self.subTest("Message count", Out=result, Exp=expected):
                self.assertEqual(result, expected)

    def test_invalid_row(self):
        """
        Should return one error per invalid field when a row contains multiple invalid cell values.
        """
        # ARRANGE
        row = replace(
            bfx.ROW_A_1,
            item=vfx.ITEM_BAD[0],
            component_type=vfx.COMP_TYPE_BAD[0],
            device_package=vfx.DEVICE_PACKAGE_BAD[0],
            description=vfx.DESCRIPTION_BAD[0],
            unit=vfx.UNITS_BAD[0],
            classification=vfx.CLASSIFICATION_BAD[0],
            manufacturer=vfx.MFG_NAME_BAD[0],
            mfg_part_number=vfx.MFG_PART_NO_BAD[0],
            ul_vde_number=vfx.UL_VDE_NO_BAD[0],
            validated_at=vfx.VALIDATED_AT_BAD[0],
            qty=vfx.QUANTITY_BAD[0],
            designator=vfx.DESIGNATOR_BAD[0],
            unit_price=vfx.PRICE_BAD[0],
            sub_total=vfx.PRICE_BAD[0],
        )
        expected_file_name = self.errors.file_name
        expected_sheet_name = self.errors.sheet_name
        expected_section_name = self.errors.section_name
        expected_errors = [
            mdl.RowFields.ITEM,
            mdl.RowFields.COMPONENT,
            mdl.RowFields.PACKAGE,
            mdl.RowFields.DESCRIPTION,
            mdl.RowFields.UNITS,
            mdl.RowFields.CLASSIFICATION,
            mdl.RowFields.MANUFACTURER,
            mdl.RowFields.MFG_PART_NO,
            mdl.RowFields.UL_VDE_NUMBER,
            mdl.RowFields.VALIDATED_AT,
            mdl.RowFields.QTY,
            mdl.RowFields.DESIGNATOR,
            mdl.RowFields.UNIT_PRICE,
            mdl.RowFields.SUB_TOTAL,
        ]

        # ACT
        bck._check_row_value(self.errors, row)

        for result, expected in zip(self.errors, expected_errors):
            # ASSERT
            with self.subTest("File Name", Out=result.file_name, Exp=expected_file_name):
                self.assertEqual(result.file_name, expected_file_name)

            with self.subTest("Sheet Name", Out=result.sheet_name, Exp=expected_sheet_name):
                self.assertEqual(result.sheet_name, expected_sheet_name)

            with self.subTest("Section Name", Out=result.section, Exp=expected_section_name):
                self.assertEqual(result.section, expected_section_name)

            with self.subTest("Error Length", Out=len(result.message), Exp="!=0"):
                self.assertNotEqual(len(result.message), 0)

            with self.subTest("Error contains", Out=result.message, Exp=expected):
                self.assertIn(expected, result.message, msg=result.message)


class TestCheckRowLogic(unittest.TestCase):
    """
    Unit tests for `_check_row_logic` (cross-field validations).
    """

    def setUp(self):
        self.errors = cmn.ErrorLog()

        self.errors.set_file_name("test.xlsx")
        self.errors.set_sheet_name("Power PCBA")
        self.errors.set_section_name("Row:3")

    def test_valid_rows(self):
        """
        Should return no errors when all row cross-field relationships are valid.
        """
        # ARRANGE
        rows = bfx.BOARD_A.rows
        expected = 0  # No errors

        for row in rows:
            # ACT
            bck._check_row_logic(self.errors, row)
            result = len(self.errors)
            # ASSERT
            with self.subTest("Message count", Out=result, Exp=expected):
                self.assertEqual(result, expected)

    def test_invalid_rows(self):
        """
        Should return errors when rows violate cross-field rules (e.g., subtotal mismatch, missing designator).
        """
        # ARRANGE
        rows = (
            # quantity is zero when item is blank.
            replace(bfx.ROW_A_1, item="", qty="2"),
            # designator is specified when quantity is an integer more than zero.
            replace(bfx.ROW_A_1, qty="2", designator=""),
            # designator count equals quantity when quantity is a greater than zero integer
            replace(bfx.ROW_A_1, qty="2", designator="R1"),
            # unit price is greater than zero when quantity is greater than zero.
            replace(bfx.ROW_A_1, qty="2", unit_price="0"),
            # sub-total is zero when quantity is zero.
            replace(bfx.ROW_A_1, qty="0", sub_total="1"),
            # sub-total is the product of quantity and unit price.
            replace(bfx.ROW_A_1, qty="2", unit_price="0.1", sub_total="3")
        )
        expected_file_name = self.errors.file_name
        expected_sheet_name = self.errors.sheet_name
        expected_section_name = self.errors.section_name
        expected_errors = [
            mdl.RowFields.QTY,
            mdl.RowFields.DESIGNATOR,
            mdl.RowFields.DESIGNATOR,
            mdl.RowFields.UNIT_PRICE,
            mdl.RowFields.SUB_TOTAL,
            mdl.RowFields.SUB_TOTAL
        ]

        for row, expected in zip(rows, expected_errors):
            self.setUp()  # reset error logs before every check

            # ACT
            bck._check_row_logic(self.errors, row)
            result = self.errors

            # ASSERT
            with self.subTest("File Name", Out=result.file_name, Exp=expected_file_name):
                self.assertEqual(result.file_name, expected_file_name)

            with self.subTest("Sheet Name", Out=result.sheet_name, Exp=expected_sheet_name):
                self.assertEqual(result.sheet_name, expected_sheet_name)

            with self.subTest("Section Name", Out=result.section_name, Exp=expected_section_name):
                self.assertEqual(result.section_name, expected_section_name)

            with self.subTest("Error Length", Out=len(result._errors), Exp="!=0"):
                self.assertNotEqual(len(result._errors), 0)

            messages = "".join(error.message for error in result._errors)
            with self.subTest("Error contains", Out=messages, Exp=expected):
                self.assertIn(expected, messages)


class TestCheckHeaderValue(unittest.TestCase):
    """
    Unit tests for `_check_header_value` (header-level validations).
    """

    def setUp(self):
        self.errors = cmn.ErrorLog()

        self.errors.set_file_name("test.xlsx")
        self.errors.set_sheet_name("UI Main PCBA")
        self.errors.set_section_name("Header")

    def test_valid_header(self):
        """
        Should return no errors when all header fields are valid.
        """
        # ARRANGE
        header = bfx.BOARD_A.header
        expected = 0  # No errors

        # ACT
        bck._check_header_value(self.errors, header)
        result = len(self.errors)
        # ASSERT
        with self.subTest("Message count", Out=result, Exp=expected):
            self.assertEqual(result, expected)

    def test_invalid_header(self):
        """
        Should return one error per invalid header field when cell values are invalid.
        """
        # ARRANGE
        header = replace(
            bfx.HEADER_A,
            model_no=vfx.MODEL_NO_BAD[0],
            board_name=vfx.BOARD_NAME_BAD[0],
            manufacturer=vfx.BOARD_SUPPLIER_BAD[0],
            build_stage=vfx.BUILD_STAGE_BAD[0],
            date=vfx.BOM_DATE_BAD[0],
            material_cost=vfx.COST_BAD[0],
            overhead_cost=vfx.COST_BAD[1],
            total_cost=vfx.COST_BAD[2],
        )
        expected_file_name = self.errors.file_name
        expected_sheet_name = self.errors.sheet_name
        expected_section_name = self.errors.section_name
        expected_errors = (
            mdl.HeaderFields.MODEL_NUMBER,
            mdl.HeaderFields.BOARD_NAME,
            mdl.HeaderFields.BOARD_SUPPLIER,
            mdl.HeaderFields.BUILD_STAGE,
            mdl.HeaderFields.BOM_DATE,
            mdl.HeaderFields.MATERIAL_COST,
            mdl.HeaderFields.OVERHEAD_COST,
            mdl.HeaderFields.TOTAL_COST,
        )

        # ACT
        bck._check_header_value(self.errors, header)

        for result, expected in zip(self.errors, expected_errors):
            # ASSERT
            with self.subTest("File Name", Out=result.file_name, Exp=expected_file_name):
                self.assertEqual(result.file_name, expected_file_name)

            with self.subTest("Sheet Name", Out=result.sheet_name, Exp=expected_sheet_name):
                self.assertEqual(result.sheet_name, expected_sheet_name)

            with self.subTest("Section Name", Out=result.section, Exp=expected_section_name):
                self.assertEqual(result.section, expected_section_name)

            with self.subTest("Error Length", Out=len(result.message), Exp="!=0"):
                self.assertNotEqual(len(result.message), 0)

            with self.subTest("Error contains", Out=result.message, Exp=expected):
                self.assertIn(expected, result.message, msg=result.message)


class TestCheckHeaderLogic(unittest.TestCase):
    """
    Should return no errors when header cross-field relationships are valid.
    """

    def setUp(self):
        self.errors = cmn.ErrorLog()
        self.errors.set_file_name("header_logic_test.xlsx")
        self.errors.set_sheet_name("Motor PCBA")
        self.errors.set_section_name("Header")

    def test_valid(self):
        """
        Should return errors when header violates cross-field cost rules.
        """
        # ARRANGE
        bom = bfx.BOM_B
        expected = 0  # No errors

        for board in bom.boards:
            # ACT
            bck._check_header_logic(self.errors, board.header, board.rows)
            result = len(self.errors)
            # ASSERT
            with self.subTest("Message count", Out=result, Exp=expected):
                self.assertEqual(result, expected)

    def test_invalid(self):
        """
        Should return at least one error when a header violates a cross-field rule.
        """
        # ARRANGE
        bom = replace(
            bfx.BOM_B,
            boards=(
                replace(
                    bfx.BOARD_B1,
                    header=replace(
                        bfx.BOARD_B1.header,
                        material_cost="99.99",
                    ),
                ),
                replace(
                    bfx.BOARD_B2,
                    header=replace(
                        bfx.BOARD_B2.header,
                        total_cost="9.90",
                    ),
                ),
            ),
        )
        expected_file_name = self.errors.file_name
        expected_sheet_name = self.errors.sheet_name
        expected_section_name = self.errors.section_name
        expected_errors = [
            mdl.HeaderFields.MATERIAL_COST,
            mdl.HeaderFields.TOTAL_COST,
        ]

        for board, expected in zip(bom.boards, expected_errors):
            self.setUp()  # reset error logs

            # ACT
            bck._check_header_logic(self.errors, board.header, board.rows)
            result = self.errors

            # ASSERT
            with self.subTest("File Name", Out=result.file_name, Exp=expected_file_name):
                self.assertEqual(result.file_name, expected_file_name)

            with self.subTest("Sheet Name", Out=result.sheet_name, Exp=expected_sheet_name):
                self.assertEqual(result.sheet_name, expected_sheet_name)

            with self.subTest("Section Name", Out=result.section_name, Exp=expected_section_name):
                self.assertEqual(result.section_name, expected_section_name)

            with self.subTest("Error Length", Out=len(result._errors), Exp="!=0"):
                self.assertNotEqual(len(result._errors), 0)

            messages = "".join(error.message for error in result._errors)
            with self.subTest("Error contains", Out=messages, Exp=expected):
                self.assertIn(expected, messages)


class TestCheckBom(unittest.TestCase):
    """
    Unit tests for `check_bom` (BOM-level aggregation).
    """

    def test_valid_bom(self):
        """
        Should return an empty diagnostics string when all boards (headers and rows) are valid.
        """
        # ARRANGE
        bom = bfx.BOM_A
        expected = ""  # No errors => empty diagnostics

        # ACT
        result = bck.check_bom(bom)

        # ASSERT
        # Coarse-grained check only (aggregation correctness)
        with self.subTest("Error contains", Out=result, Exp=expected):
            self.assertEqual(result, expected)

    def test_invalid_bom(self):
        """
        Should return a non-empty diagnostics string when any board has invalid header or row values.
        """
        # ARRANGE
        # Make board material_cost and total_cost inconsistent.
        bom = replace(
            bfx.BOM_A,
            boards=(
                replace(
                    bfx.BOARD_A,
                    header=replace(bfx.BOARD_A.header, material_cost="99.99", total_cost="9.90"),
                ),
            ),
        )
        expected_errors = [
            mdl.HeaderFields.MATERIAL_COST,
            mdl.HeaderFields.TOTAL_COST,
        ]

        # ACT
        result = bck.check_bom(bom)

        # ASSERT
        # Check that the two expected header fields are referenced
        for expected in expected_errors:
            with self.subTest("Error contains", Out=result, Exp=expected):
                self.assertIn(expected, result)


if __name__ == "__main__":
    unittest.main()
