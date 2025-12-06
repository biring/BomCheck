"""
Read/write JSON-backed cache built on top of CacheReadOnly.

This module provides:
    - A CacheReadWrite class that extends CacheReadOnly with JSON persistence support.
    - Automatic creation of a default JSON cache file when no valid resource exists.
    - Safe key-based updates that persist to disk and refresh the in-memory cache state.

Example Usage:
    # Preferred usage via higher-level settings interface:
    from src.settings import temporary as temp_settings
    temp_cache = temp_settings.get_temporary_settings()
    temp_cache.set_value("last_opened_folder", "C:/path/to/folder")

    # Direct module usage (for tests and internal tooling only):
    from src.common._cache_read_write import CacheReadWrite
    cache = CacheReadWrite(
        resource_folder_path=temp_dir,
        resource_name="temporary_settings",
        required_keys=("last_opened_folder",),
        default_values={"last_opened_folder": ""},
    )
    cache.set_value("last_opened_folder", "C:/path/to/folder")

Dependencies:
    - Python >= 3.10
    - Standard Library: typing
    - External Packages: None
    - Internal Modules: src.utils.folder_path, src.utils.file_path, src.utils.json_io, src.common.CacheReadOnly

Notes:
    - CacheReadWrite wraps the key/value map in a json_io metadata packet before persisting to disk.
    - Only keys declared in required_keys can be updated; unknown keys raise ValueError.
    - Missing or invalid JSON cache files are replaced with a default cache built from default_values and required_keys.
    - Intended for internal use by settings-like components that need small JSON-backed key/value state, not arbitrary large data.

License:
    - Internal Use Only
"""
__all__ = []  # Internal-only; not part of public API. Star import from this module gets nothing.

from typing import Final, Any

from src.utils import folder_path
from src.utils import file_path
from src.utils import json_io

from src.common import CacheReadOnly


class CacheReadWrite(CacheReadOnly):
    """
    Read/write JSON-backed cache with a fixed set of allowed keys.

    Extends CacheReadOnly to create a cache file on first use, load it into memory, and persist key updates back to disk while enforcing a predefined key set.
    """

    def __init__(
            self,
            resource_folder_path: str,
            resource_name: str,
            required_keys: tuple[str, ...],
            default_values: dict[str, Any],
    ) -> None:
        """
        Initialize a read/write JSON cache and ensure the backing file exists.

        Tries to load an existing JSON resource via CacheReadOnly; if the resource is missing or invalid, a default cache file is created using required_keys and default_values, then reloaded.

        Args:
            resource_folder_path (str): Folder path where the JSON cache file is stored or will be created.
            resource_name (str): Logical cache name, used as the base filename without extension.
            required_keys (tuple[str, ...]): Allowed keys that must be present in the cache.
            default_values (dict[str, Any]): Default values applied when creating a new cache file.

        Returns:
            None: The cache is ready for get_value and set_value operations when initialization completes.

        Raises:
            RuntimeError: If the cache file cannot be created or reloaded after a failed initial load.
        """
        self._crw_resource_name: Final[str] = resource_name
        self._crw_required_keys: Final[tuple[str, ...]] = required_keys
        self._crw_file_name: Final[str] = self._crw_resource_name + json_io.JSON_FILE_EXT
        self._crw_folder_path: Final[str] = resource_folder_path
        self._crw_file_path: Final[str] = file_path.construct_file_path(self._crw_folder_path, self._crw_file_name)
        self._crw_default_values: Final[dict[str, Any]] = default_values

        # Attempt to load the existing resource through the base CacheReadOnly implementation
        try:
            super().__init__(self._crw_folder_path, self._crw_resource_name, self._crw_required_keys)
        except ImportError:
            # No usable JSON resource yet; create a default one and retry loading
            self._create_default_cache_to_disk()
            try:
                super().__init__(self._crw_folder_path, self._crw_resource_name, self._crw_required_keys)
            except Exception as exc:
                # Escalate as a hard failure so callers know temp settings are unavailable
                raise RuntimeError(
                    f"Unable to load cache '{self._crw_file_name}' from '{self._crw_folder_path}'.\n{exc}"
                ) from exc

    def _create_default_cache_to_disk(self) -> None:
        """
        Create a new cache file populated with default values.

        Builds a key/value map for all required keys using default_values (or an empty string when missing) and persists it as a new JSON cache file.

        Args:
            None

        Returns:
            None: The new cache file is written to disk if creation succeeds.

        Raises:
            RuntimeError: If the default cache file cannot be created or written to the target folder.
        """
        try:
            # Generate default payload for every required key
            default_settings_map: dict[str, str] = {}
            for key in self._crw_required_keys:
                default_settings_map[key] = self._crw_default_values.get(key, "")

            # Persist the default cache to disk
            self._store_cache_to_disk(default_settings_map)
        except Exception as exc:
            raise RuntimeError(
                f"Failed to create default cache '{self._crw_file_name}' in '{self._crw_folder_path}'.\n{exc}"
            ) from exc

    def _store_cache_to_disk(self, settings_map: dict[str, Any]) -> None:
        """
        Persist the current cache contents to the JSON file.

        Ensures the target folder exists, wraps the settings map in a json_io metadata packet, and writes it to disk as a formatted JSON file.

        Args:
            settings_map (dict[str, Any]): The full key/value map to serialize and store in the cache file.

        Returns:
            None: The JSON file is updated on disk when persistence completes.

        Raises:
            RuntimeError: If the cache file cannot be written to disk or the folder cannot be prepared.
        """
        try:
            # Ensure the temp folder exists before writing any files
            folder_path.create_folder_if_missing(self._crw_folder_path)

            # Wrap the raw key-value map in a metadata packet (e.g., version, checksum) before saving
            json_packet = json_io.create_json_packet(settings_map, self._crw_file_name)

            # Persist the JSON packet to disk with indentation for readability
            json_io.save_json_file(self._crw_file_path, json_packet, indent_spaces=4)
        except Exception as exc:
            raise RuntimeError(
                f"Failed to store cache to '{self._crw_file_name}' in '{self._crw_folder_path}'.\n{exc}"
            ) from exc

    def update_value(self, key: str, value: Any) -> None:
        """
        Update a single cache value and persist the change to disk.

        Validates that the key is part of the required_keys set, updates the in-memory map, writes the new payload to disk, and reloads the base CacheReadOnly state.

        Args:
            key (str): Cache key to update; must be one of the required_keys.
            value (Any): New value to associate with the given key.

        Returns:
            None: The updated value is available via get_value after the call completes.

        Raises:
            ValueError: If the key is not allowed for this cache.
            RuntimeError: If writing the updated cache or reloading from disk fails.
        """
        # Only values of existing allowed keys can be updated
        if key not in self._crw_required_keys:
            allowed_keys = ", ".join(self._crw_required_keys)
            raise ValueError(
                f"Invalid key '{key}' for cache '{self._crw_resource_name}' in file '{self._crw_file_name}'. Allowed keys are: {allowed_keys}."
            )

        # Start from current cached state
        kv_map: dict[str, Any] = self.get_data_map_copy()
        kv_map[key] = value

        try:
            # Write updated payload
            self._store_cache_to_disk(kv_map)

            # Reload cache state so get_value() reflects the new contents
            super().__init__(self._crw_folder_path, self._crw_resource_name, self._crw_required_keys)
        except Exception as exc:
            raise RuntimeError(
                f"Failed to reload cache from '{self._crw_file_path}'.\n{exc}"
            ) from exc
