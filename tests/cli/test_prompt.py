"""
Unit tests for CLI prompt utilities.

This suite verifies user interface input prompt functions

Example Usage:
    # Run this test module:
    python -m unittest tests/cli/test_prompt.py

    # Discover and run all tests:
    python -m unittest discover -s tests

Dependencies:
 - Python >= 3.10
 - Standard Library: unittest, unittest.mock
 - External Packages: None

Notes:
 - Tests patch src.cli._request and src.cli._show to isolate I/O and assert header/info/warning call patterns.
 - Focus is on user-visible behavior and control flow rather than implementation details.

License:
 - Internal Use Only
"""

import unittest
from unittest.mock import patch

from src.cli import prompt as prompt


class TestStringValue(unittest.TestCase):
    """
    Unit tests for the `string_value` function in `prompt.py`.
    """

    def test_valid(self):
        """
        Should return whatever `request.string_input` returns.
        """
        # ARRANGE
        user_test = " hello "

        with (
            patch("builtins.input", return_value=user_test) as mock_input,
            patch("builtins.print"),
        ):
            # ACT
            result = prompt.string_value()

        # ASSERT
        with self.subTest("Value", Out=result, Exp=user_test):
            self.assertEqual(result, user_test)
        with self.subTest("Calls", Out=mock_input.call_count, Exp=1):
            self.assertEqual(mock_input.call_count, 1)

    def test_error(self):
        """
        Should raise RuntimeError if an unexpected exception occurs in the function.
        """
        # ARRANGE
        expected = RuntimeError.__name__

        with patch("builtins.input", side_effect=TypeError("boom")):
            try:
                # ACT
                prompt.string_value()
                result = "NoError"  # If nothing raised
            except Exception as e:
                result = e.__class__.__name__

        # ASSERT
        with self.subTest(Out=result, Exp=expected):
            self.assertEqual(result, expected)


class TestMenuSelection(unittest.TestCase):
    """
    Unit tests for the `menu_selection` function in `_prompt.py`.
    """

    def test_empty(self):
        """
        Should raise ValueError if menu is empty.
        """
        # ARRANGE
        menu_items = []

        # ACT
        with self.assertRaises(ValueError) as cm:
            prompt.menu_selection(menu_items)

        # ASSERT
        with self.subTest(Out=str(cm.exception), Exp=prompt._ERR_MENU_EMPTY):
            self.assertIn(prompt._ERR_MENU_EMPTY, str(cm.exception))

    def test_single(self):
        """
        Should immediately return 0 when menu has one item.
        """
        # ARRANGE
        menu_items = ["alpha"]

        # ACT
        result = prompt.menu_selection(menu_items)

        # ASSERT
        with self.subTest(Out=result, Exp=0):
            self.assertEqual(result, 0)

    def test_valid(self):
        """
        Should return the index chosen when input is valid.
        """
        # ARRANGE
        menu_items = ["alpha", "bravo", "charlie"]
        user_selection = 1
        with (
            patch("builtins.input", return_value=user_selection) as mock_input,
            patch("builtins.print"),
        ):
            # ACT
            result = prompt.menu_selection(menu_items, header_msg="Pick one")

        # ASSERT
        with self.subTest("Selection", Out=result, Exp=user_selection):
            self.assertEqual(result, user_selection)
        with self.subTest("Calls", Out=mock_input.call_count, Exp=1):
            self.assertEqual(mock_input.call_count, 1)

    def test_invalid(self):
        """
        Should warn on invalid input and reprompt until valid.
        """
        # ARRANGE
        menu_items = ["alpha", "bravo", "charlie"]
        invalid_index = 3
        valid_index = 1
        # IMPORTANT: simulate the sequence as strings
        user_sequence = [str(invalid_index), str(valid_index)]  # first invalid, then valid

        with (
            patch("builtins.input", side_effect=user_sequence) as mock_input,
            patch("builtins.print"),
        ):
            # ACT
            result = prompt.menu_selection(menu_items)

        # ASSERT
        with self.subTest("Selection", Out=result, Exp=valid_index):
            self.assertEqual(result, valid_index)
        with self.subTest("Calls", Out=mock_input.call_count, Exp=2):
            self.assertEqual(mock_input.call_count, 2)

    def test_unexpected_error(self):
        """
        Should raise Runtime Error if unexpected error is raised.
        """
        # ARRANGE
        menu_items = ["alpha", "bravo", "charlie"]
        expected = RuntimeError.__name__

        with(
            patch("builtins.input", side_effect=TimeoutError("slow")),
            patch("builtins.print"),
        ):
            try:
                # ACT
                prompt.menu_selection(menu_items)
                result = "NoError"  # If nothing raised
            except Exception as e:
                result = e.__class__.__name__

        # ASSERT
        with self.subTest(Out=result, Exp=expected):
            self.assertEqual(result, expected)


if __name__ == "__main__":
    unittest.main()
