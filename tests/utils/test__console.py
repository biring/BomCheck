"""
Unit tests for the `utils._console` module.

These tests validate the behavior of console input/output helpers to ensure consistency in CLI workflows.

Example Usage:
    # Run tests with unittest discovery:
    python -m unittest tests/test__console.py

Dependencies:
    - Python >= 3.9
    - Standard Library: unittest, unittest.mock

Notes:
    - Keeps tests isolated and non-interactive — no real stdin/stdout is used.
    - Designed to validate correctness without enforcing UX or retry logic.

License:
 - Internal Use Only
"""

import unittest
from unittest.mock import patch

# noinspection PyProtectedMember
import src.utils._console as console


class TestPromptStringInput(unittest.TestCase):
    """
    Unit tests for the `prompt_string_input` function.
    """

    def test_return(self):
        """
        Should return stripped user input.
        """
        # ARRANGE
        expected = "4 A 5"

        # Patch input() as called inside _console
        with patch("src.utils._console.input", return_value="  4 A 5  ") as mock_input, patch(
                "builtins.print") as mock_print:
            # ACT
            actual = console.prompt_string_input("data", "msg", "prompt> ")

            # ASSERT
            with self.subTest(Out=actual, Exp=expected):
                # Verify stripping worked
                self.assertEqual(actual, expected)
                # Verify the correct prompt string was passed
                mock_input.assert_called_once_with("prompt> ")

    def test_prints(self):
        """
        Should ensure context and advisory messages are printed.
        """
        # ARRANGE
        # N/A

        with patch("src.utils._console.input", return_value="test"), \
                patch("builtins.print") as mock_print:
            # ACT
            console.prompt_string_input("DATA", "MSG", "prompt> ")
            # ASSERT
            with self.subTest("Prints"):
                # Verify both context and advisory messages were printed
                mock_print.assert_any_call("DATA")
                mock_print.assert_any_call("MSG")


if __name__ == "__main__":
    unittest.main()
