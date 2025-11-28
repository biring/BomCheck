"""
Unit tests for the public interface of the `verifiers` package.

This module verifies that the exposed API (`v3_bom`) behaves as expected:
    - Valid BOM inputs complete without raising exceptions
    - Invalid or modified BOM values raise the correct exception type
    - Tests focus on interface behavior rather than internal verifier logic

Example Usage:
    # Preferred usage via project-root invocation:
    python -m unittest tests/verifiers/tests_interfaces.py

    # Direct discovery (runs all tests, including this module):
    python -m unittest discover -s tests

Dependencies:
    - Python >= 3.10
    - Standard Library: unittest, dataclasses
    - Internal Packages: src.verifiers.interfaces, tests.fixtures.v3_bom

Notes:
    - Treats the interface as a stable API surface; internal implementations may change.
    - Uses minimal fixture mutation to induce rule violations deterministically.
    - Assertions check only outcomes (exception/no exception), not internal details.

License:
    - Internal Use Only
"""

import unittest
from dataclasses import replace
from src.verifiers import interfaces as verify
from tests.fixtures import v3_bom as bfx


class TestVerifyV3Bom(unittest.TestCase):
    """
    Unit tests for `verify_v3_bom`.
    """

    def test_happy_path(self):
        """
        Should NOT raise any exception when the BOM is valid.
        """
        # ARRANGE
        bom = bfx.BOM_A

        # ACT
        try:
            verify.v3_bom(bom)
            actual = ""
        except Exception as ex:
            actual = type(ex).__name__

        # ASSERT
        with self.subTest("No exception", Out=actual):
            self.assertEqual(actual, "")

    def test_incorrect_value(self):
        """
        Should raise ValueError when any board violates a BOM-level rule.
        """
        # ARRANGE
        # Make board material cost incorrect.
        bom = replace(
            bfx.BOM_A,
            boards=(
                replace(
                    bfx.BOARD_A,
                    header=replace(bfx.BOARD_A.header, material_cost="99.99"),
                ),
            ),
        )
        expected = ValueError.__name__

        # ACT
        try:
            verify.v3_bom(bom)
            actual = ""
        except Exception as ex:
            actual = type(ex).__name__

        # ASSERT
        with self.subTest("Raise exception", Out=actual, Expected=expected):
            self.assertEqual(actual, expected)


if __name__ == "__main__":
    unittest.main()
