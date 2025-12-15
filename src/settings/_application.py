"""
JSON-backed application settings loader and singleton cache.

This module provides a lazy-initialized CacheReadOnly instance for application-wide settings stored as a packaged JSON resource, and exposes strongly-typed key names via KEYS for consistent access.

Example Usage:
    # Preferred usage via public package interface:
    # Not applicable. This module is internal.

    # Direct module usage (acceptable in unit tests or internal scripts only):
    from src.settings import _application as app
    cache = app.get_settings()
    mask = cache.get_value(app.KEYS.COMPONENT_TYPE_STRING_IGNORE_MASK, list)

Dependencies:
    - Python >= 3.10
    - Standard Library: dataclasses, typing
    - External Packages: None
    - Internal Modules: src.common.CacheReadOnly, src.utils.folder_path

Notes:
    - The JSON resource is resolved under a project-relative resource folder (FOLDER_PARTS, RESOURCE_NAME).
    - Required keys are derived from KEYS at import time and enforced by CacheReadOnly when loading.
"""

__all__ = [
    "FOLDER_PARTS",
    "KEYS",
    "RESOURCE_NAME",
    "get_settings",
]

from dataclasses import dataclass, asdict
from typing import Final

from src.common import CacheReadOnly
from src.utils import folder_path


@dataclass(frozen=True)
class _AppSettingsKeys:
    """
    Strongly typed container for application settings JSON keys.
    """
    COMPONENT_TYPE_JACCARD_MATCH_LEVEL: str = "ComponentTypeJaccardMatchLevel"
    COMPONENT_TYPE_LEVENSHTEIN_MATCH_LEVEL: str = "ComponentTypeLevenshteinMatchLevel"
    COMPONENT_TYPE_STRING_IGNORE_MASK: str = "ComponentTypeStringIgnoreMask"


# MODULE CONSTANTS
# Where the JSON resource resides in the project
FOLDER_PARTS: Final[tuple[str, ...]] = ("src", "resources", "settings")
# Name of the JSON resource file
RESOURCE_NAME: Final[str] = "application"
# Single instance used throughout this module
KEYS: Final[_AppSettingsKeys] = _AppSettingsKeys()
# Define required schema keys for settings validation
_REQUIRED_KEYS: Final[tuple[str, ...]] = tuple(sorted(asdict(KEYS).values()))

# MODULE VARIABLES
# Lazily initialized cache for the shared application settings instance.
_application_settings_cache: CacheReadOnly | None = None


def get_settings() -> CacheReadOnly:
    """
    Load and return the singleton application settings cache.

    Initializes the cache on first access by loading the packaged JSON settings resource and validating required keys.

    Returns:
        CacheReadOnly: Read-only cache of application settings.

    Raises:
        RuntimeError: If the settings resource cannot be loaded or validated.
    """

    global _application_settings_cache

    # Lazily initialize singleton cache
    if _application_settings_cache is None:
        resource_folder = folder_path.construct_folder_path(
            base_path=folder_path.resolve_project_folder(),
            subfolders=FOLDER_PARTS
        )
        try:
            _application_settings_cache = CacheReadOnly(
                resource_folder=resource_folder,
                resource_name=RESOURCE_NAME,
                required_keys=_REQUIRED_KEYS,
            )
        except Exception as exc:
            raise RuntimeError(
                f"Failed to load '{RESOURCE_NAME}' settings from '{resource_folder}'."
                f"\n{exc}"
            ) from exc

    return _application_settings_cache
