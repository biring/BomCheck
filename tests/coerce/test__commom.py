"""
Unit tests for the regex coercion engine (Rule, Result, apply_coerce).

Example Usage:
    # Run this module:
    python -m unittest tests/coerce/test__common.py

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
from src.coerce import _common as common  # Direct internal import — acceptable in tests


class TestApplyCoerce(unittest.TestCase):
    """
    Unit tests for the `apply_coerce` function.
    """

    def test_pattern_change(self):
        """
        Should apply a simple string replacement rule and record exactly one log entry.
        """
        # ARRANGE
        text = "abc-123-xyz"
        rules = [common.Rule(pattern=r"\d+", replacement="###", msg="mask digits")]
        expected_out = "abc-###-xyz"
        expected_logs = 1

        # ACT
        result = common.apply_coerce(text, rules)

        # ASSERT
        with self.subTest("Value In", Out=result.value_in, Exp=text):
            self.assertEqual(result.value_in, text)

        with self.subTest("Value Out", Out=result.value_out, Exp=expected_out):
            self.assertEqual(result.value_out, expected_out)

        with self.subTest("Log Count", Out=len(result.logs), Exp=expected_logs):
            self.assertEqual(len(result.logs), expected_logs)

        with self.subTest("Msg", Out=result.logs[0].description, Exp=rules[0].msg):
            self.assertEqual(result.logs[0].description, rules[0].msg)

    def test_pattern_no_change(self):
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
        with self.subTest("Value In", Out=result.value_in, Exp=text):
            self.assertEqual(result.value_in, text)

        with self.subTest("Value Out", Out=result.value_out, Exp=expected_out):
            self.assertEqual(result.value_out, expected_out)

        with self.subTest("log Count", Out=len(result.logs), Exp=expected_logs):
            self.assertEqual(len(result.logs), expected_logs)

    def test_pattern_empty(self):
        """
        Should return the original empty text and an empty log when no rules match.
        """
        # ARRANGE
        text = ""
        rules = [common.Rule(pattern=r"\d+", replacement="x", msg="digits masked")]
        expected_out = text
        expected_logs = 0

        # ACT
        result = common.apply_coerce(text, rules)

        # ASSERT
        with self.subTest("Value In", Out=result.value_in, Exp=text):
            self.assertEqual(result.value_in, text)

        with self.subTest("Value Out", Out=result.value_out, Exp=expected_out):
            self.assertEqual(result.value_out, expected_out)

        with self.subTest("log Count", Out=len(result.logs), Exp=expected_logs):
            self.assertEqual(len(result.logs), expected_logs)

    def test_callable_change(self):
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
        with self.subTest("Value In", Out=result.value_in, Exp=text):
            self.assertEqual(result.value_in, text)

        with self.subTest("Value Out", Out=result.value_out, Exp=expected_out):
            self.assertEqual(result.value_out, expected_out)

        with self.subTest("Log Count", Out=len(result.logs), Exp=expected_logs):
            self.assertEqual(len(result.logs), expected_logs)

        with self.subTest("Msg", Out=result.logs[0].description, Exp=rules[0].msg):
            self.assertEqual(result.logs[0].description, rules[0].msg)

    def test_callable_no_change(self):
        """
        Should return the original text and an empty log when no substitution occurs.
        """
        # ARRANGE
        text = "1234567890"

        def up_case_char(m: Match[str]) -> str:
            # Replace each matched vowel with its uppercase form
            return m.group(0).upper()

        rules = [common.Rule(pattern=r"[aeiou]", replacement=up_case_char, msg="uppercase vowels")]
        expected_out = "1234567890"
        expected_logs = 0

        # ACT
        result = common.apply_coerce(text, rules)

        # ASSERT
        with self.subTest("Value In", Out=result.value_in, Exp=text):
            self.assertEqual(result.value_in, text)

        with self.subTest("Value Out", Out=result.value_out, Exp=expected_out):
            self.assertEqual(result.value_out, expected_out)

        with self.subTest("Log Count", Out=len(result.logs), Exp=expected_logs):
            self.assertEqual(len(result.logs), expected_logs)

    def test_callable_empty(self):
        """
        Should return the original empty text and an empty log when no substitution occurs.
        """
        # ARRANGE
        text = ""

        def up_case_char(m: Match[str]) -> str:
            # Replace each matched vowel with its uppercase form
            return m.group(0).upper()

        rules = [common.Rule(pattern=r"[aeiou]", replacement=up_case_char, msg="uppercase vowels")]
        expected_out = ""
        expected_logs = 0

        # ACT
        result = common.apply_coerce(text, rules)

        # ASSERT
        with self.subTest("Value In", Out=result.value_in, Exp=text):
            self.assertEqual(result.value_in, text)

        with self.subTest("Value Out", Out=result.value_out, Exp=expected_out):
            self.assertEqual(result.value_out, expected_out)

        with self.subTest("Log Count", Out=len(result.logs), Exp=expected_logs):
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
        with self.subTest("Value Out", Out=result.value_out, Exp=expected_out):
            self.assertEqual(result.value_out, expected_out)

        with self.subTest("Log Count", Out=len(result.logs), Exp=expected_logs):
            self.assertEqual(len(result.logs), expected_logs)

        # Verify that messages correspond to matched rules in order
        matched_msgs = [entry.description for entry in result.logs]
        expected_msgs = [rules[0].msg, rules[1].msg, rules[2].msg, rules[3].msg]
        with self.subTest("Messages", Out=matched_msgs, Exp=expected_msgs):
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
        with self.subTest("Visible", Out=result, Exp=expected):
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
        with self.subTest("No Truncate", Out=result, Exp=expected):
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
        with self.subTest("Truncate", Out=result, Exp=expected):
            self.assertEqual(result, expected)
        with self.subTest("Length Check", Out=len(result), Exp=max_len):
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
        with self.subTest("Truncate Visible", Out=result, Exp=expected):
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
        with self.subTest("Exact Limit", Out=result, Exp=expected):
            self.assertEqual(result, expected)
        with self.subTest("length Check", Out=len(result), Exp=max_len):
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
            with self.subTest(f"Max Length = {max_len}", Out=result, Exp=expected):
                self.assertEqual(result, expected)


class TestRenderMessages(unittest.TestCase):
    """
    Unit tests for render_messages(result, field, template=...).
    """

    def test_empty(self):
        """
        Should return an empty tuple when value_in == value_out (no effective change).
        """
        # ARRANGE
        text = "no digits here"
        rules = [common.Rule(pattern=r"\d+", replacement="x", msg="digits masked")]
        res = common.apply_coerce(text, rules)

        # ACT
        messages = common.render_coerce_log(res, field="TOTAL_COST")

        # ASSERT
        with self.subTest("Log msg", out=messages, exp=()):
            self.assertEqual(messages, (), msg="Expected empty messages")

    def test_render(self):
        """
        Should produce one formatted line per matched rule, in order.
        """
        # ARRANGE
        text = "cost: 123"
        rules = [
            common.Rule(pattern=r"[:]", replacement="=", msg="Colon changed to equal. "),
            common.Rule(pattern=r"\d+", replacement="###", msg="Digits masked with ###. "),
        ]
        res = common.apply_coerce(text, rules)

        # ACT
        messages = common.render_coerce_log(res, field="Total cost")

        # ASSERT
        with self.subTest("Log count", out=len(res.logs), exp="2"):
            self.assertEqual(len(res.logs), 2, "Expected two log entries")

        for message, rule in zip(messages, rules):
            with self.subTest("Message contains", out=message, exp=rule.msg):
                self.assertIn(rule.msg, message, f"Expected to contain {rule.msg}")


class TestResult(unittest.TestCase):
    """
    Unit tests for the `Result` dataclass.
    """

    def test_defaults(self):
        """
        Should create Result with empty defaults.
        """
        # ARRANGE
        r1 = common.Result()  # default construction

        # ACT
        # not applicable. default

        # ASSERT
        with self.subTest(Field="attr_name", Out=r1.attr_name, Exp=""):
            self.assertEqual(r1.attr_name, "")
        with self.subTest(Field="value_in", Out=r1.value_in, Exp=""):
            self.assertEqual(r1.value_in, "")
        with self.subTest(Field="value_out", Out=r1.value_out, Exp=""):
            self.assertEqual(r1.value_out, "")
        with self.subTest(Field="logs_empty", Out=len(r1.logs), Exp=0):
            self.assertEqual(len(r1.logs), 0)

    def test_independent_logs(self):
        """
        Should not share log lists between instances.
        """
        # ARRANGE
        r1 = common.Result()  # default construction
        r2 = common.Result()  # separate instance

        # ACT – mutate r2.logs and verify r1.logs remains independent/unchanged
        r2.logs.append(common.Log(before="a", after="b", description="demo"))

        # ASSERT
        with self.subTest(Field="r1.logs_len", Out=len(r1.logs), Exp=0):
            self.assertEqual(len(r1.logs), 0)
        with self.subTest(Field="r2.logs_len", Out=len(r2.logs), Exp=1):
            self.assertEqual(len(r2.logs), 1)

    def test_field_assignment(self):
        """
        Should hold assigned values and preserve Log entries; compare Log objects field-by-field using __dict__.
        """
        # ARRANGE
        attr_name = "MODEL_NUMBER"
        value_in = "ab-123"
        value_out = "AB-###"
        expected_log = common.Log(before="ab-123", after="AB-###", description="upper + mask")
        logs = [expected_log]

        # ACT
        res = common.Result(attr_name=attr_name, value_in=value_in, value_out=value_out, logs=logs)

        # ASSERT – simple fields
        with self.subTest(Field="attr_name", Out=res.attr_name, Exp=attr_name):
            self.assertEqual(res.attr_name, attr_name)
        with self.subTest(Field="value_in", Out=res.value_in, Exp=value_in):
            self.assertEqual(res.value_in, value_in)
        with self.subTest(Field="value_out", Out=res.value_out, Exp=value_out):
            self.assertEqual(res.value_out, value_out)

        # ASSERT – logs list shape
        with self.subTest(Field="logs_len", Out=len(res.logs), Exp=1):
            self.assertEqual(len(res.logs), 1)

        # ASSERT – compare custom Log object by dict to ensure field-by-field equality
        result_log_dict = res.logs[0].__dict__
        expected_log_dict = expected_log.__dict__
        with self.subTest(Field="logs[0]", Out=result_log_dict, Exp=expected_log_dict):
            self.assertEqual(result_log_dict, expected_log_dict)


if __name__ == "__main__":
    unittest.main()
