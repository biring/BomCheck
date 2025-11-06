"""
Unit tests for autocorrection functions.

Example Usage:
    # Preferred usage via project-root invocation:
    python -m unittest tests/correct/test__auto.py

    # Direct discovery (runs all tests, including this module):
    python -m unittest discover -s tests

Dependencies:
    - Python >= 3.10
    - Standard Library: unittest, dataclasses
    - Project Modules: src.correct._auto, src.models.interfaces, tests.fixtures.v3_bom, tests.fixtures.v3_value

Notes:
    - Tests use dataclasses.replace for variant creation
    - Fixtures provide stable representative BOM objects
    - Focuses on correctness and deterministic audit log output
    - Internal-only test coverage for private autocorrect utilities

License:
    - Internal Use Only
"""

import unittest
from dataclasses import replace

from src.models import interfaces as mdl

# noinspection PyProtectedMember
from src.correct import _auto as auto  # Direct internal import — acceptable in tests

from tests.fixtures import v3_value as vfx
from tests.fixtures import v3_bom as bfx


class TestComponentTypeLookup(unittest.TestCase):
    """
    Unit tests for the `component_type_lookup` function.
    """

    def test_exact_match(self):
        """
        Should return the canonical key when both metrics match a known alias above the threshold.
        """
        # ARRANGE
        str_in = "SMD Ceramic Capacitor"
        ignore_list = ("SMD", "DIP")
        lookup_dict = {
            "Capacitor": ["Ceramic Capacitor", "Electrolytic Capacitor"],
            "Resistor": ["Resistor", "Res", "Resistance"]
        }
        expected_out = "Capacitor"

        # ACT
        result, log = auto.component_type_lookup(str_in, ignore_list, lookup_dict)

        # ASSERT
        with self.subTest("Output", Out=result, Exp=expected_out):
            self.assertEqual(result, expected_out)
        with self.subTest("Log", Out=log):
            self.assertIn(str_in, log)
            self.assertIn(expected_out, log)
            self.assertIn(mdl.RowFields.COMPONENT, log)

    def test_no_match_below_threshold(self):
        """
        Should return the original string and empty log when no matches exceed the threshold.
        """
        # ARRANGE
        str_in = "Unknown Part"
        ignore_str = ("SMD",)
        lookup_dict = {
            "Capacitor": ["Ceramic Capacitor", "Electrolytic Capacitor"],
            "Resistor": ["Resistor", "Res", "Resistance"]
        }

        # ACT
        result, log = auto.component_type_lookup(str_in, ignore_str, lookup_dict)

        # ASSERT
        with self.subTest("Output", Out=result, Exp=str_in):
            self.assertEqual(result, str_in)
        with self.subTest("Log", Out=log, Exp=""):
            self.assertEqual(log, "")

    def test_multiple_key_matches(self):
        """
        Should return the original input when multiple canonical keys match (ambiguity).
        """
        # ARRANGE
        str_in = "Ceramic Capacitor"
        ignore_str = ()
        lookup_dict = {
            "Capacitor": ["Ceramic Capacitor"],
            "Resistor": ["Ceramic Capacitor"],  # Duplicate alias to create ambiguity
        }

        # ACT
        result, log = auto.component_type_lookup(str_in, ignore_str, lookup_dict)

        # ASSERT
        with self.subTest("Output", Out=result, Exp=str_in):
            self.assertEqual(result, str_in)
        with self.subTest("Log", Out=log, Exp=""):
            self.assertEqual(log, "")


class TestExpandDesignators(unittest.TestCase):
    """
    Unit tests for the `expand_designators` function.
    """

    def test_no_correction(self):
        """
        Should return the original designator string and an empty change log when no corrections are made.
        """
        # ARRANGE
        cases = vfx.DESIGNATOR_GOOD

        for value_in in cases:
            # ACT
            value_out, log = auto.expand_designators(value_in)

            # ASSERT
            with self.subTest("Value Out", Out=value_out, Exp=value_in):
                self.assertEqual(value_in, value_out)
            with self.subTest("Log", Out=""):
                self.assertEqual(log, "")

    def test_correction(self):
        """
        Should return expanded range designators and a non-empty change log when corrections are made.
        """
        # ARRANGE
        field = mdl.RowFields.DESIGNATOR
        cases = (
            ("R1-R3", "R1,R2,R3"),
            ("R1, R3-R6, R12, R45-R43", "R1,R3,R4,R5,R6,R12,R45,R44,R43"),
            ("R1-R2, C10-C12", "R1,R2,C10,C11,C12"),
            ("R5-R3", "R5,R4,R3"),
        )

        for value_in, value_out in cases:
            # ACT
            out, log = auto.expand_designators(value_in)

            # ASSERT
            with self.subTest("Value Out", Out=out, Exp=value_out):
                self.assertEqual(out, value_out)
            with self.subTest("Log", Out=log):
                self.assertIn(value_in, log, value_in)
                self.assertIn(value_out, log, value_out)
                self.assertIn(field, log, field)


class TestMaterialCost(unittest.TestCase):
    """
    Unit tests for the `material_cost` function.
    """

    def test_no_correction(self):
        """
        Should return the original material cost and an empty change log when no corrections are made.
        """
        # ARRANGE
        board = bfx.BOARD_A
        expected_value = board.header.material_cost

        # ACT
        value_out, log = auto.material_cost(board.header, board.rows)

        # ASSERT
        with self.subTest("Value Out", Out=value_out, Exp=expected_value):
            self.assertEqual(value_out, expected_value)
        with self.subTest("Log", Out=log, Exp=""):
            self.assertEqual(log, "")

    def test_correction(self):
        """
        Should return corrected material cost and a non-empty change log when corrections are made.
        """
        # ARRANGE
        field = mdl.HeaderFields.MATERIAL_COST
        rows = bfx.BOARD_A.rows
        # Deliberately make header.material_cost incorrect by prefixing an extra digit
        header = replace(bfx.HEADER_B1, material_cost="1" + bfx.BOARD_A.header.material_cost)
        expected_value = bfx.BOARD_A.header.material_cost

        # ACT
        value_out, log = auto.material_cost(header, rows)

        # ASSERT
        with self.subTest("Value Out", Out=value_out, Exp=expected_value):
            self.assertEqual(value_out, expected_value)

        # Log should mention the field name and both old and new values
        with self.subTest("Log contains", Out=log):
            self.assertIn(field, log)
            self.assertIn(header.material_cost, log)
            self.assertIn(expected_value, log)

    def test_raise_on_bad_inputs(self):
        """
        Should raise ValueError when a base field cannot be parsed as float.
        """
        # ARRANGE
        good_rows = (bfx.ROW_A_1, bfx.ROW_A_2)
        good_header = bfx.HEADER_A
        # Case 1: a row with bad sub_total
        rows_bad_sub_total = (replace(bfx.ROW_A_1, sub_total="*"), bfx.ROW_A_2)

        # Case 2: header has bad material_cost (even though rows are OK)
        header_bad_material = replace(bfx.HEADER_B1, material_cost="*")

        cases = (
            (good_header, rows_bad_sub_total),
            (header_bad_material, good_rows),
        )
        expected = ValueError.__name__

        for header, rows in cases:
            # ACT
            try:
                auto.material_cost(header, rows)
                result = ""  # No exception
            except ValueError as e:
                result = type(e).__name__

            # ASSERT
            with self.subTest("Raise", Out=result, Exp=expected):
                self.assertEqual(result, expected)


class TestSubTotal(unittest.TestCase):
    """
    Unit tests for the `sub_total` function.
    """

    def test_no_correction(self):
        """
        Should return the original sub-total and an empty change log when no corrections are made.
        """
        # ARRANGE
        rows = (
            bfx.ROW_A_1,
            bfx.ROW_A_2,
            bfx.ROW_A_3,
        )

        for row in rows:
            # ACT
            value_out, log = auto.sub_total(row)

            # ASSERT
            value_in = row.sub_total
            with self.subTest("Value Out", Out=value_out, Exp=value_in):
                self.assertEqual(value_in, value_out)
            with self.subTest("Log", Out=""):
                self.assertEqual(log, "")

    def test_correction(self):
        """
        Should return corrected sub-total and a non-empty change log when corrections are made.
        """
        # ARRANGE
        field = mdl.RowFields.SUB_TOTAL
        rows = (
            (replace(bfx.ROW_A_1, sub_total="1" + bfx.ROW_A_1.sub_total), bfx.ROW_A_1.sub_total),
            (replace(bfx.ROW_A_2, sub_total="1" + bfx.ROW_A_1.sub_total), bfx.ROW_A_2.sub_total),
            (replace(bfx.ROW_A_3, sub_total="1" + bfx.ROW_A_1.sub_total), bfx.ROW_A_3.sub_total),
        )

        for row, value_out in rows:
            # ACT
            out, log = auto.sub_total(row)

            # ASSERT
            value_in = row.sub_total
            with self.subTest("Value Out", Out=out, Exp=value_out):
                self.assertEqual(out, value_out)
            with self.subTest("Log", Out=log):
                self.assertIn(value_in, log, value_in)
                self.assertIn(value_out, log, value_out)
                self.assertIn(field, log, field)

    def test_raise(self):
        """
        Should return value error when base fields can not be parsed.
        """
        # ARRANGE
        rows = (
            replace(bfx.ROW_A_1, qty="*"),
            replace(bfx.ROW_A_2, unit_price="*"),
            replace(bfx.ROW_A_3, sub_total="*"),
        )
        expected = ValueError.__name__

        for row in rows:
            # ACT
            try:
                out, log = auto.sub_total(row)
                result = ""
            except ValueError as e:
                result = type(e).__name__

            # ASSERT
            with self.subTest("Raise", Out=result, Exp=expected):
                self.assertEqual(result, expected)


class TestTotalCost(unittest.TestCase):
    """
    Unit tests for the `total_cost` function.
    """

    def test_no_correction(self):
        """
        Should return the original total cost and an empty change log when no corrections are made.
        """
        # ARRANGE
        headers = (
            bfx.HEADER_B1,
            bfx.HEADER_B2,
        )

        for header in headers:
            # ACT
            value_out, log = auto.total_cost(header)

            # ASSERT
            value_in = header.total_cost
            with self.subTest("Value Out", Out=value_out, Exp=value_in):
                self.assertEqual(value_in, value_out)
            with self.subTest("Log", Out=""):
                self.assertEqual(log, "")

    def test_correction(self):
        """
        Should return corrected total cost and a non-empty change log when corrections are made.
        """
        # ARRANGE
        field = mdl.HeaderFields.TOTAL_COST
        headers = (
            (replace(bfx.HEADER_B1, total_cost="1" + bfx.HEADER_B1.total_cost), bfx.HEADER_B1.total_cost),
            (replace(bfx.HEADER_B2, total_cost="1" + bfx.HEADER_B2.total_cost), bfx.HEADER_B2.total_cost),
        )

        for header, value_exp in headers:
            # ACT
            value_out, log = auto.total_cost(header)

            # ASSERT
            value_in = header.total_cost
            with self.subTest("Value Out", Out=value_out, Exp=value_exp):
                self.assertEqual(value_out, value_exp)
            with self.subTest("Log", Out=log):
                self.assertIn(value_out, log, value_out)
                self.assertIn(value_exp, log, value_exp)
                self.assertIn(field, log, field)

    def test_raise(self):
        """
        Should return value error when base fields can not be parsed.
        """
        # ARRANGE
        headers = (
            replace(bfx.HEADER_B1, material_cost="*"),
            replace(bfx.HEADER_B1, overhead_cost="*"),
            replace(bfx.HEADER_B1, total_cost="*"),
        )
        expected = ValueError.__name__

        for header in headers:
            # ACT
            try:
                out, log = auto.total_cost(header)
                result = ""
            except ValueError as e:
                result = type(e).__name__

            # ASSERT
            with self.subTest("Raise", Out=result, Exp=expected):
                self.assertEqual(result, expected)


if __name__ == "__main__":
    unittest.main()
