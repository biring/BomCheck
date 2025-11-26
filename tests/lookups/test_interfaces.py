"""
Unit tests for the lookup interface.

These tests verify that the public `interfaces` API correctly initializes lookup caches, exposes a valid JsonCache instance, and raises appropriate exceptions when misused.

Example Usage:
    # Preferred usage via project-root invocation:
    python -m unittest tests/lookups/test_interfaces.py

    # Direct discovery:
    python -m unittest discover -s tests

Dependencies:
    - Python >= 3.10
    - Standard Library: unittest, importlib
    - Internal: src.lookups.interfaces, src.lookups._resources

Notes:
    - Tests ensure that caches initialize cleanly after module reload.
    - Verifies behavior for valid lookups and error cases (missing keys, uninitialized cache).
    - JsonCache behavior is validated through its public interface only.

License:
    - Internal Use Only
"""

import importlib
import unittest

# noinspection PyProtectedMember
from src.lookups import interfaces as lookup  # module under test

# noinspection PyProtectedMember
from src.lookups import _resources as resource  # to reset before each test


class TestComponentTypeCache(unittest.TestCase):
    """
    Unit tests for the component-type interfaces via the public API.
    """

    def test_load(self):
        """
        Should load the resource and return valid data_map, keys and value.
        """
        # ARRANGE
        # Reload internal resources to clear any prior cache state
        importlib.reload(resource)
        importlib.reload(lookup)
        # Load component type resource
        lookup.load_cache()
        # Fetch cache via the public getter
        cache = lookup.get_component_type_cache()

        # ACT
        # Fetch data map
        out_map = cache.get_data_map_copy()
        # Fetch keys
        out_keys = cache.get_keys()
        # Fetch values
        out_vals = cache.get_value(out_keys[0], str)

        # ASSERT
        # data map
        with self.subTest("Map Not Empty", Actual=out_map):
            self.assertIsInstance(out_map, dict)
            self.assertGreater(len(out_map), 0)
        # keys
        with self.subTest("Number of keys is not zero", Actual=out_keys):
            self.assertIsInstance(out_keys, tuple)
            self.assertNotEqual(len(out_keys), 0)
        # values
        with self.subTest("Key value not empty", Actual=out_vals):
            self.assertIsInstance(out_vals, str)
            self.assertNotEqual(out_vals, "")

    def test_value_raise(self):
        """
        Should raise when requesting values for a missing key.
        """
        # ARRANGE
        missing_key = "NotARealKey"
        expected_error = KeyError.__name__
        # Reload internal resources to clear any prior cache state
        importlib.reload(resource)
        importlib.reload(lookup)
        # Load component type resource
        lookup.load_cache()
        # Fetch cache via the public getter
        cache = lookup.get_component_type_cache()

        # ACT
        try:
            _ = cache.get_value(missing_key, str)
            actual_error = ""
        except Exception as e:
            actual_error = type(e).__name__

        # ASSERT
        with self.subTest(Actual=actual_error, Expected=expected_error):
            self.assertEqual(expected_error, actual_error)

    def test_cache_raise(self):
        """
        Should raise when requesting cache before the resource has been loaded.
        """
        # ARRANGE
        expected_error = RuntimeError.__name__
        # Reload internal resources to clear any prior cache state
        importlib.reload(resource)
        importlib.reload(lookup)

        # ACT
        try:
            _ = lookup.get_component_type_cache()
            actual_error = ""
        except Exception as e:
            actual_error = type(e).__name__

        # ASSERT
        with self.subTest(Actual=actual_error, Expected=expected_error):
            self.assertEqual(expected_error, actual_error)


if __name__ == '__main__':
    unittest.main()
