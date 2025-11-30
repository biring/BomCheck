"""
Unit tests for timestamp utilities in `src.utils.timestamp`.

Example Usage:
    # Preferred usage from project root:
    python -m unittest tests/utils/test_timestamp.py

    # Run all tests via discovery:
    python -m unittest discover -s tests

Dependencies:
    - Python >= 3.9
    - Standard Library: unittest, re, datetime
    - External Packages: None

Notes:
    - Tests treat timestamp functions as pure deterministic utilities.
    - Time bounds are validated using second-level precision for stability.
    - Ensures compatibility with tools that parse fixed-format UTC timestamps.

License:
    - Internal Use Only
"""

import re
import unittest
from datetime import datetime, timezone

# noinspection PyProtectedMember
import src.utils._timestamp as timestamp


class TestNowUtcIso(unittest.TestCase):
    """
    Unit tests for the `now_utc_iso` function in `src.utils.json`.

    This suite verifies that the function:
      - Returns an ISO 8601 timestamp string with a 'Z' UTC suffix.
      - Is precise to the second (no microseconds present).
      - Produces a time value consistent with the current UTC time at call.
    """

    def test_format_and_suffix(self):
        """
        Should return a string in the exact 'YYYY-MM-DDTHH:MM:SSZ' format with 'Z' suffix.
        """
        # ARRANGE
        iso_regex = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")

        # ACT
        result = timestamp.now_utc_iso()

        # ASSERT
        # Type check
        with self.subTest(Out=type(result).__name__, Exp=str.__name__):
            self.assertIsInstance(result, str)

        # Ends with 'Z'
        with self.subTest(Out=result.endswith("Z"), Exp=True):
            self.assertTrue(result.endswith("Z"))

        # Exact length "YYYY-MM-DDTHH:MM:SSZ" == 20 chars
        with self.subTest(Out=len(result), Exp=20):
            self.assertEqual(len(result), 20)

        # 'T' separator at the expected index (10)
        with self.subTest(Out=result[10], Exp="T"):
            self.assertEqual(result[10], "T")

        # Matches strict ISO pattern with Z suffix
        with self.subTest(Out=bool(iso_regex.match(result)), Exp=True):
            self.assertTrue(iso_regex.match(result) is not None)

        # No microseconds or explicit offset in the string
        with self.subTest(Out=("." in result), Exp=False):
            self.assertNotIn(".", result)
        with self.subTest(Out=("+00:00" in result), Exp=False):
            self.assertNotIn("+00:00", result)

    def test_value_within_current_utc_bounds(self):
        """
        Should produce a timestamp that falls between the UTC instants captured
        immediately before and after the call (inclusive), at second precision.
        """
        # ARRANGE
        # Capture lower bound (truncate to seconds)
        lower = datetime.now(timezone.utc).replace(microsecond=0)

        # ACT
        text_ts = timestamp.now_utc_iso()

        # Capture upper bound (truncate to seconds)
        upper = datetime.now(timezone.utc).replace(microsecond=0)

        # Convert back to aware UTC datetime for comparison
        parsed = datetime.strptime(text_ts, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)

        # ASSERT
        # Ensure parsed time is between lower and upper (inclusive)
        with self.subTest(Out=parsed.isoformat(),
                          Exp=f"[{lower.isoformat()} .. {upper.isoformat()}]"):
            self.assertLessEqual(lower, parsed)
            self.assertLessEqual(parsed, upper)

    def test_second_precision_no_microseconds(self):
        """
        Should represent time with second-level precision only (no microseconds).
        """
        # ARRANGE & ACT
        text_ts = timestamp.now_utc_iso()
        parsed = datetime.strptime(text_ts, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)

        # ASSERT
        with self.subTest(Out=parsed.microsecond, Exp=0):
            self.assertEqual(parsed.microsecond, 0)


if __name__ == '__main__':
    unittest.main()
