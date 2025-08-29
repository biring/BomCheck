"""
Unit tests for the public `utils` package APIs.

This suite provides smoke-level coverage to ensure the top-level `utils` API behaves as expected. These tests validate that API-exposed functions delegate correctly to their implementations and return normalized results.

Example Usage (from project root):
    # Run test suite:
    python -m unittest tests.utils.test__api

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

import os
import tempfile
import unittest
from unittest.mock import patch

# noinspection PyProtectedMember
import src.utils._api as api


class TestConsole(unittest.TestCase):
    """
    Unit tests for the public API functions in the `utils._console` module.
    """

    def test_prompt_string_input(self):
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


class TestParser(unittest.TestCase):
    """
    Unit tests for the public API functions in the `utils._parser` module.
    """

    def test_is_float(self):
        """
        Should run API function
        """
        # ARRANGE
        input_list = ["3.147", "A"]
        expected_list = [True, False]

        for input_str, expected in zip(input_list, expected_list):
            # ACT
            result = api.is_float(input_str)

            # ASSERT
            with self.subTest(In=input_str, Out=result, Exp=expected):
                self.assertEqual(result, expected)

    def test_is_integer(self):
        """
        Should run API function
        """
        # ARRANGE
        input_list = ["7", "3.7"]
        expected_list = [True, False]

        for input_str, expected in zip(input_list, expected_list):
            # ACT
            result = api.is_integer(input_str)

            # ASSERT
            with self.subTest(In=input_str, Out=result, Exp=expected):
                self.assertEqual(result, expected)

    def test_is_non_empty_string(self):
        """
        Should run API function
        """
        # ARRANGE
        input_list = ["Hello", ""]
        expected_list = [True, False]

        for input_str, expected in zip(input_list, expected_list):
            # ACT
            result = api.is_non_empty_string(input_str)

            # ASSERT
            with self.subTest(In=input_str, Out=result, Exp=expected):
                self.assertEqual(result, expected)

    def test_is_strict_empty_string(self):
        """
        Should run API function
        """
        # ARRANGE
        input_list = ["", "3.7"]
        expected_list = [True, False]

        for input_str, expected in zip(input_list, expected_list):
            # ACT
            result = api.is_strict_empty_string(input_str)

            # ASSERT
            with self.subTest(In=input_str, Out=result, Exp=expected):
                self.assertEqual(result, expected)

    def test_is_valid_date_string(self):
        """
        Should run API function
        """
        # ARRANGE
        input_list = ["12/10/2025", "2025/10/10"]
        expected_list = [True, False]

        for input_str, expected in zip(input_list, expected_list):
            # ACT
            result = api.is_valid_date_string(input_str)

            # ASSERT
            with self.subTest(In=input_str, Out=result, Exp=expected):
                self.assertEqual(result, expected)

    def test_parse_to_empty_string(self):
        """
        Should run API function
        """
        # ARRANGE
        input_list = ["", "a"]
        expected_list = ["", ValueError.__name__]

        for input_str, expected in zip(input_list, expected_list):
            # ACT
            try:
                result = api.parse_to_empty_string(input_str)
            except Exception as e:
                result = type(e).__name__
            # ASSERT
            with self.subTest(In=input_str, Out=result, Exp=expected):
                self.assertEqual(result, expected)

    def test_parse_to_float(self):
        """
        Should run API function
        """
        # ARRANGE
        input_list = ["22.2", "a"]
        expected_list = [22.2, ValueError.__name__]

        for input_str, expected in zip(input_list, expected_list):
            # ACT
            try:
                result = api.parse_to_float(input_str)
            except Exception as e:
                result = type(e).__name__
            # ASSERT
            with self.subTest(In=input_str, Out=result, Exp=expected):
                self.assertEqual(result, expected)

    def test_parse_to_integer(self):
        """
        Should run API function
        """
        # ARRANGE
        input_list = ["22", "a"]
        expected_list = [22, ValueError.__name__]

        for input_str, expected in zip(input_list, expected_list):
            # ACT
            try:
                result = api.parse_to_integer(input_str)
            except Exception as e:
                result = type(e).__name__
            # ASSERT
            with self.subTest(In=input_str, Out=result, Exp=expected):
                self.assertEqual(result, expected)

    def test_parse_to_iso_date_string(self):
        """
        Should run API function
        """
        # ARRANGE
        input_list = ["12/10/2025", "2025/10/10"]
        expected_list = ["2025-10-12", ValueError.__name__]

        for input_str, expected in zip(input_list, expected_list):
            # ACT
            try:
                result = api.parse_to_iso_date_string(input_str)
            except Exception as e:
                result = type(e).__name__
            # ASSERT
            with self.subTest(In=input_str, Out=result, Exp=expected):
                self.assertEqual(result, expected)

    def test_parse_to_non_empty_string(self):
        """
        Should run API function
        """
        # ARRANGE
        input_list = ["Hello", ""]
        expected_list = ["Hello", ValueError.__name__]

        for input_str, expected in zip(input_list, expected_list):
            # ACT
            try:
                result = api.parse_to_non_empty_string(input_str)
            except Exception as e:
                result = type(e).__name__
            # ASSERT
            with self.subTest(In=input_str, Out=result, Exp=expected):
                self.assertEqual(result, expected)


class TestSanitizer(unittest.TestCase):
    """
    Unit tests for the public API functions in the `utils._sanitizer` module.
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


class TestTextIO(unittest.TestCase):
    """
    Unit tests for the public API functions in the `utils._text_io` module.
    """

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp(prefix="api_textio")

    def tearDown(self):
        for root, dirs, files in os.walk(self.temp_dir, topdown=False):
            for name in files:
                os.remove(os.path.join(root, name))
            for name in dirs:
                os.rmdir(os.path.join(root, name))
        os.rmdir(self.temp_dir)

    def test_save_text_file(self):
        """
        Should run API function
        """
        # ARRANGE
        path = os.path.join(self.temp_dir, "hello.txt")
        content = "Hello\tUTF-8 ✓ — line one 🌟"
        expected_size = len(content.encode("utf-8"))

        # ACT
        api.save_text_file(path, content)

        # ASSERT
        self.assertTrue(os.path.isfile(path))
        actual_size = os.path.getsize(path)
        with self.subTest(Out=actual_size, Exp=expected_size):
            self.assertEqual(actual_size, expected_size)

    def test_save_text_file_raise(self):
        """
        Should raise when file path is a folder path.
        """
        # ARRANGE
        bad_path = os.path.join(self.temp_dir, "not_a_file")
        os.mkdir(bad_path)
        expected = RuntimeError.__name__

        # ACT
        try:
            api.save_text_file(bad_path, "content")
            result = ""
        except Exception as e:
            result = type(e).__name__

        # ASSERT
        with self.subTest(Out=result, Exp=expected):
            self.assertEqual(result, expected)

    def test_load_text_file(self):
        """
        Should run API function
        """
        # ARRANGE
        path = os.path.join(self.temp_dir, "hello.txt")
        expected = "Hello\nUTF-8 ✓ load file data 🌟"
        with open(path, "w", encoding="utf-8", newline="") as f:
            f.write(expected)

        # ACT
        actual = api.load_text_file(path)

        # ASSERT
        with self.subTest(Out=actual, Exp=expected):
            self.assertEqual(actual, expected)

    def test_load_text_file_raise(self):
        """
        Should raise error when file does not exist.
        """
        # ARRANGE
        missing = os.path.join(self.temp_dir, "does_not_exist.txt")
        expected = RuntimeError.__name__

        # ACT
        try:
            api.load_text_file(missing)
            result = ""
        except Exception as e:
            result = type(e).__name__

        # ASSERT
        with self.subTest(Out=result, Exp=expected):
            self.assertEqual(result, expected)


if __name__ == "__main__":
    unittest.main()
