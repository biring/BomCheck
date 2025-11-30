"""
Public utilities for JSON serialization, file load/save operations, and constructing integrity-checked JSON packets.

This module provides:
 - Conversion between dicts and JSON strings
 - Safe loading and saving of JSON files
 - Deterministic SHA-256 checksums for payload integrity
 - Packet builders that embed UTC metadata, source file names, and payload hashes

Example Usage:
    # Preferred usage through the public utils namespace:
    import src.utils.json_io as json_io
    pkt = json_io.create_json_packet({"a": 1}, "example.json")

    # Direct module usage in unit tests:
    from src.utils.json_io import *
    data = json_string_to_dict('{"x": 5}')

Dependencies:
 - Python >= 3.10
 - Standard Library: json, hashlib, typing
 - Internal: src.utils.timestamp

Notes:
 - Payload keys must be strings and JSON-serializable.
 - Payloads are sorted lexicographically before hashing for stable SHA-256 generation.
 - File operations wrap underlying exceptions in RuntimeError for clearer diagnostics.
 - Designed as a public-facing utility in the `utils` package.

License:
 - Internal Use Only
"""
__all__ = [
    "create_json_packet",
    "dict_to_json_string",
    "extract_payload",
    "json_string_to_dict",
    "load_json_file",
    "save_json_file",
    "verify_json_payload_checksum",
]


import hashlib
import json
from typing import Any, TypedDict, Final
from . import timestamp


# JSON PACKET META DATA SCHEMA
class JsonMeta(TypedDict):
    generated_at_utc: str
    source_file_name: str
    payload_sha256: str


_KEY_UTC: Final[str] = list(JsonMeta.__annotations__.keys())[0]
_KEY_SOURCE: Final[str] = list(JsonMeta.__annotations__.keys())[1]
_KEY_SHA256: Final[str] = list(JsonMeta.__annotations__.keys())[2]


# JSON PACKET SCHEMA
class JsonPkt(TypedDict):
    meta_data: JsonMeta
    payload_data: dict[str, Any]


_KEY_META: Final[str] = list(JsonPkt.__annotations__.keys())[0]
_KEY_PAYLOAD: Final[str] = list(JsonPkt.__annotations__.keys())[1]


def _compute_payload_sha256(payload: dict[str, Any]) -> str:
    """
    Compute a deterministic SHA-256 for a dictionary's contents.

    The checksum is calculated by:
      1. Sorting keys lexicographically to ensure consistent ordering.
      2. Concatenating each key and value with no separators.
      3. Encoding the concatenated string as UTF-8 bytes.
      4. Compute SHA-256 over the encoded concatenated string.

    Args:
        payload (dict[str, Any]): Dictionary whose keys and values are included in the checksum.

    Returns:
        str: 64-char uppercase hex SHA-256.
    """

    # Sorting keys ensures stable order across Python runs
    parts: list[str] = []
    for key in sorted(payload.keys()):
        value = payload[key]
        parts.append(str(key))
        parts.append(str(value))

    # Convert concatenated string to UTF-8 bytes
    encoded_data_string = "".join(parts).encode("utf-8")

    # Calculate and return SHA-256
    return hashlib.sha256(encoded_data_string).hexdigest().upper()


def create_json_packet(payload: dict[str, Any], source_file: str) -> dict[str, Any]:
    """
    Build a deterministic JSON packet with metadata and a sorted payload.

    The payload dictionary is first sorted lexicographically by key to ensure stable ordering and reproducible SHA-256 checksums. Metadata includes the UTC generation timestamp, the source file name, and the checksum computed over the sorted payload. The returned packet structure is:

        {
            "meta": {
                "generated_at_utc": "<ISO 8601 UTC timestamp>",
                "source_file_name": "<original filename or identifier>",
                "payload_sha256": "<SHA-256 of sorted payload>"
            },
            "payload": { ... }  # shallow copy of the sorted payload
        }

    Args:
        payload (dict[str, Any]): Dictionary of data to include under the "payload" key. Keys must be strings and values must be JSON-serializable. The payload is sorted by key prior to hashing and inclusion in the packet.
        source_file (str): Original filename or logical identifier for the data source. Stored in the metadata for traceability.

    Returns:
        dict[str, Any]: JSON-ready packet containing metadata and a shallow copy of the sorted payload. Suitable for serialization and integrity validation.
    """
    # Sort payload
    sorted_payload = {k: payload[k] for k in sorted(payload.keys())}
    # Assemble metadata
    meta_info = {
        _KEY_UTC: timestamp.now_utc_iso(),
        _KEY_SOURCE: str(source_file),
        _KEY_SHA256: _compute_payload_sha256(sorted_payload),
    }
    # Return JSON-ready structure with shallow copy of data
    return {_KEY_META: meta_info, _KEY_PAYLOAD: dict(sorted_payload)}


def verify_json_payload_checksum(packet: dict[str, Any]) -> bool:
    """
    Verify the SHA-256 of the payload matches the stored SHA-256 in the metadata.

    Args:
        packet (dict[str, Any]): JSON-like dictionary with the structure:
            {
                "meta": {
                    "SHA-256": <str>
                },
                "data": { ... }
            }

    Returns:
        bool: True if the computed and stored SHA-256 match; False otherwise.
    """
    # Extract metadata and data
    meta_section = packet[_KEY_META]
    data_section = packet[_KEY_PAYLOAD]

    # Parse stored checksum
    expected_checksum = meta_section[_KEY_SHA256]

    # Compute checksum for data
    actual_checksum = _compute_payload_sha256(data_section)

    # Return comparison result
    return actual_checksum == expected_checksum


def extract_payload(packet: dict[str, Any]) -> dict[str, Any]:
    """
    Return a shallow copy of the 'data' mapping from a foundation object.

    This function assumes the input object contains a 'data' key whose value can be converted to a dict. The returned dict is a shallow copy to avoid mutating the
    original structure.

    Args:
        packet (dict[str, Any]): Foundation object expected to contain a 'data' mapping.

    Returns:
        dict[str, Any]: A shallow copy of obj['payload'].
    """
    # Return a shallow copy so callers can't mutate the original 'data'
    return dict(packet[_KEY_PAYLOAD])


def dict_to_json_string(input_dict: dict[str, Any], *, indent_spaces: int | None = None) -> str:
    """
    Serializes a dictionary of string keys into a JSON-formatted string.

    Converts a Python dictionary with string keys and any JSON-compatible values into a UTF-8-safe JSON string. Supports optional pretty-printing via the
    `indent` parameter. Raises a descriptive error if serialization fails.

    Args:
        input_dict (dict[str, Any]): Dictionary with string keys to be converted into JSON.
        indent_spaces (int | None, optional): Number of spaces for indentation in the output.
            Defaults to None for compact formatting.

    Returns:
        str: JSON-formatted string representation of the input dictionary.

    Raises:
        RuntimeError: If the dictionary cannot be serialized to JSON.
    """
    try:
        # Convert dictionary to JSON string with optional pretty printing
        return json.dumps(input_dict, indent=indent_spaces, ensure_ascii=False)
    except Exception as err:
        # Wrap the original exception with a more descriptive RuntimeError
        raise RuntimeError(
            f"Failed to serialize dictionary to JSON string — data may contain unsupported types.\n"
            f"{type(err).__name__}: {err}"
        ) from err


def json_string_to_dict(json_string: str) -> dict[str, Any]:
    """
    Deserializes a JSON-formatted string into a Python dictionary.

    Parses a UTF-8-safe JSON string and returns a Python dictionary with string keys and any JSON-compatible values. Raises a
    descriptive error if parsing fails or the data is not valid JSON.

    Args:
        json_string (str): JSON-formatted string to be parsed.

    Returns:
        dict[str, Any]: Dictionary representation of the parsed JSON data.

    Raises:
        RuntimeError: If parsing fails or if the JSON is invalid.
    """
    try:
        # Parse the JSON string into a Python dictionary
        return json.loads(json_string)
    except Exception as err:
        # Wrap the original exception with a more descriptive RuntimeError
        raise RuntimeError(
            f"Failed to deserialize JSON string — input may be invalid or not represent a dictionary.\n"
            f"{type(err).__name__}: {err}"
        ) from err


def load_json_file(file_path: str) -> dict[str, Any]:
    """
    Loads and parses a JSON file into a Python dictionary.

    Opens the file in read-only mode using UTF-8 encoding, then parses its contents into a dictionary with string keys and JSON-compatible values. Raises a descriptive error if the file cannot be opened, read, or contains invalid JSON.

    Args:
        file_path (str): Absolute or relative path to the JSON file.

    Returns:
        dict[str, Any]: Dictionary representation of the parsed JSON file.

    Raises:
        RuntimeError: If reading or parsing fails for any reason.
    """
    try:
        # Open the JSON file for reading with UTF-8 encoding
        with open(file_path, mode="r", encoding="utf-8") as file:
            # Parse the file contents into a Python dictionary
            return json.load(file)
    except Exception as err:
        # Wrap the original error with a descriptive message
        raise RuntimeError(
            f"Failed to load JSON file from '{file_path}' — file may be missing, unreadable, or contain invalid JSON.\n"
            f"{type(err).__name__}: {err}"
        ) from err


def save_json_file(file_path: str, data_dict: dict[str, Any], *,
                   indent_spaces: int | None = 2) -> None:
    """
    Writes a dictionary to disk as a JSON file.

    Serializes a dictionary with string keys and JSON-compatible values and writes it to the given path using UTF-8 encoding. By default, the output is pretty printed with indentation. Raises a descriptive error if the file cannot be created/written or if the data cannot be serialized.

    Args:
        file_path (str): Absolute or relative path to the target JSON file.
        data_dict (dict[str, Any]): Dictionary to serialize and save.
        indent_spaces (int | None, optional): Number of spaces used for indentation. Set to None for compact output. Defaults to 2.

    Returns:
        None: This function writes to disk and returns no value.

    Raises:
        RuntimeError: If the file cannot be created, opened, or written, or if serialization fails (e.g., due to non-serializable values).
    """
    try:
        # Open destination for writing (overwrites if the file exists)
        with open(file_path, mode="w", encoding="utf-8") as file:
            # Serialize the dictionary to JSON with optional pretty printing
            json.dump(data_dict, file, indent=indent_spaces, ensure_ascii=False)  # type: ignore[arg-type]
    except Exception as err:
        # Surface a clear, actionable error while preserving the original exception
        raise RuntimeError(
            f"Failed to save JSON file at '{file_path}' — directory may not exist, "
            f"file may be locked, or data contains non-serializable types.\n"
            f"{type(err).__name__}: {err}"
        ) from err
