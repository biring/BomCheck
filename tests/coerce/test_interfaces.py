"""
Unit tests for the public interfaces of the `coerce` package.

This module exercises representative valid and invalid paths across the validators exposed via `src.coerce.interfaces`. It provides smoke coverage for the public API and ensures consistent exception behavior on malformed inputs.

Example Usage:
    # Preferred run from project root:
    python -m unittest tests/coerce/test_interfaces.py

    # Discover all tests:
    python -m unittest discover -s tests

Dependencies:
    - Python >= 3.10
    - Standard Library: unittest

Notes:
    - Focus on availability, basic callability, and minimal behavioral checks; deep logic is covered in module-specific tests.
"""

import unittest
from dataclasses import replace

from tests.fixtures import v3_bom as fx
from src.coerce import interfaces as coerce


class TestV3Bom(unittest.TestCase):
    """
    Tests for `v3_Bom`.
    """

    def test_valid(self):
        """
        Should keep BOM values unchanged and produce an empty log.
        """
        # ARRANGE
        src = fx.BOM_B  # Clean fixture
        # ACT
        out_bom, log = coerce.v3_bom(src)
        # ASSERT
        with self.subTest("Log size", Out=len(log), Exp=0):
            self.assertEqual(len(log), 0, log)
        with self.subTest("Type contract"):
            self.assertIsInstance(out_bom, type(src))
            self.assertIsInstance(log, tuple)

    def test_invalid(self):
        """
        Should coerce values for a minimally dirty BOM and produce a non-empty log.
        """
        # ARRANGE (start clean and add space(s) to dirty up a field)
        src_dirty = replace(
            fx.BOM_A,
            boards=(
                replace(
                    fx.BOARD_A,
                    header=replace(fx.BOARD_A.header, board_name=" " + fx.BOARD_A.header.board_name + " "),
                ),
            ),
        )
        # ACT
        out_bom, log = coerce.v3_bom(src_dirty)

        # ASSERT
        with self.subTest("Log size", Out=len(log), Exp=">0"):
            self.assertGreater(len(log), 0)


if __name__ == "__main__":
    unittest.main()
