"""
Unit tests for the Version 3 BOM fixer module.

Example Usage:
    # Preferred usage via project-root invocation:
    python -m unittest tests/fixer/test__v3_bom.py

    # Direct discovery (runs all tests, including this module):
    python -m unittest discover -s tests

Dependencies:
    - Python >= 3.10
    - Standard Library: unittest, typing, unittest.mock
    - Internal Packages: src.fixer._v3_bom, src.fixer._types, src.models.interfaces

Notes:
    - Tests mock correction, CLI, and runtime interfaces to isolate orchestration from rule logic.
    - Fixtures under `tests.fixtures.v3_bom` provide deterministic BOM structures for comparison.
    - Focus is on structural integrity, logging accuracy, and controlled exception handling.

License:
    - Internal Use Only
"""
import unittest
from dataclasses import replace
from unittest.mock import patch
from src.models import interfaces as mdl
from src.runtime import interfaces as rt  # for patch at interface
from src.cli import interfaces as cli  # for patch at interface
# noinspection PyProtectedMember
from src.fixer import _v3_bom as fb  # Direct internal import — acceptable in tests
# noinspection PyProtectedMember
from src.fixer import _types as ft  # Direct internal import — acceptable in tests
from tests.fixtures import v3_bom as bf

COMPONENT_TYPE_LOOKUP = {
    "Capacitor": ["Cap", "Capacitor", "Ceramic Capacitor", "Electrolytic Capacitor"],
    "Resistor": ["Res", "Resistor", "Wire Wound Resistance"],
    "Relay": ["Relay"],
}


class TestFixV3Bom(unittest.TestCase):
    """
    Unit test for the `fix_v3_bom` function.
    """

    def test_valid(self):
        """
        Should NOT modify valid BOM data and return an empty change-log.
        """
        # ARRANGE
        src = bf.BOM_B  # Clean fixture
        with patch.object(rt, "get_component_type_data_map") as p_data_map:
            p_data_map.return_value = COMPONENT_TYPE_LOOKUP
            # ACT
            out_bom, log = fb.fix_v3_bom(src)
        # ASSERT
        with self.subTest("Log size", Out=len(log), Exp=0):
            self.assertEqual(len(log), 0, log)

    def test_invalid(self):
        """
        Should apply corrections to a minimally dirty BOM and produce a non-empty change-log.
        """
        # ARRANGE (start clean and add space(s) to dirty up a field)
        in_bom = replace(
            bf.BOM_A, boards=(
                replace(
                    bf.BOARD_A, header=replace(
                        bf.BOARD_A.header, board_name=" " + bf.BOARD_A.header.board_name + " "
                    ),
                ),
            ),
        )

        with (
            patch.object(rt, "get_component_type_data_map") as p_data_map,
            patch.object(cli, "prompt_for_string_value") as p_prompt,
            patch.object(cli, "show_info"),
            patch.object(cli, "show_warning"),
        ):
            p_prompt.return_value = bf.HEADER_A.board_name
            p_data_map.return_value = COMPONENT_TYPE_LOOKUP

            # ACT
            out_bom, log = fb.fix_v3_bom(in_bom)

        # ASSERT (spot-check)
        board_name_in = in_bom.boards[0].header.board_name
        board_name_out = out_bom.boards[0].header.board_name
        with self.subTest("Coerced cell", In=board_name_in, Out=board_name_out):
            self.assertNotEqual(board_name_in, board_name_out)
        with self.subTest("Log size", Out=len(log), Exp=">0"):
            self.assertGreater(len(log), 0)

    def test_raise(self):
        """
        Should raise ValueError when a helper function fails during board reconstruction.
        """
        # ARRANGE
        src = bf.BOM_A
        expected = ValueError.__name__

        with patch.object(fb, "_fix_header_manual") as p_row:
            p_row.side_effect = ValueError("mapping failed")
            # ACT
            try:
                _ = fb.fix_v3_bom(src)
                result = ""
            except ValueError:
                result = ValueError.__name__

            # ASSERT
            with self.subTest(Out=result, Exp=expected):
                self.assertEqual(result, expected)


class TestFixHeaderManual(unittest.TestCase):
    """
    Unit test for the `_fix_header_manual` function.
    """

    def reset_log(self):
        self.log = ft.ChangeLog()
        self.log.set_file_name("TestFile")
        self.log.set_sheet_name("TestSheet")
        self.log.set_section_name("TestSection")

    def test_valid(self):
        """
        Should keep header values unchanged and produce no log entries.
        """
        # ARRANGE
        header_in = bf.HEADER_A

        # ACT
        self.reset_log()
        header_out = fb._fix_header_manual(self.log, header_in)
        log_length = len(self.log.to_tuple())

        # ASSERT
        for field, str_in, str_out, str_exp in zip(header_out.__dict__.keys(), header_in.__dict__.values(),
                                                   header_out.__dict__.values(), header_in.__dict__.values()):
            with self.subTest(field, In=str_in, Out=str_out, Exp=str_exp):
                self.assertEqual(str_out, str_exp)

        with self.subTest("Empty Log", Out=log_length, Exp=0):
            self.assertEqual(log_length, 0)

    def test_invalid_assisted(self):
        """
        Should prompt user to correct invalid header fields and record corresponding log entries.
        """
        # ARRANGE
        cases = [
            (mdl.HeaderFields.MODEL_NUMBER, replace(bf.HEADER_A, model_no="#")),
            (mdl.HeaderFields.BOARD_NAME, replace(bf.HEADER_A, board_name="#")),
        ]

        for label, header_in in cases:
            attr_name = mdl.Header.get_attr_name_by_label(label)
            prompt_response = getattr(bf.HEADER_A, attr_name)

            with (
                patch.object(rt, "get_component_type_data_map") as p_data_map,
                patch.object(cli, "prompt_for_string_value") as p_prompt,
                patch.object(cli, "show_info"),
                patch.object(cli, "show_warning"),
            ):
                p_prompt.return_value = prompt_response
                p_data_map.return_value = COMPONENT_TYPE_LOOKUP

                # ACT
                self.reset_log()
                header_out = fb._fix_header_manual(self.log, header_in)
                str_in = getattr(header_in, attr_name)
                str_out = getattr(header_out, attr_name)
                str_exp = getattr(bf.HEADER_A, attr_name)
                log_list = self.log.to_tuple()

                # ASSERT
                with self.subTest(label, In=str_in, Out=str_out, Exp=str_exp):
                    self.assertEqual(str_out, str_exp)
                with self.subTest("Log contains", Out=log_list[0], Exp=label):
                    self.assertIn(label, log_list[0])
                with self.subTest("Log size", Out=len(log_list), Exp=1):
                    self.assertEqual(len(log_list), 1)

    def test_raises(self):
        """
        Should raise ValueError when header reconstruction fails due to invalid field mapping.
        """
        # ARRANGE
        header_in = replace(bf.HEADER_A, model_no="#")  # force an update to trigger mapping
        expected = ValueError.__name__

        with (
            patch.object(type(header_in), "__init__") as p_row,
            patch.object(rt, "get_component_type_data_map") as p_data_map,
            patch.object(cli, "prompt_for_string_value") as p_prompt,
            patch.object(cli, "show_info"),
            patch.object(cli, "show_warning"),
        ):
            p_prompt.return_value = bf.HEADER_A.model_no
            p_data_map.return_value = COMPONENT_TYPE_LOOKUP
            p_row.side_effect = TypeError("bad mapping")
            # ACT
            self.reset_log()
            try:
                _ = fb._fix_header_manual(self.log, header_in)
                result = ""
            except ValueError:
                result = ValueError.__name__

            # ASSERT
            with self.subTest("Raise type", Out=result, Exp=expected):
                self.assertEqual(result, expected)


class TestFixHeaderAuto(unittest.TestCase):
    """
    Unit test for the `_fix_header_auto` function.
    """

    def reset_log(self):
        self.log = ft.ChangeLog()
        self.log.set_file_name("TestFile")
        self.log.set_sheet_name("TestSheet")
        self.log.set_section_name("TestSection")

    def test_valid(self):
        """
        Should keep header cost fields consistent and produce no log entries.
        """
        # ARRANGE
        board_in = bf.BOARD_A
        header_in = board_in.header

        # ACT
        self.reset_log()
        header_out = fb._fix_header_auto(self.log, board_in)
        log_length = len(self.log.to_tuple())

        # ASSERT
        for field, str_in, str_out, str_exp in zip(header_out.__dict__.keys(), header_in.__dict__.values(),
                                                   header_out.__dict__.values(), header_in.__dict__.values()):
            with self.subTest(field, In=str_in, Out=str_out, Exp=str_exp):
                self.assertEqual(str_out, str_exp)

        with self.subTest("Empty Log", Out=log_length, Exp=0):
            self.assertEqual(log_length, 0)

    def test_invalid(self):
        """
        Should automatically correct cost fields and record corresponding log entries.
        """
        # ARRANGE
        cases = [
            (mdl.HeaderFields.MATERIAL_COST,
             replace(bf.BOARD_A, header=replace(bf.BOARD_A.header, material_cost="99"))),
            (mdl.HeaderFields.TOTAL_COST, replace(bf.BOARD_A, header=replace(bf.BOARD_A.header, total_cost="99"))),
        ]

        for label, board_in in cases:
            header_in = board_in.header
            attr_name = mdl.Header.get_attr_name_by_label(label)
            prompt_response = getattr(header_in, attr_name)

            with (
                patch.object(rt, "get_component_type_data_map") as p_data_map,
                patch.object(cli, "prompt_for_string_value") as p_prompt,
                patch.object(cli, "show_info"),
                patch.object(cli, "show_warning"),
            ):
                p_prompt.return_value = prompt_response
                p_data_map.return_value = COMPONENT_TYPE_LOOKUP

                # ACT
                self.reset_log()
                header_out = fb._fix_header_auto(self.log, board_in)
                str_in = getattr(header_in, attr_name)
                str_out = getattr(header_out, attr_name)
                str_exp = getattr(bf.HEADER_A, attr_name)
                log_list = self.log.to_tuple()

                # ASSERT
                with self.subTest(label, In=str_in, Out=str_out, Exp=str_exp):
                    self.assertEqual(str_out, str_exp)
                with self.subTest("Log contains", Out=log_list[0], Exp=label):
                    self.assertIn(label, log_list[0])
                with self.subTest("Log size", Out=len(log_list), Exp=1):
                    self.assertEqual(len(log_list), 1)

    def test_raises(self):
        """
        Should raise ValueError when header reconstruction fails during automatic corrections.
        """
        # ARRANGE
        board_in = replace(
            bf.BOARD_A, header=replace(
                bf.BOARD_A.header, material_cost="99"
            )
        )
        header = board_in.header
        expected = ValueError.__name__

        with patch.object(type(header), "__init__") as p_row:
            p_row.side_effect = TypeError("bad mapping")
            # ACT
            self.reset_log()
            try:
                _ = fb._fix_header_auto(self.log, board_in)
                result = ""
            except ValueError:
                result = ValueError.__name__

            # ASSERT
            with self.subTest("Raise type", Out=result, Exp=expected):
                self.assertEqual(result, expected)


class TestFixRowManual(unittest.TestCase):
    """
    Unit test for the `_fix_row_manual` function.
    """

    def setUp(self):
        self.log = ft.ChangeLog()
        self.log.set_file_name("TestFile")
        self.log.set_sheet_name("TestSheet")
        self.log.set_section_name("TestSection")

    def test_valid(self):
        """
        Should keep row values unchanged and produce no log entries.
        """
        # ARRANGE
        row = bf.ROW_A_1

        with patch.object(rt, "get_component_type_data_map") as p_data_map:
            p_data_map.return_value = COMPONENT_TYPE_LOOKUP
            # ACT
            out_row = fb._fix_row_manual(self.log, row)
            log_length = len(self.log.to_tuple())

        # ASSERT
        for field, str_in, str_out, str_exp in zip(out_row.__dict__.keys(), row.__dict__.values(),
                                                   out_row.__dict__.values(), row.__dict__.values()):
            with self.subTest(field, In=str_in, Out=str_out, Exp=str_exp):
                self.assertEqual(str_out, str_exp)

        with self.subTest("Empty Log", Out=log_length, Exp=0):
            self.assertEqual(log_length, 0)

    def test_invalid_assisted(self):
        """
        Should prompt user to correct invalid row fields and record corresponding log entries.
        """
        # ARRANGE
        cases = [
            (mdl.RowFields.ITEM, replace(bf.ROW_A_1, item="?")),
            (mdl.RowFields.COMPONENT, replace(bf.ROW_A_1, component_type="?")),
            (mdl.RowFields.PACKAGE, replace(bf.ROW_A_1, device_package="?")),
            (mdl.RowFields.DESCRIPTION, replace(bf.ROW_A_1, description="")),
            (mdl.RowFields.UNITS, replace(bf.ROW_A_1, unit="?")),
            (mdl.RowFields.CLASSIFICATION, replace(bf.ROW_A_1, classification="?")),
            (mdl.RowFields.MANUFACTURER, replace(bf.ROW_A_1, manufacturer="?")),
            (mdl.RowFields.MFG_PART_NO, replace(bf.ROW_A_1, mfg_part_number="?")),
            (mdl.RowFields.UL_VDE_NUMBER, replace(bf.ROW_A_1, ul_vde_number="?")),
            (mdl.RowFields.VALIDATED_AT, replace(bf.ROW_A_1, validated_at="?")),
            (mdl.RowFields.QTY, replace(bf.ROW_A_1, qty="?")),
            (mdl.RowFields.DESIGNATOR, replace(bf.ROW_A_1, designator="?")),
            (mdl.RowFields.UNIT_PRICE, replace(bf.ROW_A_1, unit_price="?")),
        ]

        for label, row_in in cases:
            self.setUp()
            attr_name = mdl.Row.get_attr_name_by_label(label)
            prompt_response = getattr(bf.ROW_A_1, attr_name)

            with (
                patch.object(rt, "get_component_type_data_map") as p_data_map,
                patch.object(cli, "prompt_for_string_value") as p_prompt,
                patch.object(cli, "show_info"),
                patch.object(cli, "show_warning"),
            ):
                p_prompt.return_value = prompt_response
                p_data_map.return_value = COMPONENT_TYPE_LOOKUP

                # ACT
                row_out = fb._fix_row_manual(self.log, row_in)
                str_in = getattr(row_in, attr_name)
                str_out = getattr(row_out, attr_name)
                str_exp = getattr(bf.ROW_A_1, attr_name)
                log_list = self.log.to_tuple()

                # ASSERT
                with self.subTest(label, In=str_in, Out=str_out, Exp=str_exp):
                    self.assertEqual(str_out, str_exp)
                with self.subTest("Log contains", Out=log_list[0], Exp=label):
                    self.assertIn(label, log_list[0])
                with self.subTest("Log size", Out=len(log_list), Exp=1):
                    self.assertEqual(len(log_list), 1)

    def test_raises(self):
        """
        Should raise ValueError when row reconstruction fails during manual corrections.
        """
        # ARRANGE
        label = mdl.RowFields.ITEM
        row = replace(bf.ROW_A_1, item="?")
        attr_name = mdl.Row.get_attr_name_by_label(label)
        prompt_response = getattr(bf.ROW_A_1, attr_name)
        expected = ValueError.__name__

        with (
            patch.object(type(row), "__init__") as p_row,
            patch.object(rt, "get_component_type_data_map") as p_data_map,
            patch.object(cli, "prompt_for_string_value") as p_prompt,
            patch.object(cli, "show_info"),
            patch.object(cli, "show_warning"),
        ):
            p_row.side_effect = TypeError("bad mapping")
            p_prompt.return_value = prompt_response
            p_data_map.return_value = COMPONENT_TYPE_LOOKUP
            # ACT
            try:
                _ = fb._fix_row_manual(self.log, row)
                result = ""
            except ValueError:
                result = ValueError.__name__

            # ASSERT
            with self.subTest("Raise type", Out=result, Exp=expected):
                self.assertEqual(result, expected)


class TestFixRowAuto(unittest.TestCase):
    """
    Unit test for the `_fix_row_auto` function.
    """

    def setUp(self):
        self.log = ft.ChangeLog()
        self.log.set_file_name("TestFile")
        self.log.set_sheet_name("TestSheet")
        self.log.set_section_name("TestSection")

    def test_valid(self):
        """
        Should keep row values unchanged and produce no log entries.
        """
        # ARRANGE
        row = bf.ROW_A_1

        with patch.object(rt, "get_component_type_data_map") as p_data_map:
            p_data_map.return_value = COMPONENT_TYPE_LOOKUP
            # ACT
            out_row = fb._fix_row_auto(self.log, row)
            log_length = len(self.log.to_tuple())

        # ASSERT
        for field, str_in, str_out, str_exp in zip(out_row.__dict__.keys(), row.__dict__.values(),
                                                   out_row.__dict__.values(), row.__dict__.values()):
            with self.subTest(field, In=str_in, Out=str_out, Exp=str_exp):
                self.assertEqual(str_out, str_exp)

        with self.subTest("Empty Log", Out=log_length, Exp=0):
            self.assertEqual(log_length, 0)

    def test_invalid(self):
        """
        Should automatically correct invalid row fields and record corresponding log entries.
        """
        # ARRANGE
        cases = [
            (mdl.RowFields.COMPONENT, replace(bf.ROW_A_1, component_type="Res")),
            (mdl.RowFields.DESIGNATOR, replace(bf.ROW_A_1, designator="R1-R2")),
            (mdl.RowFields.SUB_TOTAL, replace(bf.ROW_A_1, sub_total="999")),
        ]

        for label, row_in in cases:
            self.setUp()
            attr_name = mdl.Row.get_attr_name_by_label(label)
            prompt_response = getattr(bf.ROW_A_1, attr_name)

            with (
                patch.object(rt, "get_component_type_data_map") as p_data_map,
                patch.object(cli, "prompt_for_string_value") as p_prompt,
                patch.object(cli, "show_info"),
                patch.object(cli, "show_warning"),
            ):
                p_prompt.return_value = prompt_response
                p_data_map.return_value = COMPONENT_TYPE_LOOKUP

                # ACT
                row_out = fb._fix_row_auto(self.log, row_in)
                str_in = getattr(row_in, attr_name)
                str_out = getattr(row_out, attr_name)
                str_exp = getattr(bf.ROW_A_1, attr_name)
                log_list = self.log.to_tuple()

                # ASSERT
                with self.subTest(label, In=str_in, Out=str_out, Exp=str_exp):
                    self.assertEqual(str_out, str_exp)
                with self.subTest("Log contains", Out=log_list[0], Exp=label):
                    self.assertIn(label, log_list[0])
                with self.subTest("Log size", Out=len(log_list), Exp=1):
                    self.assertEqual(len(log_list), 1)

    def test_raises(self):
        """
        Should raise ValueError when row reconstruction fails during automatic corrections.
        """
        # ARRANGE
        row = replace(bf.ROW_A_1, sub_total="999")
        expected = ValueError.__name__

        with patch.object(type(row), "__init__") as p_row:
            p_row.side_effect = TypeError("bad mapping")
            # ACT
            try:
                _ = fb._fix_row_auto(self.log, row)
                result = ""
            except ValueError:
                result = ValueError.__name__

            # ASSERT
            with self.subTest("Raise type", Out=result, Exp=expected):
                self.assertEqual(result, expected)


if __name__ == "__main__":
    unittest.main()
