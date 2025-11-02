"""
Runtime JSON resource helpers for locating, loading, and validating package-managed runtime files.

Example Usage:
    # Preferred usage via public package interface:
    # Internal-only; surface helpers via a stable package API if needed.

    # Direct module usage (acceptable in unit tests or internal scripts only):
    from src.runtime import _helpers as helpers
    path = helpers.resolve_json_file_path("log_msg")
    data = helpers.load_and_validate_json("log_msg", path)
    helpers.assert_all_values_are_str_or_list_str(data)

Dependencies:
 - Python >= 3.10
 - Standard Library: typing
 - Internal Packages: src.utils

Notes:
 - Runtime JSON files live under the package runtime directory and start with "_" (e.g., "_log_msg.json").
 - Checksums are required for integrity; loading fails if verification does not pass.
 - Intended for internal use; do not treat these helpers as a public API boundary.

License:
    - Internal Use Only
"""
__all__ = []  # Internal-only; not part of public API. Star import from this module gets nothing.

import src.utils as utils

RUNTIME_JSON_PREFIX = "_"
RUNTIME_FOLDER: tuple[str, ...] = ("src", "runtime",)


def assert_all_values_are_str_or_list_str(key_value_map: dict[str, str | list[str]]) -> None:
    """
    Validate that all values in the provided dictionary are strings or list of strings.

    Iterates through each key-value pair in the dictionary and checks that the value is of type `str` or type `list[str]`. If a non-string value is found, a `TypeError` is raised specifying the key with the invalid value.

    Args:
        key_value_map (dict[str, str | list[str]]): Dictionary mapping keys to string values.

    Returns:
        None: This function performs validation and does not return anything.

    Raises:
        TypeError: If any value in the dictionary is not of type `str`.
    """

    # Ensure provided data is a dict
    if not isinstance(key_value_map, dict):
        raise TypeError(f"Resource map must be type dict, got '{type(key_value_map).__name__}'.")

    # Iterate through each key-value pair in the dictionary
    for key, value in key_value_map.items():
        # Ensure the key is a string; raise an error if not
        if not isinstance(key, str):
            raise TypeError(f"'{key}' key must be a type string, got '{type(key_value_map).__name__}'.")
        # Ensure the value is a string or list of string
        if isinstance(value, str):
            continue
        if isinstance(value, list) and all(isinstance(x, str) for x in value):
            continue
        raise TypeError(f"Invalid value type for key '{key}': expected str or list[str], got {type(value).__name__}.")


def assert_required_keys_are_present(key_value_map: dict[str, str], required_keys: list[str]) -> None:
    """
    Verify that all required keys are present in the provided dictionary.

    Compares the list of `required_keys` against the keys in `key_value_map` and raises a `KeyError` if any required key is missing.

    Args:
        key_value_map (dict[str, str]): Dictionary mapping keys to string values.
        required_keys (list[str]): List of keys that must be present in the dictionary.

    Returns:
        None: This function performs validation and does not return anything.

    Raises:
        KeyError: If any required keys are missing from `key_value_map`.
    """

    if required_keys:
        # Identify any required keys that are missing from the dictionary
        missing_keys = [key for key in required_keys if key not in key_value_map]

        # If any required keys are missing, raise a KeyError with details
        if missing_keys:
            raise KeyError(f"Missing mandatory keys: {missing_keys}.")


def export_keys(module_globals: dict) -> list[str]:
    """
    Extract all uppercase string constant names from a module's globals.

    This is typically used to auto-generate a module's `__all__` by scanning for public key constants (following the convention of all-uppercase names).

    Args:
        module_globals (dict[str, object]): The dictionary returned by `globals()` from the calling module.

    Returns:
        list[str]: List of constant names (keys from `module_globals`) that are all-uppercase and have string values.
    """
    keys: list[str] = []

    # Iterate through globals as (name, value) pairs
    for name, value in module_globals.items():
        # Only include all-uppercase names (conventional constants)
        if name.isupper():
            # Ensures you only export string keys to avoid exporting REQUIRED_KEYS constant because it is a list.
            if isinstance(value, str):
                keys.append(name)

    return keys


def load_and_validate_json(resource_name: str, resource_path: str) -> dict:
    """
    Load, validate, and extract key–value pairs from a runtime JSON resource.

    Args:
        resource_name (str): Logical resource name of the JSON file.
        resource_path (str): Full path to the resource file.

    Returns:
        dict[str, str | list[str]]: Validated mapping extracted from the JSON file.

    Raises:
        RuntimeError: If the file read fails, checksum verification fails, payload data is empty or payload
            extraction fails.
    """
    # Load the JSON package
    json_package = utils.load_json_file(resource_path)

    # Verify integrity of the payload via checksum in meta
    if not utils.verify_json_payload_checksum(json_package):
        raise RuntimeError(f"'{resource_name} runtime resource JSON data checksum verification failed.")

    # Extract the "key:value" mapping (shallow copy)
    key_value_map = utils.extract_payload(json_package)

    # Make sure data is not empty
    if not key_value_map:
        raise RuntimeError(f"'{resource_name}' runtime resource JSON file has no data.")

    return key_value_map


def resolve_json_file_path(resource_name: str) -> str:
    """
    Resolve the absolute path to a runtime JSON resource by name.

    Builds the expected "_<resource_name>.json" filename, locates the runtime folder, lists available JSON files in that folder, and verifies the target file exists. Returns the absolute path if found.

    Args:
        resource_name (str): Logical resource name (file stem) of the JSON (e.g., "_log_msg").

    Returns:
        str: Absolute path to the JSON file within the runtime directory.

    Raises:
        RuntimeError: If the runtime JSON file is not found.
    """
    # Build the expected filename, e.g., "_log_msg.json"
    target_filename = RUNTIME_JSON_PREFIX + resource_name + utils.JSON_FILE_EXT

    # Locate the application root and runtime folder
    project_root = utils.find_root_folder()
    runtime_dir = utils.construct_folder_path(project_root, RUNTIME_FOLDER)

    # Enumerate JSON files available in the runtime directory
    available_filenames = utils.get_files_in_directory(runtime_dir, [utils.JSON_FILE_EXT])

    # Validate presence of the requested resource file
    if target_filename not in available_filenames:
        raise FileNotFoundError(f"'{target_filename}' file not found in '{runtime_dir}'. ")

    # Construct and return the absolute file path
    return utils.build_file_path(runtime_dir, target_filename)
