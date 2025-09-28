"""
Unit tests for common review helpers.

This module validates shared utilities in `_common`, ensuring consistent behavior across header, row, and logic review wrappers. Tests confirm that validators run correctly, errors are captured as strings, and successful inputs return empty strings.

Example Usage:
    # Preferred usage via project-root invocation:
    python -m unittest tests/review/test_common.py

    # Direct discovery (runs all tests, including this module):
    python -m unittest discover -s tests

Dependencies:
    - Python >= 3.10
    - Standard Library: unittest, typing
    - External Packages: None

Notes:
    - Tests use dummy rules (success and failure) to isolate `_common` logic.
    - This module ensures error messages are faithfully captured from raised ValueErrors.
    - Coverage focuses on correctness and consistency of `review_and_capture`.
    - No external validators are invoked; mocking is used where appropriate.

License:
    - Internal Use Only
"""
import unittest

# noinspection PyProtectedMember
from src.review import _common as common  # Direct internal import — acceptable in tests


class TestReviewAndCapture(unittest.TestCase):
    """
    Unit tests for the `review_and_capture` function.
    """

    def test_valid(self):
        """
        Should return an empty string when the rule does not raise a ValueError.
        """

        # ARRANGE
        def always_pass(value: str) -> None:
            # No error is ever raised
            return None

        value = "valid input"
        expected = ""

        # ACT
        result = common.review_and_capture(value, always_pass)

        # ASSERT
        with self.subTest(Out=result, Exp=expected):
            self.assertEqual(result, expected)

    def test_invalid(self):
        """
        Should return the ValueError message when the rule raises a ValueError.
        """

        # ARRANGE
        def fail_if_empty(value: str) -> None:
            if value == "":
                raise ValueError("Input cannot be empty")

        value = ""
        expected = "Input cannot be empty"

        # ACT
        result = common.review_and_capture(value, fail_if_empty)

        # ASSERT
        with self.subTest(Out=result, Exp=expected):
            self.assertEqual(result, expected)

    def test_raise(self):
        """
        Should capture and return the exact error message provided by the rule.
        """

        # ARRANGE
        def fail_on_number(value: str) -> None:
            if any(ch.isdigit() for ch in value):
                raise ValueError("Digits are not allowed")

        value = "abc123"
        expected = "Digits are not allowed"

        # ACT
        result = common.review_and_capture(value, fail_on_number)

        # ASSERT
        with self.subTest(Out=result, Exp=expected):
            self.assertEqual(result, expected)


class TestReviewAndCaptureByArgs(unittest.TestCase):
    """
    Unit tests for the `review_and_capture_by_args` function.
    """

    # --- Helper dummy rules used only for testing ---

    @staticmethod
    def _rule_sum_with_limit(a: int, b: int, *, limit: int = 10) -> None:
        """
        Passes if a + b <= limit; otherwise raises ValueError.
        """
        if a + b > limit:
            raise ValueError("Sum exceeds limit")

    @staticmethod
    def _rule_requires_prefix(s: str, prefix: str = "ABC") -> None:
        """
        Passes if the string starts with the given prefix; otherwise raises ValueError.
        """
        if not s.startswith(prefix):
            raise ValueError(f"Must start with '{prefix}'")

    # --- Tests ---

    def test_valid_with_pos_args(self):
        """
        Should return an empty string when the rule passes using positional args.
        """
        # ARRANGE
        expected = ""  # No error string on success

        # ACT
        result = common.review_and_capture_by_args(self._rule_sum_with_limit, 3, 4, limit=10)

        # ASSERT
        with self.subTest(Out=result, Exp=expected):
            self.assertEqual(result, expected)

    def test_valid_with_key_args(self):
        """
        Should return an empty string when the rule passes using keyword args.
        """
        # ARRANGE
        expected = ""  # No error string on success

        # ACT
        result = common.review_and_capture_by_args(
            self._rule_requires_prefix,
            s="ABC123",
            prefix="ABC",
        )

        # ASSERT
        with self.subTest(Out=result, Exp=expected):
            self.assertEqual(result, expected)

    def test_invalid_with_pos_args(self):
        """
        Should return the exact ValueError message when the rule fails (positional args).
        """
        # ARRANGE
        expected = "Sum exceeds limit"

        # ACT
        result = common.review_and_capture_by_args(self._rule_sum_with_limit, 9, 5, limit=10)

        # ASSERT
        with self.subTest(Out=result, Exp=expected):
            self.assertEqual(result, expected)

    def test_invalid_with_key_args(self):
        """
        Should return the exact ValueError message when the rule fails (keyword args).
        """
        # ARRANGE
        expected = "Must start with 'ABC'"

        # ACT
        result = common.review_and_capture_by_args(
            self._rule_requires_prefix,
            s="XYZ",
            prefix="ABC",
        )

        # ASSERT
        with self.subTest(Out=result, Exp=expected):
            self.assertEqual(result, expected)


if __name__ == "__main__":
    unittest.main()
