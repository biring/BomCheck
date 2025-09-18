"""
Unit tests for interactive console input helpers.

These tests validate the behavior of user input request to ensure consistency in CLI workflows.
Example Usage:
    # Preferred usage via project-root invocation:
    python -m unittest tests/cli/test__request.py

    # Direct discovery (runs all tests, including this module):
    python -m unittest discover -s tests

Dependencies:
    - Python >= 3.9
    - Standard Library: unittest, unittest.mock
    - Internal: src.cli._console, src.cli._show, src.utils

Notes:
    - Keeps tests isolated and non-interactive — no real stdin/stdout is used.

License:
    - Internal Use Only
"""

import unittest
from unittest.mock import patch

# noinspection PyProtectedMember
from src.cli import _request as request


class TestStringInput(unittest.TestCase):
    """
    Unit tests for string_input.
    """

    def test_valid(self):
        """
        Should return the same string that builtins.input yields.
        """
        # ARRANGE
        expected = "4 A 5"
        prompt = "Test Input: "

        with (
            patch("builtins.input", return_value=expected) as mock_input,
            patch("builtins.print")
        ):
            # ACT
            actual = request.string_input(prompt)

        # ASSERT
        with self.subTest("Return Value", Out=actual, Exp=expected):
            self.assertEqual(actual, expected)
        with self.subTest("Call count", Out=mock_input.call_count, Exp=1):
            self.assertEqual(mock_input.call_count, 1)

    def test_eof_error(self):
        """
        Should raise EOFError if input stream closes before reading.
        """
        prompt = "Enter number: "

        with patch("builtins.input", side_effect=EOFError()):
            try:
                # ACT
                request.string_input(prompt)
                result = "NoError"  # If nothing raised
            except Exception as e:
                result = e.__class__.__name__

        # ASSERT
        with self.subTest(Out=result, Exp="EOFError"):
            self.assertEqual(result, "EOFError")

    def test_keyboard_interrupt(self):
        """
        Should raise KeyboardInterrupt if user aborts with Ctrl+C.
        """
        prompt = "Enter number: "

        with patch("builtins.input", side_effect=KeyboardInterrupt()):
            try:
                # ACT
                request.string_input(prompt)
                result = "NoError"  # If nothing raised
            except BaseException as e:
                result = e.__class__.__name__

        # ASSERT
        with self.subTest(Out=result, Exp="KeyboardInterrupt"):
            self.assertEqual(result, "KeyboardInterrupt")


class TestIntegerInput(unittest.TestCase):
    """
    Unit tests for integer_input.
    """

    def test_valid(self):
        """
        Should return the parsed integer when input is valid.
        """
        # ARRANGE
        prompt = "Enter number: "
        user_input = "42"
        expected = int(42)

        with (
            patch("builtins.input", return_value=user_input) as mock_input,
            patch("builtins.print") as mock_print,
        ):
            # ACT
            result = request.integer_input(prompt)

        # ASSERT
        with self.subTest("Return Value", Out=result, Exp=expected):
            self.assertEqual(result, expected)
        with self.subTest("Call count", Out=mock_input.call_count, Exp=1):
            self.assertEqual(mock_input.call_count, 1)

    def test_invalid(self):
        """
        Should warn and reprompt until parse_to_integer succeeds, then return the parsed integer.
        """
        # ARRANGE
        prompt = "Enter number: "
        invalid_input = "abc"
        valid_input = "99"
        user_inputs = [invalid_input, valid_input]

        def parse_side_effect(val):
            if val == "abc":
                raise ValueError("not an int")
            return 99

        with (
            patch("builtins.input", side_effect=user_inputs) as mock_input,
            patch("builtins.print") as mock_prints,
        ):
            # ACT
            result = request.integer_input(prompt)

        # ASSERT
        with self.subTest("Return value", Out=result, Exp=valid_input):
            self.assertEqual(result, 99)

        with self.subTest("Call count", Out=mock_input.call_count, Exp=2):
            self.assertEqual(mock_input.call_count, 2)

    def test_eof_error_propagates(self):
        """
        Should raise EOFError if input stream closes before reading.
        """
        prompt = "Enter number: "

        with patch("builtins.input", side_effect=EOFError()):
            try:
                # ACT
                request.integer_input(prompt)
                result = "NoError"  # If nothing raised
            except Exception as e:
                result = e.__class__.__name__

        # ASSERT
        with self.subTest(Out=result, Exp="EOFError"):
            self.assertEqual(result, "EOFError")

    def test_keyboard_interrupt(self):
        """
        Should raise KeyboardInterrupt if user aborts with Ctrl+C.
        """
        prompt = "Enter number: "

        with patch("builtins.input", side_effect=KeyboardInterrupt()):
            try:
                # ACT
                request.integer_input(prompt)
                result = "NoError"  # If nothing raised
            except BaseException as e:
                result = e.__class__.__name__

        # ASSERT
        with self.subTest(Out=result, Exp="KeyboardInterrupt"):
            self.assertEqual(result, "KeyboardInterrupt")


if __name__ == "__main__":
    unittest.main()
