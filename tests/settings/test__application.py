"""
Unit tests for the JSON-backed application settings cache and singleton accessor.

This module validates behavior of the application settings loader, including:
 - Successful loading and caching of application-level settings
 - Correct access to typed values via the settings cache
 - Proper failure behavior when the settings resource cannot be resolved

Example Usage:
    # Preferred usage via project-root invocation:
    python -m unittest tests.settings.test__application

    # Direct discovery (runs all tests, including this module):
    python -m unittest discover -s tests

Dependencies:
    - Python >= 3.10
    - Standard Library: unittest, unittest.mock
    - Internal Packages: src.settings._application

Notes:
    - Tests treat get_settings() as a singleton accessor that returns an immutable, populated cache.
    - Happy-path behavior is validated using real resources without patching loaders.
    - Failure-path behavior is validated by overriding resource resolution inputs only.
    - Tests do not validate JSON schema or parsing internals; those are owned by json_io utilities.

License:
    - Internal Use Only
"""
import unittest
from unittest.mock import patch

# noinspection PyProtectedMember
from src.settings import _application as app_settings  # module under test


class TestGetSettings(unittest.TestCase):
    """
    Unit tests for the `get_settings` singleton accessor.
    """

    def setUp(self) -> None:
        """
        Reset the application settings singleton before each test.
        """
        # Reset singleton to force fresh load
        app_settings._application_settings_cache = None

    def tearDown(self) -> None:
        """
        Reset the application settings singleton after each test.
        """
        # Reset singleton to force fresh load
        app_settings._application_settings_cache = None

    def test_happy_path(self) -> None:
        """
        Should load application settings and return a populated cache.
        """
        # ARRANGE
        test_key = app_settings.KEYS.COMPONENT_TYPE_STRING_IGNORE_MASK

        # ACT
        cache = app_settings.get_settings()
        sample_value = cache.get_value(test_key, list)

        # ASSERT
        with self.subTest("Type", Out=type(sample_value).__name__, Exp=list.__name__):
            self.assertIsInstance(sample_value, list)

        with self.subTest("Length", Out=len(sample_value), Exp=">0"):
            self.assertGreater(len(sample_value), 0)

    def test_raise(self) -> None:
        """
        Should raise when the settings resource cannot be located/loaded.
        """
        # ARRANGE
        expected = RuntimeError.__name__

        # ACT
        # Override resource path to force load failure
        with patch.object(app_settings, "FOLDER_PARTS", new=("not_a_folder",)):
            try:
                _ = app_settings.get_settings()
                actual = ""
            except Exception as exc:
                actual = type(exc).__name__

        # ASSERT
        with self.subTest(Out=actual, Exp=expected):
            self.assertEqual(actual, expected)


if __name__ == "__main__":
    unittest.main()
