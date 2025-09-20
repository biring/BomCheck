"""
Unit tests for the regex coercion engine (Rule, Result, apply_coerce).

This suite verifies:
 - Rules compile and apply in sequence
 - Substitutions mutate text and produce Log entries
 - No-change passes do not create logs
 - Result.empty() provides a clean baseline for fixtures

Example Usage:
    # Run this module:
    python -m unittest tests/rules/coerce/test__common.py

    # Discover and run all tests:
    python -m unittest discover -s tests

Dependencies:
    - Python >= 3.9
    - Standard Library: unittest, typing
    - External Packages: None

Notes:
    - Tests treat rules as pure transformations and assert both value_out and logs.
    - Emphasis is on public behavior, not internal regex implementation details.

License:
    - Internal Use Only
"""

import unittest
from typing import Match

# noinspection PyProtectedMember
from src.rules.coerce import _common as common  # Direct internal import — acceptable in tests


class TestCoerceText(unittest.TestCase):
    """
    Unit tests for the `coerce_text` function.
    """

    def test_valid(self):
        """
        Should apply a simple string replacement rule and record exactly one log entry.
        """
        # ARRANGE
        text = "abc-123-xyz"
        rules = [common.Rule(pattern=r"\d+", replacement="###", msg="mask digits")]
        expected_out = "abc-###-xyz"
        expected_logs = len(rules)

        # ACT
        result = common.apply_coerce(text, rules)

        # ASSERT
        with self.subTest(Field="value_in", Out=result.value_in, Exp=text):
            self.assertEqual(result.value_in, text)

        with self.subTest(Field="value_out", Out=result.value_out, Exp=expected_out):
            self.assertEqual(result.value_out, expected_out)

        with self.subTest(Field="log_count", Out=len(result.logs), Exp=expected_logs):
            self.assertEqual(len(result.logs), expected_logs)

        with self.subTest(Field="msg", Out=result.logs[0].description, Exp=rules[0].msg):
            self.assertEqual(result.logs[0].description, rules[0].msg)

    def test_callable(self):
        """
        Should support a callable replacement and log when at least one substitution occurs.
        """
        # ARRANGE
        text = "alpha beta gamma"

        def up_case_char(m: Match[str]) -> str:
            # Replace each matched vowel with its uppercase form
            return m.group(0).upper()

        rules = [common.Rule(pattern=r"[aeiou]", replacement=up_case_char, msg="uppercase vowels")]
        expected_out = "AlphA bEtA gAmmA"
        expected_logs = len(rules)

        # ACT
        result = common.apply_coerce(text, rules)

        # ASSERT
        with self.subTest(Field="value_in", Out=result.value_in, Exp=text):
            self.assertEqual(result.value_in, text)

        with self.subTest(Field="value_out", Out=result.value_out, Exp=expected_out):
            self.assertEqual(result.value_out, expected_out)

        with self.subTest(Field="log_count", Out=len(result.logs), Exp=expected_logs):
            self.assertEqual(len(result.logs), expected_logs)

        with self.subTest(Field="msg", Out=result.logs[0].description, Exp=rules[0].msg):
            self.assertEqual(result.logs[0].description, rules[0].msg)

    def test_no_change(self):
        """
        Should return the original text and an empty log when no rules match.
        """
        # ARRANGE
        text = "will not change"
        rules = [common.Rule(pattern=r"\d+", replacement="x", msg="digits masked")]
        expected_out = text
        expected_logs = 0

        # ACT
        result = common.apply_coerce(text, rules)

        # ASSERT
        with self.subTest(Field="value_in", Out=result.value_in, Exp=text):
            self.assertEqual(result.value_in, text)

        with self.subTest(Field="value_out", Out=result.value_out, Exp=expected_out):
            self.assertEqual(result.value_out, expected_out)

        with self.subTest(Field="log_count", Out=len(result.logs), Exp=expected_logs):
            self.assertEqual(len(result.logs), expected_logs)

    def test_multiple(self):
        """
        Should apply multiple rules sequentially and log only the rules that matched.
        """
        # ARRANGE
        text = "  id: 007  \nname: bond\t"
        rules = [
            # Trim leading/trailing whitespace lines (affects the overall string)
            common.Rule(pattern=r"^\s+|\s+$", replacement="", msg="trim ends"),
            # Collapse internal whitespace to single spaces
            common.Rule(pattern=r"[ \t]+", replacement=" ", msg="collapse spaces"),
            # Mask numbers
            common.Rule(pattern=r"\d+", replacement="<num>", msg="mask digits"),
            # Replace 'name:' label once
            common.Rule(pattern=r"\bname:", replacement="agent:", msg="rename label"),
            # A rule that won't match anymore (e.g., tabs already collapsed)
            common.Rule(pattern=r"\t", replacement=" ", msg="tabs to spaces"),
        ]
        # Work through the expected transformation step-by-step:
        # 1) trim ends -> "id: 007  \nname: bond"
        # 2) collapse spaces -> "id: 007 \nname: bond"
        # 3) mask digits -> "id: <num> \nname: bond"
        # 4) rename label -> "id: <num> \nagent: bond"
        # 5) tabs to spaces -> no-op
        expected_out = "id: <num> \nagent: bond"
        # 4 rules should have matched (last one no-ops)
        expected_logs = 4

        # ACT
        result = common.apply_coerce(text, rules)

        # ASSERT
        with self.subTest(Field="value_out", Out=result.value_out, Exp=expected_out):
            self.assertEqual(result.value_out, expected_out)

        with self.subTest(Field="log_count", Out=len(result.logs), Exp=expected_logs):
            self.assertEqual(len(result.logs), expected_logs)

        # Verify that messages correspond to matched rules in order
        matched_msgs = [entry.description for entry in result.logs]
        expected_msgs = ["trim ends", "collapse spaces", "mask digits", "rename label"]
        with self.subTest(Field="log_msgs", Out=matched_msgs, Exp=expected_msgs):
            self.assertEqual(matched_msgs, expected_msgs)


class TestShow(unittest.TestCase):
    """
    Unit tests for the `_show` helper.

    Ensures control characters are made visible (`\n` -> "\\n", `\t` -> "\\t")
    and that long strings are truncated with a single ellipsis character
    when exceeding `max_len`.
    """

    def test_valid(self):
        """
        Should replace newline and tab with visible escape sequences.
        """
        # ARRANGE
        text = "line1\nline2\tend"
        expected = r"line1\nline2\tend"  # literal backslashes

        # ACT
        result = common._show(text)

        # ASSERT
        with self.subTest(Field="visible", Out=result, Exp=expected):
            self.assertEqual(result, expected)

    def test_small(self):
        """
        Should return the original (visibility-adjusted) text when length <= max_len (default 32).
        """
        # ARRANGE
        text = "short_text"
        expected = "short_text"

        # ACT
        result = common._show(text)  # default max_len=32

        # ASSERT
        with self.subTest(Field="no_truncate", Out=result, Exp=expected):
            self.assertEqual(result, expected)

    def test_truncates(self):
        """
        Should truncate to max_len-1 characters and append a single ellipsis '…' when length > max_len.
        """
        # ARRANGE
        text = "abcdefghijklmnopqrstuvwxyz0123456789"  # 36 chars
        max_len = 10
        # Expect first 9 characters + '…'
        expected = "abcdefghi" + "…"

        # ACT
        result = common._show(text, max_len=max_len)

        # ASSERT
        with self.subTest(Field="truncate", Out=result, Exp=expected):
            self.assertEqual(result, expected)
        with self.subTest(Field="length_check", Out=len(result), Exp=max_len):
            self.assertEqual(len(result), max_len)

    def test_truncation_counts_after_visibility_expansion(self):
        """
        Should apply truncation logic to the visibility-adjusted string (i.e., after '\\n' and '\\t' expansion increases length).
        """
        # ARRANGE
        # Input of length 4 becomes length 5 after visibility.
        text = "A\nBC"
        # max_len forces truncation after visibility; max_len=4 means keep 4 chars + '…'
        max_len = 4
        visible = r"A\nB"  # "A\\nB"
        expected = visible[: max_len - 1] + "…"

        # ACT
        result = common._show(text, max_len=max_len)

        # ASSERT
        with self.subTest(Field="truncate_visible", Out=result, Exp=expected):
            self.assertEqual(result, expected)

    def test_max_size(self):
        """
        Should not truncate when visibility-adjusted length equals max_len - 1 exactly.
        """
        # ARRANGE
        # Visible version has exactly 8 characters: "A\\nB\\tCD" -> A(1) \ (2) n(3) B(4) \ (5) t(6) C(7) D(8)
        text = "A\nB\tCD"
        max_len = 8
        expected = r"A\nB\tCD"

        # ACT
        result = common._show(text, max_len=max_len)

        # ASSERT
        with self.subTest(Field="exact_limit", Out=result, Exp=expected):
            self.assertEqual(result, expected)
        with self.subTest(Field="length_check", Out=len(result), Exp=max_len):
            self.assertEqual(len(result), max_len)

    def test_small_length(self):
        """
        Should handle very small max_len values (e.g., 1 or 2) by truncating to max_len-1 + '…' when needed.
        """
        # ARRANGE
        cases = [
            # text, max_len, expected
            ("abc", 1, "…"),  # keep 0 chars + '…'
            ("abc", 2, "a" + "…"),  # keep 1 char + '…'
        ]

        # ACT & ASSERT
        for text, max_len, expected in cases:
            result = common._show(text, max_len=max_len)
            with self.subTest(Field=f"max_len={max_len}", Out=result, Exp=expected):
                self.assertEqual(result, expected)


if __name__ == "__main__":
    unittest.main()
