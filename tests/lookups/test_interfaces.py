"""
Integration tests for the public lookups interfaces.

This module verifies that lookup APIs exposed by the lookups package provide valid, populated lookup tables and related constants, without asserting internal resource-loading or caching behavior.

Example Usage:
    # Preferred usage via project-root invocation:
    python -m unittest tests/lookups/test_interfaces.py

    # Direct discovery (runs all tests, including this module):
    python -m unittest discover -s tests

Dependencies:
    - Python >= 3.10
    - Standard Library: unittest
    - Internal Packages: src.lookups.interfaces

Notes:
    - Tests are integration-style and exercise happy-path behavior only.
    - Interfaces are treated as stable API contracts; tests assert presence, type, and basic validity of outputs.
    - Resource files, paths, and parsing logic are owned by private lookup modules and are not patched or inspected here.
    - Designed to catch API regressions as lookup resources and internals evolve.

License:
    - Internal Use Only
"""

import unittest

from src.lookups import interfaces as lookup


class TestInterfaces(unittest.TestCase):
    """
    Integration tests for the public lookups interface.
    """

    def test_component_type(self):
        """
        Should expose a populated component-type lookup table and related constants via the public interfaces API.
        """
        # ARRANGE
        # n/a

        # ACT
        out_map = lookup.get_component_type_lookup_table()
        folder_parts = lookup.COMPONENT_TYPE_FOLDER_PARTS
        resource_name = lookup.COMPONENT_TYPE_RESOURCE_NAME

        # ASSERT
        with self.subTest("Lookup table"):
            self.assertIsInstance(out_map, dict)
            self.assertGreater(len(out_map), 0)
        with self.subTest("Folder parts"):
            self.assertIsInstance(folder_parts, tuple)
            self.assertGreater(len(folder_parts), 0)
        with self.subTest("Resource name"):
            self.assertIsInstance(resource_name, str)
            self.assertGreater(len(resource_name), 0)


if __name__ == '__main__':
    unittest.main()
