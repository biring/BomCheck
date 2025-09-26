"""
Unit tests for the approval validator helpers.

Example Usage:
    # Project-root invocation:
    python -m unittest tests/rules/approve/test__common.py

    # Or run via discovery from the tests root
    python -m unittest discover -s tests

Dependencies:
    - Python >= 3.10
    - Standard Library: unittest, re
    - External Packages: None

Notes:
    - A deliberately broken regex object is used to exercise the RuntimeError branch

License:
    - Internal Use Only
"""

import re
import unittest

# noinspection PyProtectedMember
from src.approve import _common as common  # Direct internal import — acceptable in tests


class TestApproveOrRaise(unittest.TestCase):
    """
    Unit tests for the `common.approve_or_raise` function.
    """

    def setUp(self):
        """
        Define reusable test parameters.
        """
        self.label = "Quantity"
        self.rule = " Valid '{a}' must be numeric."

        # Sample regex patterns
        self.numeric_pattern = re.compile(r'^[0-9]+$')
        self.alpha_pattern = re.compile(r'^[A-Za-z]+$')

    def test_valid(self):
        """
        Should not raise an exception when the value matches the regex pattern.
        """
        # ARRANGE
        value = "123"

        # ACT / ASSERT
        try:
            common.approve_or_raise(value, self.numeric_pattern, self.label, self.rule)
            result = ""
        except Exception as e:
            result = type(e).__name__

        expected = ""
        with self.subTest(Out=result, Exp=expected):
            self.assertEqual(result, expected)

    def test_invalid(self):
        """
        Should raise ValueError when the value does not match the regex pattern.
        """
        # ARRANGE
        value = "ABC"
        expected = ValueError.__name__

        # ACT
        try:
            common.approve_or_raise(value, self.numeric_pattern, self.label, self.rule)
            result = "No Exception"
        except Exception as e:
            result = type(e).__name__

        # ASSERT
        with self.subTest(Out=result, Exp=expected):
            self.assertEqual(result, expected)

    def test_invalid_regex(self):
        """
        Should raise TypeError when a non-regex object is passed as pattern.
        """
        # ARRANGE
        value = "123"
        invalid_pattern = "not_a_regex"
        expected = TypeError.__name__

        # ACT
        try:
            common.approve_or_raise(value, invalid_pattern, self.label,
                                    self.rule)  # type: ignore[arg-type]
            result = "No Exception"
        except Exception as e:
            result = type(e).__name__

        # ASSERT
        with self.subTest(Out=result, Exp=expected):
            self.assertEqual(result, expected)

    def test_regex_error(self):
        """
        Should raise RuntimeError when regex engine fails internally during runtime.
        """
        # ARRANGE
        value = "123"
        # Invalid regex will cause re.error during compilation
        try:
            # NOTE:
            # The regex below is deliberately invalid and will trigger a re.error
            # during compilation ("bad character range"). This is intentional to
            # simulate a corrupt regex object for testing the RuntimeError branch
            # of approve_or_raise. Ignore the warning/error at compile time.
            bad_pattern = re.compile(r'[A-')
        except re.error:
            # Simulate an already compiled object that triggers re.error at match time
            class BadPattern:
                def fullmatch(self, _):
                    raise re.error("broken regex")

            bad_pattern = BadPattern()

        expected = RuntimeError.__name__

        # ACT
        try:
            common.approve_or_raise(value, bad_pattern, self.label, self.rule)
            result = "No Exception"
        except Exception as e:
            result = type(e).__name__

        # ASSERT
        with self.subTest(Out=result, Exp=expected):
            self.assertEqual(result, expected)


class TestFloatsEqual(unittest.TestCase):
    """
    Unit tests for the `common.floats_equal` function.
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
        result = common.floats_equal(value_a, value_b)

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
        result = common.floats_equal(value_a, value_b)

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
        result = common.floats_equal(value_a, value_b)

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
        result = common.floats_equal(value_a, value_b)

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
        result = common.floats_equal(value_a, value_b)

        # ASSERT
        with self.subTest(Out=result, Exp=expected):
            self.assertEqual(result, expected)


if __name__ == "__main__":
    unittest.main()
