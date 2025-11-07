"""
In-memory cache for validated JSON runtime resources.

Purpose:
 - Load a single JSON resource from the runtime directory exactly once per Cache instance
 - Enforce schema: presence of required keys and value types (str or list[str])
 - Provide safe, typed retrieval helpers for string and list-of-string values

Example Usage:
    # Preferred usage via package API:
    # Not publicly exposed; this is an internal module.

    # Direct module usage (acceptable for unit tests or internal scripts):
    from src.runtime import _cache as c
    cache = c.Cache()
    cache.load_resource("component_type", required_keys=["Capacitor"])
    kinds = cache.get_list_value("Capacitor")

Dependencies:
 - Python >= 3.10
 - Standard Library: typing
 - External Packages: None
 - Internal: src.runtime._helpers

Notes:
 - Internal-only; designed to centralize runtime JSON validation and access

License:
    - Internal Use Only
"""

from . import _helpers as hlp


class Cache:
    """
    Manage in-memory access to a runtime JSON resource.

    The Cache encapsulates logic for loading, validating, and retrieving resource data from JSON files located in the runtime directory. It ensures resources are loaded once per instance, enforces schema correctness, and provides safe access methods for string and list-of-string values.

    Attributes:
        resource (str): Name of the loaded resource (without file prefix or file type).
        data_map (dict[str, str | list[str]]): Cached key–value pairs loaded from JSON.
    """

    resource: str = None
    data_map: dict[str, str | list[str]] = None

    def _fetch_value(self, key: str) -> str | list[str]:
        """
        Retrieve the raw value for a given key from the loaded resource.

        Args:
            key (str): Key to look up within the loaded resource.

        Returns:
            str | list[str]: String value or list of string values for the specified key.

        Raises:
            RuntimeError: If no resource has been loaded.
            TypeError: If the key is not a string.
            KeyError: If the key is not present in the loaded resource.
        """
        if self.data_map is None:
            raise RuntimeError("No resource loaded. Call load_resource() before accessing values.")

        # Verify key type
        if not isinstance(key, str):
            raise TypeError(f"'{key}' name must be type string, got {type(key).__name__}.")

        # get key value
        try:
            value = self.data_map[key]
        except KeyError as err:
            raise KeyError(f"'{key}' key not found. Available keys are {sorted(self.data_map.keys())}. ") from err

        return value

    def load_resource(self, resource_name: str, required_keys: list[str]) -> None:
        """
        Load and validate a runtime JSON resource into memory.

        This method locates the JSON file corresponding to `resource_name`, loads its data, verifies required keys and value types, and stores the validated mapping in memory. Re-loading an already loaded resource raises an exception to prevent accidental overwrites.

        Args:
            resource_name (str): Logical resource name (without prefix `_` or `.json`).
            required_keys (list[str]): Keys that must be present in the resource.

        Returns:
            None: The data is stored internally for subsequent access.

        Raises:
            ResourceWarning: If the resource is already loaded for this Cache instance.
            FileNotFoundError: If the runtime JSON file for the given resource is not found.
            RuntimeError: If the JSON file cannot be read, the checksum verification fails, the payload is empty, or payload extraction fails.
            KeyError: If any required key is missing from the loaded data.
            TypeError: If the loaded data contains invalid types (non-str keys/values).
        """

        # Prevent duplicate loading
        if self.data_map:
            raise ResourceWarning(f"'{resource_name}' runtime resource has already been loaded. Reload not allowed. ")

        self.resource = resource_name
        self.data_map = {}

        # Resolve the JSON file path
        resource_file_path = hlp.resolve_json_file_path(resource_name)

        # Load JSON and extract data
        data = hlp.load_and_validate_json(resource_name, resource_file_path)

        # Validate schema integrity
        hlp.assert_required_keys_are_present(data, required_keys)
        hlp.assert_all_values_are_str_or_list_str(data)

        self.data_map = data

    def get_data_map(self) -> dict[str, str | list[str]]:
        """
        Return the full validated data map for the loaded resource.

        Returns:
            dict[str, str | list[str]]: The validated data map.

        Raises:
            ResourceWarning: If no resource has been loaded yet.
        """
        if self.data_map is None:
            raise ResourceWarning(f"'{self.resource}' resource is not loaded. Load resource before accessing resource data.")
        return self.data_map

    def get_all_keys(self) -> tuple[str, ...]:
        """
        Return all keys available in the loaded resource.

        Returns:
            tuple[str, ...]: All keys currently cached for the resource.

        Raises:
            KeyError: If no resource has been loaded yet.
        """
        # Ensure the cache has been initialized with a resource
        if self.data_map is None:
            raise KeyError(f"'{self.resource}' resource is not loaded. Load resource before requesting value of a key.")

        return tuple(self.data_map.keys())

    def get_str_value(self, key: str) -> str:
        """
        Retrieve a single string value for a given key.

        Args:
            key (str): Key to look up within the loaded resource.

        Returns:
            str: The string value associated with the key.

        Raises:
            RuntimeError: If no resource has been loaded.
            TypeError: If the key is not a string or the stored value is not a string.
            KeyError: If the key is not present in the resource.
        """
        value = self._fetch_value(key)

        # Enforce value is a string
        if not isinstance(value, str):
            raise TypeError(f"'{key}' key value should be type string, got type '{type(value).__name__}'. ")

        return value

    def get_list_value(self, key: str) -> tuple[str, ...]:
        """
        Retrieve a list of string values for a given key.

        If the stored value is a single string, it is normalized to a single-item list.

        Args:
            key (str): Key to look up within the loaded resource.

        Returns:
            tuple[str, ...]: Tuple of values for the specified key. A stored string is returned
                as a one-element tuple.

        Raises:
            RuntimeError: If no resource has been loaded.
            TypeError: If the key is not a string or the stored value is neither a string nor a list.
            KeyError: If the key is not present in the resource.
        """
        value = self._fetch_value(key)

        # Enforce value is a list
        if not isinstance(value, (str | list)):
            raise TypeError(f"'{key}' key value should be type string or list, got type '{type(value).__name__}'. ")

        # Normalize single string into list
        if isinstance(value, str):
            value = [value]

        return tuple(value)
