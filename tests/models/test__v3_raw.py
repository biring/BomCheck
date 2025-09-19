"""
Unit tests for the raw Version 3 BOM data models.

This suite validates the behavior of the dataclasses defined in `_v3_raw.py`

Example Usage:
    # Preferred usage via project-root invocation:
    python -m unittest tests/models/test__v3_raw.py

    # Direct discovery (runs all tests, including this module):
    python -m unittest discover -s tests

Dependencies:
    - Python >= 3.10
    - Standard Library: unittest
    - External Packages: None

Notes:
    - Tests use direct imports of internal modules which is acceptable for unit testing.

License:
    - Internal Use Only
"""

import unittest

# noinspection PyProtectedMember
from src.models import _v3_fields as fields  # Direct internal import acceptable in test modules
# noinspection PyProtectedMember
from src.models import _v3_raw as raw  # Direct internal import acceptable in test modules


class TestHeader(unittest.TestCase):
    """
    Unit tests for `header` class methods.
    """

    def test_get_labels(self):
        """
        Should return tuple with Header labels.
        """
        # ARRANGE
        expected = tuple(fields.HEADER_TO_ATTR_MAP.keys())

        # ACT
        result = raw.Header.get_labels()

        # ASSERT
        with self.subTest(Out=type(result).__name__, Exp=tuple.__name__):
            self.assertIsInstance(result, tuple)
        with self.subTest(Out=result, Exp=expected):
            self.assertEqual(result, expected)

    def test_get_by_label_invalid(self):
        """
        Should raise KeyError when an invalid header label is requested.
        """
        # ARRANGE
        hdr = raw.Header()
        invalid_label = "NotHeaderLabel"
        expected = KeyError.__name__

        # ACT
        try:
            hdr.get_by_label(invalid_label)
            result = ""  # No exception raised
        except KeyError as e:
            result = type(e).__name__

        # ASSERT
        with self.subTest(Out=result, Exp=expected):
            self.assertEqual(result, expected)

    def test_get_by_label_valid(self):
        """
        Should return the value of the attribute mapped by a valid header label.
        """
        # ARRANGE
        hdr = raw.Header(model_no="ABC123")
        expected = hdr.model_no

        # ACT
        result = hdr.get_by_label(fields.HeaderFields.MODEL_NUMBER)

        # ASSERT
        with self.subTest(Out=result, Exp=expected):
            self.assertEqual(result, expected)


class TestRows(unittest.TestCase):
    """
    Unit tests for `rows` class methods.
    """

    def test_get_by_label_invalid(self):
        """
        Should raise KeyError when an invalid row label is requested.
        """
        # ARRANGE
        row = raw.Row()
        invalid_label = "NotRowLabel"
        expected = KeyError.__name__

        # ACT
        try:
            row.get_by_label(invalid_label)
            result = ""  # No exception raised
        except KeyError as e:
            result = type(e).__name__

        # ASSERT
        with self.subTest(Out=result, Exp=expected):
            self.assertEqual(result, expected)

    def test_get_by_label_valid(self):
        """
        Should return the value of the attribute mapped by a valid row label.
        """
        # ARRANGE
        row = raw.Row(qty="2")
        expected = row.qty

        # ACT
        result = row.get_by_label(fields.RowFields.QTY)

        # ASSERT
        with self.subTest(Out=result, Exp=expected):
            self.assertEqual(result, expected)

    def test_get_labels(self):
        """
        Should return tuple with Row labels.
        """
        # ARRANGE
        expected = tuple(fields.ROW_TO_ATTR_MAP.keys())

        # ACT
        result = raw.Row.get_labels()

        # ASSERT
        with self.subTest(Out=type(result).__name__, Exp=tuple.__name__):
            self.assertIsInstance(result, tuple)
        with self.subTest(Out=result, Exp=expected):
            self.assertEqual(result, expected)

    def test_get_v3_template_labels(self):
        """
        Should return tuple with v3 template identifier Row labels.
        """
        # ARRANGE
        expected = tuple(fields.REQ_V3_ROW_IDENTIFIERS)

        # ACT
        result = raw.Row.get_v3_template_labels()

        # ASSERT
        with self.subTest(Out=type(result).__name__, Exp=tuple.__name__):
            self.assertIsInstance(result, tuple)
        with self.subTest(Out=result, Exp=expected):
            self.assertEqual(result, expected)


if __name__ == "__main__":
    unittest.main()
