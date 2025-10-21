"""
Utility functions for serializing and deserializing JSON data, reading/writing JSON files, and parsing strict key–value text formats.

This module includes helpers to:
    - Conversion between dicts (string keys) ↔ JSON strings (`dict_to_json_string`, `json_string_to_dict`)
    - Reading/writing JSON files (`load_json_file`, `save_json_file`)
    - JSON packet structure helpers with metadata and deterministic SHA-256 checksums
    - Parse strict `"Key" = "Value"` text formats with optional list values

Typical uses include:
    - Centralized JSON I/O for configuration, small datasets, and test fixtures
    - Creating self-validating JSON objects with metadata and checksums
    - Parsing deterministic key–value text formats for configuration import

Example Usage:
    # Preferred usage via package interface:
    # Not exposed publicly; this is an internal module.

    # Direct module usage (acceptable in unit tests or internal scripts only):
    import src.utils._json_io as jio
    text = jio.dict_to_json_string({"name": "bob"}, indent_spaces=None)

Dependencies:
    - Python >= 3.10  (`dict[str, Any]` typing)
    - Standard Library: json, re, datetime, typing

Notes:
    - Keys are assumed to be strings; values must be JSON-serializable.
    - Files are read/written as UTF-8; `ensure_ascii=False` preserves Unicode characters.
    - Functions raise `RuntimeError` with wrapped original exceptions for clear diagnostics.
    - Packet checksums are computed over sorted key–value pairs.
    - Strict parser rejects duplicate keys and malformed lines; supports comments prefixed with `#`.
    - Designed for deterministic serialization and integrity verification within the utils package.
    - Intended for internal use within the `utils` package to centralize JSON I/O.

License:
 - Internal Use Only
"""
import hashlib
import json
import re
from datetime import datetime, timezone
from typing import Any, TypedDict, Final

LINE_KEY_VALUE_RE = re.compile(
    r'^\s*'  # Optional leading whitespace
    r'"([^"]+)"'  # "key" — one or more non-quote characters inside quotes
    r'\s*=\s*'  # Optional spaces around '='
    r'(?:'  # Non-capturing group for either form of value
    r'"([^"]*)"'  # Case 1: "value" — zero or more non-quote characters inside quotes
    r'|'  # OR
    r'\[\s*([^\]]*?)\s*\]'  # Case 2: [ ... ] — list of values inside square brackets (no nested brackets)
    r')'  # End non-capturing group
    r'\s*$'  # Optional trailing whitespace
)
LIST_ITEM_RE = re.compile(r'"([^"\\]*(?:\\.[^"\\]*)*)"')


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


def parse_strict_key_value_to_dict(source_path: str, text: str) -> dict[str, str]:
    """
    Parse a quoted key–value configuration text into a dictionary.

    Each non-empty, non-comment line must match the exact form `"Key" = "Value"` or `"Key" = ["Value1", "Value2", ...]`. Lines beginning with `#` are ignored, and trailing comments introduced by `#` are stripped before validation. Invalid lines are skipped with a WARNING log entry. Duplicate keys terminate parsing with an exception.

    Args:
        source_path (str): Logical name or file path used only for diagnostics in logs/errors.
        text (str): Entire input content to parse.

    Returns:
        dict[str, str]: Mapping of parsed keys to values. List values are stored as their bracketed string representation (e.g., '["A", "B"]').

    Raises:
        RuntimeError: If the same key appears more than once in the input.
    """
    result: dict[str, str] = {}

    for line_no, raw_line in enumerate(text.splitlines(), start=1):
        # Ignore empty lines exactly (after trimming whitespace).
        if raw_line.strip() == '':
            continue

        # Ignore lines that begin with '#' (no leading whitespace allowed by spec).
        if raw_line.startswith('#'):
            continue

        # Strip trailing comments and surrounding whitespace.
        content = raw_line.split('#', 1)[0].strip()
        if content == '':
            # Line reduced to nothing after removing a trailing comment.
            continue

        # Validate strict `"Key" = "Value"` format.
        match = LINE_KEY_VALUE_RE.match(content)
        if not match:
            # Non-conforming lines are not accepted; warn and skip
            print(
                f"Invalid key-value format at {source_path}:{line_no}; ignoring line: {raw_line!r}")
            continue

        # Extract key/value from regex groups (1 = key, 2 = single value, 3 = list of values).
        key = match.group(1)
        value = None

        # Case 1: Standard quoted value ("Key" = "Value")
        if match.group(2) is not None:
            value = match.group(2)

        # Case 2: List-style value ("Key" = ["A", "B", "C"])
        elif match.group(3) is not None:
            raw_items = match.group(3)
            # Extract only properly quoted items; supports escaped quotes and commas inside items
            items = [m.group(1).encode("utf-8").decode("unicode_escape")
                     for m in LIST_ITEM_RE.finditer(raw_items)]
            value = "[" + ", ".join(f'"{i}"' for i in items) + "]"

        else:
            # Neither group matched; ignore this line safely
            print(f"Invalid value at {source_path}:{line_no}; ignoring line: {raw_line!r}")
            continue

        # Enforce unique keys.
        if key in result:
            raise RuntimeError(f"Duplicate key '{key}' in {source_path} at line {line_no}.")

        result[key] = value

    return result


def _now_utc_iso() -> str:
    """
    Get the current UTC time in ISO 8601 format with a 'Z' suffix.

    The output is accurate to the second (microseconds are removed) and uses the 'Z' suffix to indicate UTC, instead of an explicit offset.

    Returns:
        str: Current UTC timestamp in the form 'YYYY-MM-DDTHH:MM:SSZ'.
    """
    return (
        datetime.now(timezone.utc)  # Get current time in UTC
        .replace(microsecond=0)  # Remove microseconds for second precision
        .isoformat()  # Convert to ISO 8601
        .replace("+00:00", "Z")  # Replace '+00:00' with 'Z' for UTC
    )


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
    Build the JSON packet with meta and payload data.

    The returned structure contains:
        {
            "meta": {
                "generated_at_utc": "<ISO 8601 UTC timestamp>",
                "source_file_name": "<original filename>",
                "payload_sha256": <SHA-256 of payload>
            },
            "payload": { ... }  # shallow copy of the provided data
        }

    Args:
        payload (dict[str, Any]): Dictionary of data to include under the "payload" key. Values will be shallow-copied into the output.
        source_file (str): Original filename or identifier for the data source.

    Returns:
        dict[str, Any]: The JSON-ready object containing the meta and payload data.
    """
    # Assemble metadata
    meta_info = {
        _KEY_UTC: _now_utc_iso(),
        _KEY_SOURCE: str(source_file),
        _KEY_SHA256: _compute_payload_sha256(payload),
    }
    # Return JSON-ready structure with shallow copy of data
    return {_KEY_META: meta_info, _KEY_PAYLOAD: dict(payload)}


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
