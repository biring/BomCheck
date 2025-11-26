"""
Unit tests for internal lookup helper functions.

These tests validate the behavior of `extract_uppercase_keys`, ensuring correct filtering,type matching, and deterministic ordering for uppercase symbolic constant extraction.

Example Usage:
    # Preferred usage via project-root invocation:
    python -m unittest tests/lookups/test__helpers.py

    # Direct discovery:
    python -m unittest discover -s tests

Dependencies:
    - Python >= 3.10
    - Standard Library: unittest
    - Internal: src.lookups._helpers

Notes:
    - Tests validate only public behavior: filtering rules, allowed-type matching, and sorted output.
    - Fixtures are inline dictionaries to keep cases isolated and easy to reason about.
    - No reliance on internal implementation details beyond the documented interface.

License:
    - Internal Use Only
"""


import unittest

# noinspection PyProtectedMember
from src.lookups import _helpers as helper  # Module under test


class TestExtractUppercaseKeys(unittest.TestCase):
    """
    Unit tests for the `extract_uppercase_keys` helper function.

    The tests cover:
    - Filtering only ALL-CAPS keys.
    - Enforcing allowed value types via the `allowed_value_type` parameter.
    - Returning results as a sorted tuple for stable ordering.
    """

    def test_happy_path(self):
        """
        Should return only uppercase names whose values match the allowed types.
        """
        # ARRANGE
        module_globals = {
            "USER_NAME": "foo",
            "MY_CODE": "bar",
            "mask": "value",
            "Mixed": "type is mixed",
            "RETRY": 123,
            "LOWER_THRESHOLD": -123,
            "boundary_number": 589,
            "REQUIRED_KEYS": ["X"],
            "NUMBER_LIST": [1, 2, 3],
            "Cypher": [1, 2, 3],
        }

        cases = (
            ((str,), ("MY_CODE", "USER_NAME")),
            ((int,), ("LOWER_THRESHOLD", "RETRY")),
            ((list,), ("NUMBER_LIST", "REQUIRED_KEYS")),
            ((int, str), ("LOWER_THRESHOLD", "MY_CODE", "RETRY", "USER_NAME")),

        )

        for allowed_value_type, expected in cases:
            # ACT
            # Call the helper to extract uppercase keys matching allowed types
            result = helper.extract_uppercase_keys(module_globals, allowed_value_type)

            # ASSERT
            # Verify tuple content and ordering
            with self.subTest(Out=result, Exp=expected):
                self.assertEqual(result, expected)

    def test_without_any_matching_entries(self):
        """
        Should return an empty tuple when no uppercase keys match allowed types.
        """
        # ARRANGE
        module_globals = {
            "lower": "value",  # lowercase key, excluded
            "MixedCase": 100,  # mixed case key, excluded
            "LIST": [1, 2, 3],  # uppercase but list, not allowed type
            "NUM": 42,  # uppercase but int, not allowed type
        }
        allowed_value_type = (str,)
        expected: tuple[str, ...] = ()  # Expect empty tuple

        # ACT
        result = helper.extract_uppercase_keys(module_globals, allowed_value_type)

        # ASSERT
        with self.subTest(Out=result, Exp=expected):
            self.assertEqual(result, expected)

    def test_with_multiple_allowed_value_types(self):
        """
        Should include uppercase keys whose values match any allowed type,
        including bool when int is allowed (bool is a subclass of int).
        """
        # ARRANGE
        module_globals = {
            "NAME": "Widget",  # str, allowed
            "COUNT": 10,  # int, allowed
            "PRICE": 9.99,  # float, excluded
            "ENABLED": True,  # bool, included because bool is a subclass of int
            "label": "skip",  # lowercase key, excluded
        }
        allowed_value_type = (str, int)
        # Expect uppercase keys whose values are str or int (including bool),
        # sorted by key name
        expected = ("COUNT", "ENABLED", "NAME")

        # ACT
        result = helper.extract_uppercase_keys(module_globals, allowed_value_type)

        # ASSERT
        with self.subTest(Out=result, Exp=expected):
            self.assertEqual(result, expected)


if __name__ == "__main__":
    unittest.main()
