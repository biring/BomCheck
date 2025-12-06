"""
JSON-backed temporary settings stored in the application temp folder.

This module provides:
 - Strongly typed keys for temporary settings used across workflows
 - A JsonCache-based loader for reading and persisting the temporary settings file
 - A lazy singleton accessor for internal components that require shared temp state

These settings are intended for short-lived, workflow-level state such as last-used source and destination folders, without touching user-facing configuration files.

Example Usage:
    # Preferred usage via public package interface:
    # Not applicable. This module is internal.

    # Direct module usage (allowed in tests or internal scripts):
    from src.settings import _temporary_settings as tmp
    cache = tmp.get_temp_settings()
    cache.set_value(tmp.KEYS.DESTINATION_FILES_FOLDER, "/path/out")

Dependencies:
    - Python >= 3.10
    - Standard Library: typing
    - External Packages: None
    - Internal Modules: src.common.JsonCache, src.utils.folder_path, src.utils.json_io

Notes:
    - This module is internal to the settings subsystem; it is not part of the public API.
    - Required keys are defined at import time and enforced when creating or loading the JSON file.
    - If the backing JSON is missing or invalid, a new file is created with all required keys set to empty strings.
    - A singleton cache is exposed via get_temporary_settings() to minimize disk I/O.


License:
    - Internal Use Only
"""

__all__ = [
    "get_temp_settings",
    "KEYS",
]

from dataclasses import dataclass, asdict
from typing import Any, Final

from src.common import JsonCache
from src.utils import folder_path
from src.utils import file_path
from src.utils import json_io


# ---------------------------------------------------------------------------
# Key definitions and required-key schema
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class TemporarySettingsKeys:
    """
    Strongly-typed container defining JSON key names for temporary settings.

    Each field maps directly to a JSON key stored within the temporary settings payload.

    Args:

    Returns:
        TemporarySettingsKeys: A dataclass instance containing constant key strings.

    Raises:
        None
    """
    DESTINATION_FILES_FOLDER: str = "DESTINATION_FILES_FOLDER"
    SOURCE_FILES_FOLDER: str = "SOURCE_FILES_FOLDER"


# Single instance used throughout this module
KEYS: Final[TemporarySettingsKeys] = TemporarySettingsKeys()

# REQUIRED_KEYS drives JsonCache schema validation; values are the JSON key names.
REQUIRED_KEYS: Final[tuple[str, ...]] = tuple(sorted(asdict(KEYS).values()))

# Default values for each temporary setting
DEFAULT_TEMP_SETTINGS: Final[dict[str, Any]] = {
    KEYS.DESTINATION_FILES_FOLDER: folder_path.resolve_project_folder(),
    KEYS.SOURCE_FILES_FOLDER: folder_path.resolve_project_folder(),
}

_TEMP_FILE_NAME: Final[str] = "temporary_settings"


class TemporarySettingsCache(JsonCache):
    """
    JSON-backed cache for short-lived temporary settings.

    This class wraps JsonCache to manage a key-value map stored under the application temp folder. If the JSON resource is missing or invalid, a new default file is created using DEFAULT_TEMP_SETTINGS.

    Args:

    Returns:
        TemporarySettingsCache: A fully initialized temporary settings cache.

    Raises:
        RuntimeError: If the JSON resource cannot be created or loaded.
    """

    def __init__(self) -> None:
        """
        Initialize the temporary settings cache and load the JSON resource.

        This sets the required file paths, required keys, and invokes the JsonCache loader. If the resource is missing, a new default file is created before retrying load.

        Args:

        Returns:
            None

        Raises:
            RuntimeError: If loading or creating the temporary settings file fails.
        """

        # Logical resource configuration (fixed for temporary settings)
        self._temp_cache_name: Final[str] = _TEMP_FILE_NAME
        self._temp_required_keys: Final[tuple[str, ...]] = REQUIRED_KEYS
        self._temp_file_name: Final[str] = self._temp_cache_name + json_io.JSON_FILE_EXT
        self._temp_folder_path: Final[str] = folder_path.get_temp_folder()
        self._temp_file_path: Final[str] = file_path.construct_file_path(self._temp_folder_path, self._temp_file_name)

        # Attempt to load the existing JSON resource through the base JsonCache implementation
        try:
            super().__init__(self._temp_folder_path, self._temp_cache_name, self._temp_required_keys)
        except ImportError:
            # No usable JSON resource yet; create a default one and retry loading
            self._new()
            try:
                super().__init__(self._temp_folder_path, self._temp_cache_name, self._temp_required_keys)
            except Exception as exc:
                # Escalate as a hard failure so callers know temp settings are unavailable
                raise RuntimeError(
                    f"Unable to load temporary settings JSON resource '{self._temp_file_name}' in folder '{self._temp_folder_path}'.\n{exc}"
                ) from exc

    def _new(self) -> None:
        """
        Create a new temporary settings JSON file with default values.

        Builds a default key-value map covering all REQUIRED_KEYS and persists it to disk.

        Args:


        Returns:
            None

        Raises:
            RuntimeError: If the default JSON file cannot be written.
        """
        try:
            # Generate default payload
            default_settings_map: dict[str, str] = {}
            for key in self._temp_required_keys:
                default_settings_map[key] = DEFAULT_TEMP_SETTINGS.get(key, "")

            self._persist(default_settings_map)
        except Exception as exc:
            raise RuntimeError(
                f"Failed to create default temporary settings map for resource '{self._temp_file_name}' in '{self._temp_folder_path}'.\n{exc}"
            ) from exc

    def _persist(self, settings_map: dict[str, Any]) -> None:
        """
        Persist the full settings map to disk as the temporary JSON resource.

        Ensures the target folder exists, wraps the payload in a metadata packet, and writes it as a JSON file.

        Args:
            settings_map (dict[str, Any]): The complete key-value map to serialize.

        Returns:
            None

        Raises:
            RuntimeError: If the folder cannot be created or the JSON file cannot be written.
        """

        try:
            # Ensure the temp folder exists before writing any files
            folder_path.create_folder_if_missing(self._temp_folder_path)

            # Wrap the raw key-value map in a metadata packet (e.g., version, checksum) before saving
            json_packet = json_io.create_json_packet(settings_map, self._temp_file_name)
            json_io.save_json_file(self._temp_file_path, json_packet, indent_spaces=4)
        except Exception as exc:
            raise RuntimeError(
                f"Failed to persist temporary settings to '{self._temp_file_name}' in '{self._temp_folder_path}'.\n{exc}"
            ) from exc

    def set_value(self, key: str, value: Any) -> None:
        """
        Update a temporary setting and persist the change to disk.

        The current cache map is copied, the key updated, and the map is re-persisted. JsonCache is reloaded so get_value() reflects updated state.

        Args:
            key (str): A required settings key.
            value (Any): JSON-serializable value assigned to the key.

        Returns:
            None

        Raises:
            ValueError: If the key is not in REQUIRED_KEYS.
            RuntimeError: If the updated settings map cannot be persisted or reloaded.
        """
        # Only values of existing allowed keys can be updated
        if key not in self._temp_required_keys:
            allowed_keys = ", ".join(self._temp_required_keys)
            raise ValueError(
                f"Invalid key '{key}' for temporary settings resource '{self._temp_cache_name}' in file '{self._temp_file_name}'. Allowed keys are: {allowed_keys}."
            )

        # Start from current cached state
        kv_map: dict[str, Any] = self.get_data_map_copy()
        kv_map[key] = value

        try:
            # Write updated payload
            self._persist(kv_map)

            # Reload JsonCache state so get_value() reflects the new contents
            super().__init__(self._temp_folder_path, self._temp_cache_name, self._temp_required_keys)
        except Exception as exc:
            raise RuntimeError(
                f"Failed to update temporary setting '{key}' in resource '{self._temp_file_name}'.\n{exc}"
            ) from exc


# ----------------------------------------------------------------------------
# TEMPORARY SETTING
# ----------------------------------------------------------------------------

# Lazily initialized cache for the shared temporary settings instance. This is intentionally module-global so all callers see a consistent view of temp state.
_temporary_settings_cache: TemporarySettingsCache | None = None


def get_temp_settings() -> TemporarySettingsCache:
    """
    Retrieve the singleton temporary settings cache.

    The first call constructs a TemporarySettingsCache instance; subsequent calls return the same cached instance.

    Args:
        None

    Returns:
        TemporarySettingsCache: The shared singleton instance.

    Raises:
        RuntimeError: If the cache cannot be initialized.
    """

    global _temporary_settings_cache

    if _temporary_settings_cache is None:
        try:
            _temporary_settings_cache = TemporarySettingsCache()
        except Exception as exc:
            raise RuntimeError(
                f"Failed to initialize the temporary settings.\n{exc}"
            ) from exc

    return _temporary_settings_cache
