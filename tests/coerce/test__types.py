"""
Unit tests for coerce package internal data types.

Example Usage:
    # Preferred usage via project-root invocation:
    python -m unittest tests/coerce/test__types.py

    # Direct discovery (runs all tests, including this module):
    python -m unittest discover -s tests

Dependencies:
    - Python >= 3.10
    - Standard Library: unittest
    - External Packages: None

Notes:
    - Tests use a direct internal import (from src.coerce._types import ...) which is acceptable in unit tests.
    - Assertions use subTest for clearer diagnostics on individual field checks and rendered line comparisons.

License:
    - Internal Use Only
"""

import unittest

# noinspection PyProtectedMember
from src.coerce._types import Log, Result, Rule  # Direct internal import — acceptable in tests


class TestLog(unittest.TestCase):
    """
    Unit tests for the `Log` dataclass.
    """

    def test_init(self):
        """
        Should correctly initialize all `Log` fields.
        """
        # ARRANGE
        before = "Acme  Corporation"
        after = "Acme Corporation"
        description = "Collapsed repeated spaces"

        # ACT
        log = Log(before=before, after=after, description=description)

        # ASSERT
        with self.subTest(Field="before", Out=log.before, Exp=before):
            self.assertEqual(log.before, before)
        with self.subTest(Field="after", Out=log.after, Exp=after):
            self.assertEqual(log.after, after)
        with self.subTest(Field="description", Out=log.description, Exp=description):
            self.assertEqual(log.description, description)


class TestResult(unittest.TestCase):
    """
    Unit tests for the `Result` dataclass and its `render` behavior.
    """

    def test_init(self):
        """
        Should correctly initialize all `Result` fields.
        """
        # ARRANGE
        attr_name = "manufacturer"
        value_in = "Acme  Corporation"
        value_out = "ACME"
        logs = [
            Log(before="Acme  Corporation", after="Acme Corporation", description="Collapsed repeated spaces"),
            Log(before="Acme Corporation", after="ACME", description="Mapped to canonical vendor code"),
        ]

        # ACT
        res = Result(attr_name=attr_name, original_value=value_in, coerced_value=value_out, changes=logs)

        # ASSERT
        with self.subTest(Field="attr_name", Out=res.attr_name, Exp=attr_name):
            self.assertEqual(res.attr_name, attr_name)
        with self.subTest(Field="value_in", Out=res.original_value, Exp=value_in):
            self.assertEqual(res.original_value, value_in)
        with self.subTest(Field="value_out", Out=res.coerced_value, Exp=value_out):
            self.assertEqual(res.coerced_value, value_out)
        with self.subTest(Field="logs_len", Out=len(res.changes), Exp=len(logs)):
            self.assertEqual(len(res.changes), len(logs))

    def test_render_empty(self):
        """
        Should return an empty tuple when `value_in` equals `value_out`, regardless of logs.
        """
        # ARRANGE
        result_obj = Result(
            attr_name="manufacturer",
            original_value="Acme Corporation",
            coerced_value="Acme Corporation",  # no effective change
            changes=[
                Log(before="Acme  Corporation", after="Acme Corporation", description="Collapsed repeated spaces"),
            ],
        )
        expected = tuple()

        # ACT
        out = result_obj.render_changes()

        # ASSERT
        with self.subTest(Out=out, Exp=expected):
            self.assertEqual(out, expected)

    def test_render_log(self):
        """
        Should format one line per `Log` entry when `value_in` != `value_out`.
        """
        # ARRANGE
        logs = [
            Log(before="Acme  Corporation", after="Acme Corporation", description="Collapsed repeated spaces"),
            Log(before="Acme Corporation", after="ACME", description="Mapped to canonical vendor code"),
        ]
        result_obj = Result(
            attr_name="manufacturer",
            original_value="Acme  Corporation",
            coerced_value="ACME",  # net effective change is present
            changes=logs,
        )
        expected = (
            "'manufacturer' changed from 'Acme  Corporation' to 'Acme Corporation'. Collapsed repeated spaces",
            "'manufacturer' changed from 'Acme Corporation' to 'ACME'. Mapped to canonical vendor code",
        )

        # ACT
        out = result_obj.render_changes()

        # ASSERT
        with self.subTest(Out=len(out), Exp=len(expected)):
            self.assertEqual(len(out), len(expected))
        for idx, (got, exp) in enumerate(zip(out, expected), start=1):
            with self.subTest(Line=idx, Out=got, Exp=exp):
                self.assertEqual(got, exp)


class TestRule(unittest.TestCase):
    """
    Unit tests for the `Rule` dataclass, focusing on initialization and error handling.
    """

    def test_init(self):
        """
        Should correctly initialize `Rule` fields for a valid regex pattern.
        """
        # ARRANGE
        pattern = r"\s+"
        replacement = " "
        msg = "Normalize whitespace"

        # ACT
        rule = Rule(pattern=pattern, replacement=replacement, description=msg)

        # ASSERT
        with self.subTest(Field="pattern", Out=rule.pattern, Exp=pattern):
            self.assertEqual(rule.pattern, pattern)
        with self.subTest(Field="replacement", Out=rule.replacement, Exp=replacement):
            self.assertEqual(rule.replacement, replacement)
        with self.subTest(Field="msg", Out=rule.description, Exp=msg):
            self.assertEqual(rule.description, msg)

    def test_raises(self):
        """
        Should raise ValueError when an invalid regex pattern is provided.
        """
        # ARRANGE
        bad_pattern = r"("  # unbalanced parenthesis => invalid regex
        expected_exception = ValueError.__name__

        # ACT
        try:
            Rule(pattern=bad_pattern, replacement="", description="bad")  # type: ignore[arg-type]
            result = ""  # no exception raised
        except ValueError as exc:
            result = type(exc).__name__

        # ASSERT
        with self.subTest(Out=result, Exp=expected_exception):
            self.assertEqual(result, expected_exception)


if __name__ == "__main__":
    unittest.main()
