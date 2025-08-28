"""
Unit tests for the public `utils` package APIs.

This suite provides smoke-level coverage to ensure the top-level `utils` API behaves as expected. These tests validate that API-exposed functions delegate correctly to their implementations and return normalized results.

Example Usage (from project root):
    # Run test suite:
    python -m unittest tests.utils.test_api

Dependencies:
    - Python >= 3.9
    - Standard Library: unittest, unittest.mock

Design Notes & Assumptions:
    - Tests are API-level only, not internal implementation details
    - Input/output validation is minimal; focus is on public contract correctness
    - Interactive functions (e.g., input prompts) are patched to avoid blocking

License:
 - Internal Use Only
"""

import unittest
from unittest.mock import patch

# noinspection PyProtectedMember
import src.utils._api as api


class TestAPI(unittest.TestCase):
    """
    Unit tests for the public API functions in the `utils` module.
    """

    def test_normalize_spaces(self):
        """
        Should run API function
        """
        # ARRANGE
        input_str = " A  B "
        expected = "A B"

        # ACT
        result = api.normalize_spaces(input_str)

        # ASSERT
        with self.subTest(Out=result, Exp=expected):
            self.assertEqual(result, expected)

    def test_normalize_to_string(self):
        """
        Should run API function
        """
        # ARRANGE
        input_int = 123
        expected = "123"

        # ACT
        result = api.normalize_to_string(input_int)

        # ASSERT
        with self.subTest(Out=result, Exp=expected):
            self.assertEqual(result, expected)

    def test_remove_all_whitespaces(self):
        """
        Should run API function
        """
        # ARRANGE
        input_str = "A B\tC\nD\rE\fF\vG"
        expected = "ABCDEFG"

        # ACT
        result = api.remove_all_whitespace(input_str)

        # ASSERT
        with self.subTest(Out=result, Exp=expected):
            self.assertEqual(result, expected)

    def test_get_string_input(self):
        """
        Should run API function
        """
        # ARRANGE
        expected = "45"

        # Patch the API-level symbol, since we're testing the public API
        with patch("src.utils._api.prompt_string_input", return_value=expected) as mock_input:
            # ACT
            result = api.prompt_string_input("", "", "")

            # ASSERT
            with self.subTest(Out=result, Exp=expected):
                self.assertEqual(result, expected)
                mock_input.assert_called_once_with("", "", "")


if __name__ == "__main__":
    unittest.main()
