"""
Unit tests for the helper module in correct package.

Example Usage:
    # Preferred usage via project-root invocation:
    python -m unittest tests/correct/test__helper.py

    # Direct discovery (runs all tests, including this module):
    python -m unittest discover -s tests

Dependencies:
    - Python >= 3.10
    - Standard Library: unittest
    - External Packages: None

Notes:

License:
    - Internal Use Only
"""

import re
import unittest

# noinspection PyProtectedMember
import src.correct._helper as helper  # Direct internal import — acceptable in tests


class TestFloatsEqual(unittest.TestCase):
    """
    Unit tests for the `floats_equal` function.
    """

    def test_exactly_equal(self):
        """
        Should return True for floats that are exactly equal.
        """
        # ARRANGE
        value_a = 1.234567
        value_b = 1.234567
        expected = True

        # ACT
        result = helper.floats_equal(value_a, value_b)

        # ASSERT
        with self.subTest(Out=result, Exp=expected):
            self.assertEqual(result, expected)

    def test_equal_within_tolerance(self):
        """
        Should return True when floats differ only by tiny floating-point noise.
        """
        # ARRANGE
        value_a = 1.0000001
        value_b = 1.0000002
        expected = True  # Within rounding precision and epsilon tolerance

        # ACT
        result = helper.floats_equal(value_a, value_b)

        # ASSERT
        with self.subTest(Out=result, Exp=expected):
            self.assertEqual(result, expected)

    def test_not_equal_outside_tolerance(self):
        """
        Should return False when floats differ more than the tolerance allows.
        """
        # ARRANGE
        value_a = 1.000001
        value_b = 1.00001
        expected = False  # Difference too large

        # ACT
        result = helper.floats_equal(value_a, value_b)

        # ASSERT
        with self.subTest(Out=result, Exp=expected):
            self.assertEqual(result, expected)

    def test_rounding_effect(self):
        """
        Should return True for values that round to the same 6th decimal place.
        """
        # ARRANGE
        # Both round to 6 decimals as 1.234567
        value_a = 1.2345671
        value_b = 1.2345674
        expected = True  # After rounding: equal -> diff 0.0 < 1e-6

        # ACT
        result = helper.floats_equal(value_a, value_b)

        # ASSERT
        with self.subTest(Out=result, Exp=expected):
            self.assertEqual(result, expected)

    def test_boundary_at_epsilon(self):
        """
        Should return False when the post-rounding difference equals epsilon (1e-6).
        """
        # ARRANGE
        # After rounding: 2.123456 vs 2.123457 -> diff = 0.000001 == _EPSILON
        value_a = 2.1234564
        value_b = 2.1234565
        expected = False  # difference == _EPSILON, and code uses `< _EPSILON`

        # ACT
        result = helper.floats_equal(value_a, value_b)

        # ASSERT
        with self.subTest(Out=result, Exp=expected):
            self.assertEqual(result, expected)


if __name__ == "__main__":
    unittest.main()
