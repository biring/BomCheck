"""
Unit tests for the Version 3 BOM checker.

This suite validates header, row, board, and BOM-level checks, ensuring both cell-level value assertions and cross-field logic validations integrate correctly.

Example Usage (from project root):
    # Run test suite:
    python -m unittest tests.checkers.test__v3_bom

Dependencies:
    - Python >= 3.9
    - Standard Library: unittest, dataclasses
    - Internal:
        - src.checkers._v3_bom
        - src.models.interfaces (Bom, Board, Header, Row)
        - tests._fixtures (provides valid/invalid sample objects)

Design Notes & Assumptions:
    - Uses `replace` from `dataclasses` to mutate fixture rows/headers for invalid cases.
    - Expected error fields and sections are asserted in order where deterministic.
    - `ErrorMsg.render` output is indirectly verified via `check_v3_bom` string results.
    - Unit tests balance between targeted validator coverage and integration-style aggregation.

License:
 - Internal Use Only
"""

import unittest
from dataclasses import replace

from src.models.interfaces import Bom, Board, Header, HeaderFields, RowFields

# noinspection PyProtectedMember
from src.checkers._v3_bom import (
    _check_boards,
    _check_header,
    _check_row_cell_logic,
    _check_row_cell_value,
    _check_rows,
    _check_bom,
    check_v3_bom,
)

from ._fixtures import (
    _HEADER,
    _ROW_ONE,
    _ROW_ONE_ALT,
    _ROW_TWO,
    _BOARD_TWO,
    _BOARD_ONE,
    _BOM
)


class TestCheckRowCellValue(unittest.TestCase):
    """
    Unit tests for `_check_row_cell_value` (cell-level validations only).
    """

    def test_valid_rows(self):
        """
        Should return an empty error list for rows with valid cell values.
        """
        # ARRANGE
        rows = [_ROW_ONE, _ROW_ONE_ALT, _ROW_TWO]
        expected_error_message = ["", "", ""]  # No errors

        for row, expected in zip(rows, expected_error_message):
            # ACT
            errors = _check_row_cell_value("", "", "", row)
            # ASSERT
            with self.subTest("Message Length", Out=len(errors), Exp=0):
                self.assertEqual(len(errors), 0)

    def test_invalid_row(self):
        """
        Should return one error per invalid field when a row contains multiple invalid cell values.

        The fields intentionally set invalid here are chosen to map 1:1 with expected error fields,
        ensuring we verify only the function's documented, cell-level validation behavior.
        """
        # ARRANGE
        row = replace(
            _ROW_ONE,
            item="-5",  # invalid item
            description="",  # invalid description
            classification="Z",  # invalid classification
            manufacturer="",  # invalid manufacturer
            mfg_part_number="",  # invalid part number
            qty="-1",  # invalid qty
            unit_price="-0.5",  # invalid unit price
            sub_total="bad",  # invalid sub total
        )
        file_name = "file.xlsx"
        sheet_name = "Sheet1"
        line = "2"

        expected_errors = [
            RowFields.ITEM,
            RowFields.DESCRIPTION,
            RowFields.CLASSIFICATION,
            RowFields.MANUFACTURER,
            RowFields.MFG_PART_NO,
            RowFields.QTY,
            RowFields.UNIT_PRICE,
            RowFields.SUB_TOTAL,
        ]

        # ACT
        results = _check_row_cell_logic(file_name, sheet_name, line, row)

        for result, expected in zip(results, expected_errors):
            # ASSERT
            with self.subTest("File Name", Out=result.file_name, Exp=file_name):
                self.assertEqual(result.file_name, file_name)

            with self.subTest("Sheet Name", Out=result.sheet_name, Exp=sheet_name):
                self.assertEqual(result.sheet_name, sheet_name)

            with self.subTest("Section", Out=result.location, Exp=line):
                self.assertEqual(result.location, line)

            with self.subTest("Field", Out=result.field_name, Exp=expected):
                self.assertEqual(result.field_name, expected)

            with self.subTest("Error Length", Out=len(result.message), Exp="!=0"):
                self.assertNotEqual(len(result.message), 0)


class TestCheckRowCellLogic(unittest.TestCase):
    """
    Unit tests for `_check_row_cell_logic` (cross-field validations).
    """

    def test_valid_rows(self):
        """
        Should return an empty error list for rows with valid cross-field relationships.
        """
        # ARRANGE
        rows = [_ROW_ONE, _ROW_ONE_ALT, _ROW_TWO]

        for row in rows:
            # ACT
            errors = _check_row_cell_logic("file.xlsx", "Sheet1", "1", row)

            # ASSERT
            with self.subTest("Message Length", Out=len(errors), Exp=0):
                self.assertEqual(len(errors), 0)

    def test_invalid_rows(self):
        """
        Should return at least one error when a row violates a cross-field rule.
        """
        # ARRANGE
        rows = [
            replace(_ROW_ONE, item=""),  # Qty should be zero
            replace(_ROW_ONE, qty="0", sub_total="0"),  # Qty should be more than zero
            replace(_ROW_ONE, designator="R1"),  # Two designators required
            replace(_ROW_ONE, designator=""),  # Designator required
            replace(_ROW_ONE, unit_price="0"),  # Unit price required
            replace(_ROW_ONE, item="", qty="0"),  # For qty zero, sub-total should be zero
            replace(_ROW_ONE, sub_total="3")  # Sub-total should be qty x unit price
        ]
        file_name = "file.xlsx"
        sheet_name = "Sheet1"
        line = "2"
        expected_error_fields = [
            RowFields.QTY,
            RowFields.QTY,
            RowFields.DESIGNATOR,
            RowFields.DESIGNATOR,
            RowFields.UNIT_PRICE,
            RowFields.SUB_TOTAL,
            RowFields.SUB_TOTAL
        ]

        for row, expected in zip(rows, expected_error_fields):
            # ACT
            results = _check_row_cell_logic(file_name, sheet_name, line, row)

            for result in results:
                # ASSERT
                with self.subTest("File Name", Out=result.file_name, Exp=file_name):
                    self.assertEqual(result.file_name, file_name)

                with self.subTest("Sheet Name", Out=result.sheet_name, Exp=sheet_name):
                    self.assertEqual(result.sheet_name, sheet_name)

                with self.subTest("Section", Out=result.location, Exp=line):
                    self.assertEqual(result.location, line)

                with self.subTest("Field", Out=result.field_name, Exp=expected):
                    self.assertEqual(result.field_name, expected)

                with self.subTest("Error Length", Out=len(result.message), Exp="!=0"):
                    self.assertNotEqual(len(result.message), 0)


class TestCheckHeader(unittest.TestCase):
    """
    Unit tests for `_check_header` (header-level validations).
    """

    def test_valid_header(self):
        """
        Should return an empty list when header values are valid.
        """
        # ARRANGE
        header = _HEADER

        # ACT
        result = _check_header("", "", header)
        # ASSERT
        with self.subTest("Message Length", Out=len(result), Exp=0):
            self.assertEqual(len(result), 0)

    def test_invalid_header(self):
        """
        Should return a list of error(s) when header cell validation fails.
        """
        # ARRANGE
        header = Header(
            model_no="ACE-2000",  # invalid
            board_name="Power Board",  # invalid (doesn't end in uppercase PCBA pattern)
            manufacturer="",  # invalid (non-empty required)
            build_stage="Z9",  # invalid
            date="2025/13/40",  # invalid date
            material_cost="-1",  # invalid price
            overhead_cost="-2",  # invalid price
            total_cost="-3",  # invalid price
        )
        file_name, sheet_name = "a.xlsx", "HDR"

        expected_fields = (
            HeaderFields.MODEL_NUMBER,
            HeaderFields.BOARD_NAME,
            HeaderFields.BOARD_SUPPLIER,
            HeaderFields.BUILD_STAGE,
            HeaderFields.BOM_DATE,
            HeaderFields.MATERIAL_COST,
            HeaderFields.OVERHEAD_COST,
            HeaderFields.TOTAL_COST,
        )

        # ACT
        errors = _check_header(file_name, sheet_name, header)

        for result, expected in zip(errors, expected_fields):
            # ASSERT
            with self.subTest("File Name", Out=result.file_name, Exp=file_name):
                self.assertEqual(result.file_name, file_name)

            with self.subTest("Sheet Name", Out=result.sheet_name, Exp=sheet_name):
                self.assertEqual(result.sheet_name, sheet_name)

            with self.subTest("Section", Out=result.location, Exp="Header"):
                self.assertEqual(result.location, "Header")

            with self.subTest("Field", Out=result.field_name, Exp=expected):
                self.assertEqual(result.field_name, expected)

            with self.subTest("Error Length", Out=len(result.message), Exp="!=0"):
                self.assertNotEqual(len(result.message), 0)


class TestCheckRows(unittest.TestCase):
    """
    Unit tests for `_check_rows` (row-level aggregation of cell and logic validations).
    """

    def test_valid_rows(self):
        """
        Should return an empty list when all rows are valid.
        """
        # ARRANGE
        rows = [_ROW_ONE, _ROW_ONE_ALT, _ROW_TWO]
        file_name = "file.xlsx"
        sheet_name = "Sheet1"

        # ACT
        errors = _check_rows(file_name, sheet_name, rows)

        # ASSERT
        with self.subTest(Out=len(errors), Exp=0):
            self.assertEqual(len(errors), 0)

    def test_invalid_row(self):
        """
        Should return a list of aggregated errors when some rows are invalid.
        """
        # ARRANGE
        rows = [
            replace(_ROW_ONE, description=""),  # cell: non-empty required
            replace(_ROW_ONE_ALT, classification="X"),  # cell: invalid classification
            replace(_ROW_TWO, sub_total="999"),  # logic: subtotal incorrect
        ]
        file_name = "file.xlsx"
        sheet_name = "Sheet1"

        expected_fields = (
            RowFields.DESCRIPTION,
            RowFields.CLASSIFICATION,
            RowFields.SUB_TOTAL,
        )
        expected_errors = 3

        # ACT
        result_errors = _check_rows("file.xlsx", "Sheet1", rows)

        for result, expected in zip(result_errors, expected_fields):
            # ASSERT
            with self.subTest("Error Length", Out=len(result.message), Exp="!=0"):
                self.assertNotEqual(len(result.message), 0)
            with self.subTest("Field", Out=result.field_name, Exp=expected):
                self.assertEqual(result.field_name, expected)


class TestCheckBoards(unittest.TestCase):
    """
    Unit tests for `_check_boards` (board-level aggregation of header and row checks).
    """

    def test_valid_board(self):
        """
        Should return empty list when both header and rows are valid.
        """
        # ARRANGE
        board = [_BOARD_ONE, _BOARD_TWO]
        file_name = "file.xlsx"

        # ACT
        errors = _check_boards(file_name, board)

        # ASSERT
        with self.subTest("No of errors", Out=len(errors), Exp=0):
            self.assertEqual(len(errors), 0)

    def test_invalid_board(self):
        """
        Should return a non-empty list when a header or row is invalid.
        """
        # ARRANGE
        board = [
            replace(
                _BOM.boards[0],
                header=replace(_HEADER, model_no="Alpha")  # invalid model_no
            ),
            replace(
                _BOM.boards[1],
                rows=[_ROW_TWO, replace(_ROW_TWO, description="")]  # invalid description
            ),
        ]
        expected_errors = 2

        # ACT
        result_errors = _check_boards("Sample.xlsx", board)

        # ASSERT
        with self.subTest("Error msg length", Out=len(result_errors), Exp=expected_errors):
            self.assertEqual(len(result_errors), expected_errors)


class TestCheckBom(unittest.TestCase):
    """
    Unit tests for `_check_bom` (BOM-level aggregation across boards).
    """

    def test_valid_bom(self):
        """
        Should return an empty list when all boards (headers + rows) are valid.
        """
        # ARRANGE
        bom = _BOM  # known good fixture

        # ACT
        errors = _check_bom(bom)

        # ASSERT
        with self.subTest("No of errors", Out=len(errors), Exp=0):
            self.assertEqual(len(errors), 0)

    def test_invalid_bom(self):
        """
        Should return a non-empty list when any board has invalid header or rows.
        """
        # ARRANGE
        bom = replace(
            _BOM, boards=[
                replace(
                    _BOM.boards[0],
                    header=replace(_HEADER, model_no="Alpha")  # invalid model_no
                ),
                replace(
                    _BOM.boards[1],
                    rows=[_ROW_TWO, replace(_ROW_TWO, description="")]  # invalid description
                ),
            ],
        )
        expected_errors = 2

        # ACT
        result_errors = _check_bom(bom)

        # ASSERT
        with self.subTest("No of errors", Out=len(result_errors), Exp=expected_errors):
            self.assertEqual(len(result_errors), expected_errors)

        for error in result_errors:
            with self.subTest("Error msg length", Out=len(error.message), Exp=">0"):
                self.assertNotEqual(len(error.message), 0)


class TestCheckV3Bom(unittest.TestCase):
    """
    Unit tests for `check_v3_bom` (BOM-level aggregation across boards).
    """

    def test_valid_bom(self):
        """
        Should return an empty string when all boards (headers + rows) are valid.
        """
        # ARRANGE
        bom = _BOM  # known good fixture

        # ACT
        error_msg = check_v3_bom(bom)

        # ASSERT
        with self.subTest("Error msg length", Out=len(error_msg), Exp=0):
            self.assertEqual(len(error_msg), 0)

    def test_invalid_bom(self):
        """
        Should return a non-empty string when any board has invalid header or rows.
        """
        # ARRANGE
        bom = replace(
            _BOM, boards=[
                replace(
                    _BOM.boards[0],
                    header=replace(_HEADER, model_no="Alpha")  # invalid model_no
                ),
                replace(
                    _BOM.boards[1],
                    rows=[_ROW_TWO, replace(_ROW_TWO, description="")]  # invalid description
                ),
            ],
        )

        # ACT
        error_msg = check_v3_bom(bom)

        # ASSERT
        with self.subTest("Error msg length", Out=len(error_msg), Exp=">0"):
            self.assertNotEqual(len(error_msg), 0)


if __name__ == "__main__":
    unittest.main()
