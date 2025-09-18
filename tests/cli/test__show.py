"""
Unit tests for colorized CLI output helpers.

This module verifies that each function:
    - Prints the expected ANSI-colored text for error, warning, success, info, log, and header
    - Returns a correctly formatted ANSI string for prompts
    - Uses colorama consistently across all helpers

Example Usage:
    # Preferred usage via project-root invocation:
    python -m unittest tests/cli/test__show.py

    # Direct discovery (runs all tests, including this module):
    python -m unittest discover -s tests

Dependencies:
    - Python >= 3.9
    - Standard Library: unittest, unittest.mock
    - External Packages: colorama

Notes:
    - Printing functions are tested by patching `builtins.print` and asserting call arguments.
    - The `prompt` function is tested by direct string comparison instead of print interception.
    - Tests ensure no extra formatting leaks into outputs and auto reset behavior is respected.

License:
    - Internal Use Only
"""

import unittest
from unittest.mock import patch

from colorama import Fore, Style

# noinspection PyProtectedMember
from src.cli import _show as show


class TestShow(unittest.TestCase):
    """
    Unit tests for colorized printing helpers in `_show`:
    """

    def test_prints_colored_message(self):
        """
        Should print the message once with the expected Colorama prefix and a trailing reset.
        """
        # ARRANGE
        msg = "Hello"
        cases = [
            (show.error, f"{Fore.RED}"),
            (show.warning, f"{Fore.YELLOW}"),
            (show.info, f"{Style.RESET_ALL}"),  # info prefixes with reset (no Fore color)
            (show.header, f"{Fore.LIGHTWHITE_EX}"),
            (show.log, f"{Fore.LIGHTBLACK_EX}"),
            (show.success, f"{Fore.GREEN}"),
        ]

        with patch("builtins.print") as mock_print:
            for fn, prefix in cases:
                mock_print.reset_mock()
                expected = f"{prefix}{msg}{Style.RESET_ALL}"

                # ACT
                fn(msg)

                # ASSERT
                with self.subTest(Behavior="Call count", Fn=fn.__name__,
                                  Out=mock_print.call_count, Exp=1):
                    self.assertEqual(mock_print.call_count, 1)

                # Extract the printed string (first positional arg of first call)
                actual = mock_print.call_args[0][0] if mock_print.call_args else ""
                with self.subTest(Fn=fn.__name__, Out=actual, Exp=expected):
                    self.assertEqual(actual, expected)


class TestPrompt(unittest.TestCase):
    """
    Unit tests for `prompt` helper in `_show`.
    """

    def test_returns_colored_prompt(self):
        """
        Should return the prompt wrapped in blue with a trailing reset.
        """
        # ARRANGE
        msg = "Enter value: "
        expected = f"{Fore.BLUE}{msg}{Style.RESET_ALL}"

        # ACT
        result = show.prompt(msg)

        # ASSERT
        with self.subTest(Out=result, Exp=expected):
            self.assertEqual(result, expected)


if __name__ == "__main__":
    unittest.main()
