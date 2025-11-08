"""
Unit tests for helper utilities in the correction package.

Example Usage:
    # Preferred usage via project-root invocation:
    python -m unittest tests/correction/test__helper.py

    # Direct discovery (runs all tests, including this module):
    python -m unittest discover -s tests

Dependencies:
    - Python >= 3.10
    - Standard Library: unittest, unittest.mock
    - Project: src.cli.interfaces (patched)

Notes:
    - Tests simulate CLI calls with patched prompt, info, and warning functions to count invocations.
    - prompt_until_valid tests cover single-pass, one-prompt, and multi-prompt scenarios for validator return logic.
    - Floating-point equality tests explicitly target edge rounding and epsilon boundaries.

License:
    - Internal Use Only
"""

import unittest
from unittest.mock import patch

from src.cli import interfaces as cli

# noinspection PyProtectedMember
import src.correction._helper as helper  # Direct internal import — acceptable in tests


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


class TestGenerateLogEntry(unittest.TestCase):
    """
    Unit tests for the `generate_log_entry` function.
    """

    def test_msg(self):
        """
        Should return message that includes all expected fields (field, before, after, reason) when values differ.
        """
        # ARRANGE
        field = "Test"
        before = "23"
        after = "25"
        reason = "Manual update."

        # ACT
        log = helper.generate_log_entry(field, before, after, reason)

        with self.subTest("Log contains", Out=log, Exp=field):
            self.assertIn(field, log)
        with self.subTest("Log contains", Out=log, Exp=before):
            self.assertIn(before, log)
        with self.subTest("Log contains", Out=log, Exp=after):
            self.assertIn(after, log)
        with self.subTest("Log contains", Out=log, Exp=reason):
            self.assertIn(reason, log)

    def test_no_msg(self):
        """
        Should return an empty string when before and after values are identical.
        """
        # ARRANGE
        field = "Test"
        before = "23"
        after = before
        reason = "Manual update."

        # ACT
        log = helper.generate_log_entry(field, before, after, reason)

        with self.subTest("Empty Log", Out=log):
            self.assertEqual(log, "")


class TestPromptUntilValid(unittest.TestCase):
    """
    Unit tests for the `prompt_until_valid` function.
    """

    data = "Test Data"
    expected_out = "Beta"
    field = "Test"

    def no_return_when_beta(self, value):
        if value == self.expected_out:
            return ""
        else:
            return "Prompt again."

    def asset_value_out(self, value_in: str, value_out: str, expected_out: str):
        with self.subTest("Value", In=value_in, Out=value_out, Exp=expected_out):
            self.assertEqual(value_out, self.expected_out)

    def asset_info_call_count(self, actual_info_calls: int, expected_info_calls: int):
        with self.subTest("Info call count", Out=actual_info_calls, Exp=expected_info_calls):
            self.assertEqual(actual_info_calls, expected_info_calls)

    def asset_warning_call_count(self, actual_warning_calls: int, expected_warning_calls: int):
        with self.subTest("Warning call count", Out=actual_warning_calls, Exp=expected_warning_calls):
            self.assertEqual(actual_warning_calls, expected_warning_calls)

    def asset_prompt_call_count(self, actual_prompt_calls: int, expected_prompt_calls: int):
        with self.subTest("Prompt call count", Out=actual_prompt_calls, Exp=expected_prompt_calls):
            self.assertEqual(actual_prompt_calls, expected_prompt_calls)

    def test_no_prompt(self):
        """
        Should not prompt the user when the initial value passes validation.
        """

        # ARRANGE
        fn = self.no_return_when_beta
        value_in = self.expected_out
        expected_prompt_calls = 0
        expected_info_calls = 0
        expected_warning_calls = 0

        # ACT
        with (
            patch.object(cli, "prompt_for_string_value", return_value=self.expected_out) as p_prompt,
            patch.object(cli, "show_info") as p_info,
            patch.object(cli, "show_warning") as p_warning,
        ):
            value_out = helper.prompt_until_valid(data=self.data, fn=fn, value=value_in, field=self.field)
            actual_prompt_calls = p_prompt.call_count
            actual_info_calls = p_info.call_count
            actual_warning_calls = p_warning.call_count

        # ASSERT
        self.asset_value_out(value_in, value_out, self.expected_out)
        self.asset_info_call_count(actual_info_calls, expected_info_calls)
        self.asset_warning_call_count(actual_warning_calls, expected_warning_calls)
        self.asset_prompt_call_count(actual_prompt_calls, expected_prompt_calls)

    def test_one_prompt(self):
        """
        Should prompt once and return when the user provides a valid corrected value.
        """

        # ARRANGE
        fn = self.no_return_when_beta
        value_in = "alpha"
        expected_prompt_calls = 1
        expected_info_calls = 1
        expected_warning_calls = 1

        # ACT
        with (
            patch.object(cli, "prompt_for_string_value", return_value=self.expected_out) as p_prompt,
            patch.object(cli, "show_info") as p_info,
            patch.object(cli, "show_warning") as p_warning,
        ):
            value_out = helper.prompt_until_valid(data=self.data, fn=fn, value=value_in, field=self.field)
            actual_prompt_calls = p_prompt.call_count
            actual_info_calls = p_info.call_count
            actual_warning_calls = p_warning.call_count

        # ASSERT
        self.asset_value_out(value_in, value_out, self.expected_out)
        self.asset_info_call_count(actual_info_calls, expected_info_calls)
        self.asset_warning_call_count(actual_warning_calls, expected_warning_calls)
        self.asset_prompt_call_count(actual_prompt_calls, expected_prompt_calls)

    def test_multiple_prompt(self):
        """
        Should loop and prompt multiple times until validator returns empty string.
        """

        # ARRANGE
        fn = self.no_return_when_beta
        value_in = "alpha"
        user_inputs = ["Hello", "try again", self.expected_out]
        expected_prompt_calls = 3
        expected_info_calls = 1
        expected_warning_calls = 3

        # ACT
        with (
            patch.object(cli, "prompt_for_string_value", side_effect=user_inputs) as p_prompt,
            patch.object(cli, "show_info") as p_info,
            patch.object(cli, "show_warning") as p_warning,
        ):
            value_out = helper.prompt_until_valid(data=self.data, fn=fn, value=value_in, field=self.field)
            actual_prompt_calls = p_prompt.call_count
            actual_info_calls = p_info.call_count
            actual_warning_calls = p_warning.call_count

        # ASSERT
        self.asset_value_out(value_in, value_out, self.expected_out)
        self.asset_info_call_count(actual_info_calls, expected_info_calls)
        self.asset_warning_call_count(actual_warning_calls, expected_warning_calls)
        self.asset_prompt_call_count(actual_prompt_calls, expected_prompt_calls)


class TestLevenshteinMatch(unittest.TestCase):
    """
    Unit tests for the `levenshtein_match` function.
    """

    def test_best_match(self):
        """
        Should return the closest match and its ratio when above the given threshold.
        """
        # ARRANGE
        test_string = "X1 Capacitor"
        reference_strings = ("Resistor", "Capacitor", "Inductor")
        ratio_threshold = 0.1
        expected_match = "Capacitor"

        # ACT
        match, ratio = helper.levenshtein_match(test_string, reference_strings, ratio_threshold)

        # ASSERT
        with self.subTest(Out=match, Exp=expected_match):
            self.assertEqual(match, expected_match)
        with self.subTest("Ratio above threshold", Out=ratio, Exp=True):
            self.assertGreaterEqual(ratio, ratio_threshold)

    def test_no_match(self):
        """
        Should return ('', 0.0) when no reference exceeds the threshold ratio.
        """
        # ARRANGE
        test_string = "Capacitor"
        reference_strings = ("Resistor", "Inductor")
        ratio_threshold = 0.9
        expected = ("", 0.0)

        # ACT
        result = helper.levenshtein_match(test_string, reference_strings, ratio_threshold)

        # ASSERT
        with self.subTest(Out=result, Exp=expected):
            self.assertEqual(result, expected)

    def test_exact_match(self):
        """
        Should return (same_string, 1.0) for exact matches.
        """
        # ARRANGE
        test_string = "Diode"
        reference_strings = ("Diode", "Resistor")
        ratio_threshold = 0.5
        expected = ("Diode", 1.0)

        # ACT
        result = helper.levenshtein_match(test_string, reference_strings, ratio_threshold)

        # ASSERT
        with self.subTest(Out=result, Exp=expected):
            self.assertEqual(result, expected)

    def test_empty_reference(self):
        """
        Should return ('', 0.0) when reference list is empty.
        """
        # ARRANGE
        test_string = "Capacitor"
        reference_strings = ()
        ratio_threshold = 0.5
        expected = ("", 0.0)

        # ACT
        result = helper.levenshtein_match(test_string, reference_strings, ratio_threshold)

        # ASSERT
        with self.subTest(Out=result, Exp=expected):
            self.assertEqual(result, expected)


class TestJaccardMatch(unittest.TestCase):
    """
    Unit tests for the `jaccard_match` function.
    """

    def test_best_match(self):
        """
        Should return the best matching string and similarity score above the threshold.
        """
        # ARRANGE
        test_string = "X1 Capacitor"
        reference_strings = ("Resistor", "Capacitator", "Inductor")
        similarity_threshold = 0.1
        expected_match = "Capacitator"

        # ACT
        match, similarity = helper.jaccard_match(test_string, reference_strings, similarity_threshold)

        # ASSERT
        with self.subTest(Out=match, Exp=expected_match):
            self.assertEqual(match, expected_match)
        with self.subTest("Similarity above threshold", Out=similarity, Exp=True):
            self.assertGreaterEqual(similarity, similarity_threshold)

    def test_no_match(self):
        """
        Should return ('', 0.0) when no reference meets the similarity threshold.
        """
        # ARRANGE
        test_string = "Resistor"
        reference_strings = ("Capacitor", "Inductor")
        similarity_threshold = 0.9
        expected = ("", 0.0)

        # ACT
        result = helper.jaccard_match(test_string, reference_strings, similarity_threshold)

        # ASSERT
        with self.subTest(Out=result, Exp=expected):
            self.assertEqual(result, expected)

    def test_exact_match(self):
        """
        Should return (same_string, 1.0) when test and reference strings are identical.
        """
        # ARRANGE
        test_string = "Connector"
        reference_strings = ("Connector", "Transistor")
        similarity_threshold = 0.5
        expected = ("Connector", 1.0)

        # ACT
        result = helper.jaccard_match(test_string, reference_strings, similarity_threshold)

        # ASSERT
        with self.subTest(Out=result, Exp=expected):
            self.assertEqual(result, expected)

    def test_empty_reference(self):
        """
        Should return ('', 0.0) when reference list is empty.
        """
        # ARRANGE
        test_string = "Capacitor"
        reference_strings = ()
        similarity_threshold = 0.5
        expected = ("", 0.0)

        # ACT
        result = helper.jaccard_match(test_string, reference_strings, similarity_threshold)

        # ASSERT
        with self.subTest(Out=result, Exp=expected):
            self.assertEqual(result, expected)


if __name__ == "__main__":
    unittest.main()
