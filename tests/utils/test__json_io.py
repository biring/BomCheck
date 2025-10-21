"""
Unit tests for JSON utility functions.

This module validates serialization, deserialization, file loading, and file saving behaviors for the JSON helper functions:
    - dict_to_json_string: Serialize dicts to JSON strings with optional indentation
    - json_string_to_dict: Deserialize JSON strings into Python dictionaries
    - load_json_file: Read and parse JSON from disk into a dictionary
    - save_json_file: Serialize and save a dictionary to disk as JSON

Each test suite covers:
    - Correct handling of valid input data (including Unicode characters)
    - Proper application of optional pretty-print indentation
    - Behavior with nested structures and whitespace
    - Error handling for malformed JSON, non-serializable values, and missing files

Example Usage:
    # Preferred usage — run all tests in this module:
    python -m unittest tests/utils/test__json_io.py

Dependencies:
 - Python >= 3.9
 - Standard Library: unittest, json, os, tempfile, shutil
 - Internal: src.utils.json

Notes:
    - Tests follow the Arrange–Act–Assert pattern with `subTest` assertions for clearer output on mismatches.
    - Temporary files and directories are created in setUp/tearDown to ensure isolation between tests and avoid polluting the filesystem.
    - Unicode handling is explicitly verified to ensure `ensure_ascii=False` works as intended.

License:
 - Internal Use Only
"""

import copy
import json
import os
import re
import shutil
import tempfile
import unittest
from datetime import datetime, timezone
from unittest.mock import patch

# noinspection PyProtectedMember
import src.utils._json_io as jio


class TestComputePayloadSha256(unittest.TestCase):
    """
    Unit tests for `_compute_payload_sha256`.

    Note: Use https://emn178.github.io/online-tools/sha256.html to generate expected value
    """

    def test_value(self):
        """
        Should match known SHA-256 for {"a": "1", "b": "2"} → concat("a1b2") based on independent verification using .
        """
        # ARRANGE
        data = {"b": "2", "a": "1"}  # different insertion order
        expected = "85337816D263D362ACB23A4255A636191075C2A90C47F2EE6DB3362F7DF11203"  # SHA256("a1b2").upper()

        # ACT
        result = jio._compute_payload_sha256(data)

        # ASSERT
        with self.subTest(Out=result, Exp=expected):
            self.assertEqual(result, expected)

    def test_order_independence(self):
        """
        Should produce identical hash regardless of dict insertion order.
        """
        # ARRANGE
        data_a = {"x": "10", "a": "Z", "m": "7"}
        data_b = {"m": "7", "x": "10", "a": "Z"}  # same pairs, different order

        # ACT
        result_a = jio._compute_payload_sha256(data_a)
        result_b = jio._compute_payload_sha256(data_b)

        # ASSERT
        with self.subTest(Out=result_a, Exp=result_b):
            self.assertEqual(result_a, result_b)

    def test_utf8(self):
        """
        Should correctly hash UTF-8 content. Example: {"Δ": "é", "a": "1"} → concat("a1Δé").
        """
        # ARRANGE
        data = {"Δ": "é", "a": "1"}  # sorted keys: "a", "Δ" → "a1Δé"
        expected = "81840CFFD7C0887838BA7B8E65E6EC2AA15A9243C1CB2DEDF131710C1E5EE033"  # SHA256("a1Δé").upper()

        # ACT
        result = jio._compute_payload_sha256(data)

        # ASSERT
        with self.subTest(Out=result, Exp=expected):
            self.assertEqual(result, expected)

    def test_empty(self):
        """
        Should equal SHA-256 of empty string when payload is {}.
        """
        # ARRANGE
        data = {}
        expected = "E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855"  # SHA256("").upper()

        # ACT
        result = jio._compute_payload_sha256(data)

        # ASSERT
        with self.subTest(Out=result, Exp=expected):
            self.assertEqual(result, expected)

    def test_stringification(self):
        """
        Should stringify non-string values before concatenation.

        Example: {"x": 10, "y": True} → concat("x10yTrue").
        """
        # ARRANGE
        data = {"x": 10, "y": True}
        expected = "8FB6798C3A7699067328977CF29EDDCFCEE1E9F56A832216A3B4C661B9461C1D"  # SHA256("x10yTrue").upper()

        # ACT
        result = jio._compute_payload_sha256(data)

        # ASSERT
        with self.subTest(Out=result, Exp=expected):
            self.assertEqual(result, expected)


class TestCreateJsonPacket(unittest.TestCase):
    """
    Unit test for the `create_json_packet` function.
    """

    def test_builds_packet_with_meta_and_payload(self):
        """
        Should build a JSON packet with meta (timestamp, source, checksum) and shallow copy of payload.
        """
        # ARRANGE
        payload = {"a": 1, "b": "two"}
        source_file = "example.csv"

        fake_timestamp = "2025-09-06T12:00:00Z"
        fake_checksum = "A591A6D40BF420404A011733CFB7B190D62C65BF0BCDA32B57B277D9AD9F146E"

        expected_payload = dict(payload)  # shallow copy
        expected_meta = {
            jio._KEY_UTC: fake_timestamp,
            jio._KEY_SOURCE: source_file,
            jio._KEY_SHA256: fake_checksum,
        }

        # Patch helper functions to control outputs
        with patch("src.utils._json_io._now_utc_iso", return_value=fake_timestamp), \
                patch("src.utils._json_io._compute_payload_sha256",
                      return_value=fake_checksum):
            # ACT
            result = jio.create_json_packet(payload, source_file)

        # ASSERT
        # Verify meta fields
        for field, expected_value in expected_meta.items():
            result_value = result[jio._KEY_META][field]
            with self.subTest(Field=field, Out=result_value, Exp=expected_value):
                self.assertEqual(result_value, expected_value)

        # Verify payload is a shallow copy (same keys/values, but not the same object)
        with self.subTest(Out=result[jio._KEY_PAYLOAD], Exp=expected_payload):
            self.assertEqual(result[jio._KEY_PAYLOAD], expected_payload)
            self.assertIsNot(result[jio._KEY_PAYLOAD], payload)


class TestDictToJsonString(unittest.TestCase):
    """
    Unit tests for the `dict_to_json_string` function.

    This test ensures that:
      1) A dictionary with string keys is correctly serialized to JSON.
      2) Pretty-printing indentation is applied when `indent_spaces` is provided.
      3) Unicode characters are preserved (ensure_ascii=False).
      4) Serialization errors are wrapped in a `RuntimeError` with a descriptive message.
    """

    def test_serialization(self):
        """
        Should serialize a simple dictionary with string keys into a JSON string.
        """
        # ARRANGE
        input_dict = {"name": "Alice", "age": 30}
        expected = json.dumps(input_dict, ensure_ascii=False)

        # ACT
        result = jio.dict_to_json_string(input_dict)

        # ASSERT
        with self.subTest(Out=result, Exp=expected):
            self.assertEqual(result, expected)

    def test_with_indentation(self):
        """
        Should serialize with indentation when indent_spaces is provided.
        """
        # ARRANGE
        input_dict = {"city": "Paris", "population": 2148327}
        indent_spaces = 4
        expected = json.dumps(input_dict, indent=indent_spaces, ensure_ascii=False)

        # ACT
        result = jio.dict_to_json_string(input_dict, indent_spaces=indent_spaces)

        # ASSERT
        with self.subTest(Out=result, Exp=expected):
            self.assertEqual(result, expected)

    def test_unicode(self):
        """
        Should preserve Unicode characters without escaping.
        """
        # ARRANGE
        input_dict = {"greeting": "こんにちは"}  # Japanese for "Hello"
        expected = json.dumps(input_dict, ensure_ascii=False)

        # ACT
        result = jio.dict_to_json_string(input_dict)

        # ASSERT
        with self.subTest(Out=result, Exp=expected):
            self.assertEqual(result, expected)

    def test_non_serializable(self):
        """
        Should raise RuntimeError when dictionary contains non-serializable values.
        """
        # ARRANGE
        input_dict = {"callback": lambda x: x}  # Functions are not JSON serializable
        expected_error = RuntimeError.__name__

        # ACT
        try:
            jio.dict_to_json_string(input_dict)
            result = ""
        except Exception as e:
            result = type(e).__name__

        # ASSERT
        with self.subTest(Out=result, Exp=expected_error):
            self.assertEqual(result, expected_error)


class TestJsonStringToDict(unittest.TestCase):
    """
    Unit tests for the `json_string_to_dict` function.

    This suite verifies that valid JSON strings are deserialized into Python
    dictionaries and that malformed JSON raises a `RuntimeError`. Tests focus
    strictly on input→output behavior implemented in the function body (i.e.,
    calling `json.loads` and wrapping exceptions) without asserting implied
    validations not present in the function.
    """

    def test_deserialization(self):
        """
        Should parse a compact JSON object string into an equivalent Python dict.
        """
        # ARRANGE
        json_str = '{"name":"Alice","age":30,"active":true}'
        expected = {"name": "Alice", "age": 30, "active": True}

        # ACT
        result = jio.json_string_to_dict(json_str)

        # ASSERT
        with self.subTest(Out=result, Exp=expected):
            self.assertEqual(result, expected)

    def test_with_whitespace_and_newlines(self):
        """
        Should ignore whitespace/newlines and parse to the same dict.
        """
        # ARRANGE
        json_str = """
        {
            "city": "Paris",
            "population": 2148327,
            "co-ords": { "lat": 48.8566, "lon": 2.3522 }
        }
        """
        # Use Python literal for clarity and to avoid duplicating parsing logic
        expected = {
            "city": "Paris",
            "population": 2148327,
            "co-ords": {"lat": 48.8566, "lon": 2.3522},
        }

        # ACT
        result = jio.json_string_to_dict(json_str)

        # ASSERT
        with self.subTest(Out=result, Exp=expected):
            self.assertEqual(result, expected)

    def test_unicode(self):
        """
        Should correctly parse and preserve Unicode characters.
        """
        # ARRANGE
        json_str = '{"greeting":"こんにちは","emoji":"😀","currency":"€"}'
        expected = {"greeting": "こんにちは", "emoji": "😀", "currency": "€"}

        # ACT
        result = jio.json_string_to_dict(json_str)

        # ASSERT
        with self.subTest(Out=result, Exp=expected):
            self.assertEqual(result, expected)

    def test_nested_structures(self):
        """
        Should parse nested dicts and arrays exactly as represented.
        """
        # ARRANGE
        json_str = json.dumps(
            {
                "user": {"id": 1, "roles": ["admin", "editor"]},
                "flags": {"beta": True, "notifications": {"email": False, "sms": True}},
            },
            ensure_ascii=False,
        )
        expected = {
            "user": {"id": 1, "roles": ["admin", "editor"]},
            "flags": {"beta": True, "notifications": {"email": False, "sms": True}},
        }

        # ACT
        result = jio.json_string_to_dict(json_str)

        # ASSERT
        with self.subTest(Out=result, Exp=expected):
            self.assertEqual(result, expected)

    def test_invalid_json(self):
        """
        Should raise RuntimeError when JSON string is malformed.
        """
        # ARRANGE
        # Trailing comma makes this JSON invalid
        invalid_json = '{"a": 1, "b": 2,}'

        expected_error = RuntimeError.__name__

        # ACT
        try:
            jio.json_string_to_dict(invalid_json)
            result = ""  # No exception raised (unexpected)
        except Exception as e:
            # Verify the wrapped exception type name only (no reliance on message format)
            result = type(e).__name__

        # ASSERT
        with self.subTest(Out=result, Exp=expected_error):
            self.assertEqual(result, expected_error)


class TestLoadJsonFile(unittest.TestCase):
    """
    Unit tests for the `load_json_file` function.

    This suite verifies that a JSON file is read and deserialized into a Python
    dictionary, and that errors are wrapped in a RuntimeError when the file is
    missing, unreadable, or contains invalid JSON.
    """

    def setUp(self):
        """
        Create a temporary directory for test artifacts.
        """
        self.tmpdir = tempfile.mkdtemp(prefix="json_load_test_")
        self.file_path = os.path.join(self.tmpdir, "test.json")

    def tearDown(self):
        """
        Remove any temporary files/directories created during tests.
        """
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_load_valid_json_file(self):
        """
        Should read and parse a valid JSON file into the expected dictionary.
        """
        # ARRANGE
        expected = {"name": "Alice", "age": 30, "active": True}
        with open(self.file_path, mode="w", encoding="utf-8") as f:
            json.dump(expected, f, ensure_ascii=False)  # type: ignore[arg-type]

        # ACT
        result = jio.load_json_file(self.file_path)

        # ASSERT
        with self.subTest(Out=result, Exp=expected):
            self.assertEqual(result, expected)

    def test_load_json_with_unicode(self):
        """
        Should correctly parse JSON containing Unicode characters.
        """
        # ARRANGE
        expected = {"greeting": "こんにちは", "emoji": "😀", "currency": "€"}
        with open(self.file_path, mode="w", encoding="utf-8") as f:
            json.dump(expected, f, ensure_ascii=False)  # type: ignore[arg-type]

        # ACT
        result = jio.load_json_file(self.file_path)

        # ASSERT
        with self.subTest(Out=result, Exp=expected):
            self.assertEqual(result, expected)

    def test_invalid_json_file(self):
        """
        Should raise RuntimeError if the file contains invalid JSON.
        """
        # ARRANGE
        with open(self.file_path, mode="w", encoding="utf-8") as f:
            f.write('{"a": 1, "b": 2,}')  # Invalid trailing comma
        expected_error = RuntimeError.__name__

        # ACT
        try:
            jio.load_json_file(self.file_path)
            result = ""  # No exception raised
        except Exception as e:
            result = type(e).__name__

        # ASSERT
        with self.subTest(Out=result, Exp=expected_error):
            self.assertEqual(result, expected_error)

    def test_missing_file(self):
        """
        Should raise RuntimeError if the file does not exist.
        """
        # ARRANGE
        missing_path = os.path.join(self.tmpdir, "missing.json")
        expected_error = RuntimeError.__name__

        # ACT
        try:
            jio.load_json_file(missing_path)
            result = ""  # No exception raised
        except Exception as e:
            result = type(e).__name__

        # ASSERT
        with self.subTest(Out=result, Exp=expected_error):
            self.assertEqual(result, expected_error)


class TestSaveJsonFile(unittest.TestCase):
    """
    Unit tests for the `save_json_file` function.

    This suite verifies that a dictionary is serialized and saved to disk as JSON,
    that optional indentation is honored, that Unicode is preserved (ensure_ascii=False),
    and that errors are wrapped in `RuntimeError` for non-serializable data or invalid paths.

    Tests follow Arrange–Act–Assert and focus on input→output/side-effect behavior defined
    in the function body (writing JSON text to a file using `json.dump` with `ensure_ascii=False`).
    """

    def setUp(self):
        """Create a temporary directory for test artifacts."""
        self.tmpdir = tempfile.mkdtemp(prefix="save_json_test_")
        self.file_path = os.path.join(self.tmpdir, "out.json")

    def tearDown(self):
        """Remove any temporary files/directories created during tests."""
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_valid_json_compact(self):
        """
        Should write a compact JSON file when indent_spaces=None.
        """
        # ARRANGE
        data = {"name": "Alice", "age": 30, "active": True}
        expected_text = json.dumps(data, indent=None, ensure_ascii=False)

        # ACT
        jio.save_json_file(self.file_path, data, indent_spaces=None)

        # ASSERT
        with open(self.file_path, mode="r", encoding="utf-8") as f:
            written_text = f.read()
        with self.subTest(Out=written_text, Exp=expected_text):
            self.assertEqual(written_text, expected_text)

        # Also confirm round-trip parses to the same dict
        parsed = json.loads(written_text)
        with self.subTest(Out=parsed, Exp=data):
            self.assertEqual(parsed, data)

    def test_with_indent(self):
        """
        Should write pretty-printed JSON when indent_spaces is provided.
        """
        # ARRANGE
        data = {"city": "Paris", "population": 2148327}
        indent_spaces = 4
        expected_text = json.dumps(data, indent=indent_spaces, ensure_ascii=False)

        # ACT
        jio.save_json_file(self.file_path, data, indent_spaces=indent_spaces)

        # ASSERT
        with open(self.file_path, mode="r", encoding="utf-8") as f:
            written_text = f.read()
        with self.subTest(Out=written_text, Exp=expected_text):
            self.assertEqual(written_text, expected_text)

        parsed = json.loads(written_text)
        with self.subTest(Out=parsed, Exp=data):
            self.assertEqual(parsed, data)

    def test_unicode(self):
        """
        Should preserve Unicode characters without escaping (ensure_ascii=False).
        """
        # ARRANGE
        data = {"greeting": "こんにちは", "emoji": "😀", "currency": "€"}
        # The exact bytes should match json.dumps with ensure_ascii=False
        expected_text = json.dumps(data, ensure_ascii=False, indent=2)

        # ACT
        jio.save_json_file(self.file_path, data, indent_spaces=2)

        # ASSERT
        with open(self.file_path, mode="r", encoding="utf-8") as f:
            written_text = f.read()
        with self.subTest(Out=written_text, Exp=expected_text):
            self.assertEqual(written_text, expected_text)

        # Additionally ensure characters are present literally (not escaped)
        contains_unicode = all(s in written_text for s in ["こんにちは", "😀", "€"])
        with self.subTest(Out=contains_unicode, Exp=True):
            self.assertTrue(contains_unicode)

    def test_non_serializable(self):
        """
        Should raise RuntimeError when data contains non-serializable values.
        """
        # ARRANGE
        data = {"callback": lambda x: x}  # Functions are not JSON-serializable
        expected_error = RuntimeError.__name__

        # ACT
        try:
            jio.save_json_file(self.file_path, data)
            result = ""  # No exception raised (unexpected)
        except Exception as e:
            result = type(e).__name__

        # ASSERT
        with self.subTest(Out=result, Exp=expected_error):
            self.assertEqual(result, expected_error)

    def test_missing_parent_directory(self):
        """
        Should raise RuntimeError when the target directory does not exist.
        """
        # ARRANGE
        missing_dir_path = os.path.join(self.tmpdir, "does_not_exist", "out.json")
        expected_error = RuntimeError.__name__

        # ACT
        try:
            jio.save_json_file(missing_dir_path, {"a": 1})
            result = ""  # No exception raised (unexpected)
        except Exception as e:
            result = type(e).__name__

        # ASSERT
        with self.subTest(Out=result, Exp=expected_error):
            self.assertEqual(result, expected_error)


class TestParseStrictKeyValueToDict(unittest.TestCase):
    """
    Unit tests for the `parse_strict_key_value_to_dict` function in `src.utils.json`.

    This suite verifies that a quoted key–value configuration text is parsed into a
    dictionary when lines conform to the strict `"Key" = "Value"` format, while:
      - Ignoring empty lines and comment-only lines.
      - Stripping trailing comments introduced by `#`.
      - Skipping invalid lines without failing.
      - Raising an error on duplicate keys.

    Scope: Tests focus strictly on input→output behavior implemented in the function,
    without asserting on logging/printing side effects for invalid lines.
    """

    def test_basic_parsing(self):
        """
        Should parse multiple valid lines into a dictionary.
        """
        # ARRANGE
        src = "config.txt"
        text = (
            '"Name" = "Alice"\n'
            '"City" = "Paris"\n'
            '"Age" = "30"\n'
        )
        expected = {"Name": "Alice", "City": "Paris", "Age": "30"}

        # ACT
        result = jio.parse_strict_key_value_to_dict(src, text)

        # ASSERT
        with self.subTest(Out=result, Exp=expected):
            self.assertEqual(result, expected)

    def test_trailing_comments_and_whitespace(self):
        """
        Should strip trailing comments and surrounding whitespace before validation.
        """
        # ARRANGE
        src = "cfg.conf"
        text = (
            '   "KeyA"   =   "Value A"    # trailing comment\n'
            '"KeyB"="Value B"#another comment\n'
            '"KeyC" = ""   # empty string value is allowed\n'
        )
        expected = {"KeyA": "Value A", "KeyB": "Value B", "KeyC": ""}

        # ACT
        result = jio.parse_strict_key_value_to_dict(src, text)

        # ASSERT
        with self.subTest(Out=result, Exp=expected):
            self.assertEqual(result, expected)

    def test_ignores_comments_and_empty_lines(self):
        """
        Should ignore blank lines and lines that are comments (including those reduced to empty after '#').
        """
        # ARRANGE
        src = "settings.kv"
        text = (
            "\n"
            "# Full-line comment\n"
            '   # Indented full-line comment\n'
            '"Mode" = "Prod"\n'
            '   # comment only after spaces\n'
            '"Level" = "High"  # keep this\n'
            "   \n"
            " # another (indented) comment line\n"
        )
        expected = {"Mode": "Prod", "Level": "High"}

        # ACT
        result = jio.parse_strict_key_value_to_dict(src, text)

        # ASSERT
        with self.subTest(Out=result, Exp=expected):
            self.assertEqual(result, expected)

    def test_invalid_lines_are_skipped(self):
        """
        Should skip non-conforming lines and keep only valid `"Key" = "Value"` entries.
        """
        # ARRANGE
        src = "bad_lines.txt"
        text = (
            'Key = "no_quotes_on_key"\n'  # invalid (key not quoted)
            '"NoEquals"  "MissingEquals"\n'  # invalid (no equals)
            '"Good" = "Yes"\n'  # valid
            '"AlsoGood"="True"\n'  # valid
            '"Bad" = "Unclosed\n'  # invalid (unterminated quote)
        )
        expected = {"Good": "Yes", "AlsoGood": "True"}

        with patch("builtins.print"):  # mock to suppress print output in unit test
            # ACT
            result = jio.parse_strict_key_value_to_dict(src, text)

            # ASSERT
            with self.subTest(Out=result, Exp=expected):
                self.assertEqual(result, expected)

    def test_duplicate_keys_raises(self):
        """
        Should raise RuntimeError if the same key appears more than once.
        """
        # ARRANGE
        src = "dupe.cfg"
        text = (
            '"A" = "1"\n'
            '"B" = "2"\n'
            '"A" = "3"\n'  # duplicate key: "A"
        )
        expected_error = RuntimeError.__name__

        # ACT
        try:
            jio.parse_strict_key_value_to_dict(src, text)
            result = ""  # No exception raised (unexpected)
        except Exception as e:
            result = type(e).__name__

        # ASSERT
        with self.subTest(Out=result, Exp=expected_error):
            self.assertEqual(result, expected_error)

    def test_all_whitespace_and_trailing_comment_only_lines(self):
        """
        Should ignore lines that become empty after stripping trailing comments and whitespace.
        """
        # ARRANGE
        src = "comments_only.txt"
        text = (
            "   # just a comment\n"
            "\t  # another comment with leading whitespace\n"
            '"K" = "V"   # valid with trailing comment\n'
            "   #\n"
        )
        expected = {"K": "V"}

        # ACT
        result = jio.parse_strict_key_value_to_dict(src, text)

        # ASSERT
        with self.subTest(Out=result, Exp=expected):
            self.assertEqual(result, expected)

    def test_value_empty_string_is_allowed(self):
        """
        Should allow empty quoted values (`""`) and parse them as empty strings.
        """
        # ARRANGE
        src = "empty_value.cfg"
        text = '"Empty" = ""\n"NonEmpty" = "x"'
        expected = {"Empty": "", "NonEmpty": "x"}

        with patch("builtins.print"):  # mock to suppress print output in unit test
            # ACT
            result = jio.parse_strict_key_value_to_dict(src, text)

            # ASSERT
            with self.subTest(Out=result, Exp=expected):
                self.assertEqual(result, expected)


class TestNowUtcIso(unittest.TestCase):
    """
    Unit tests for the `now_utc_iso` function in `src.utils.json`.

    This suite verifies that the function:
      - Returns an ISO 8601 timestamp string with a 'Z' UTC suffix.
      - Is precise to the second (no microseconds present).
      - Produces a time value consistent with the current UTC time at call.
    """

    def test_format_and_suffix(self):
        """
        Should return a string in the exact 'YYYY-MM-DDTHH:MM:SSZ' format with 'Z' suffix.
        """
        # ARRANGE
        iso_regex = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")

        # ACT
        result = jio._now_utc_iso()

        # ASSERT
        # Type check
        with self.subTest(Out=type(result).__name__, Exp=str.__name__):
            self.assertIsInstance(result, str)

        # Ends with 'Z'
        with self.subTest(Out=result.endswith("Z"), Exp=True):
            self.assertTrue(result.endswith("Z"))

        # Exact length "YYYY-MM-DDTHH:MM:SSZ" == 20 chars
        with self.subTest(Out=len(result), Exp=20):
            self.assertEqual(len(result), 20)

        # 'T' separator at the expected index (10)
        with self.subTest(Out=result[10], Exp="T"):
            self.assertEqual(result[10], "T")

        # Matches strict ISO pattern with Z suffix
        with self.subTest(Out=bool(iso_regex.match(result)), Exp=True):
            self.assertTrue(iso_regex.match(result) is not None)

        # No microseconds or explicit offset in the string
        with self.subTest(Out=("." in result), Exp=False):
            self.assertNotIn(".", result)
        with self.subTest(Out=("+00:00" in result), Exp=False):
            self.assertNotIn("+00:00", result)

    def test_value_within_current_utc_bounds(self):
        """
        Should produce a timestamp that falls between the UTC instants captured
        immediately before and after the call (inclusive), at second precision.
        """
        # ARRANGE
        # Capture lower bound (truncate to seconds)
        lower = datetime.now(timezone.utc).replace(microsecond=0)

        # ACT
        text_ts = jio._now_utc_iso()

        # Capture upper bound (truncate to seconds)
        upper = datetime.now(timezone.utc).replace(microsecond=0)

        # Convert back to aware UTC datetime for comparison
        parsed = datetime.strptime(text_ts, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)

        # ASSERT
        # Ensure parsed time is between lower and upper (inclusive)
        with self.subTest(Out=parsed.isoformat(),
                          Exp=f"[{lower.isoformat()} .. {upper.isoformat()}]"):
            self.assertLessEqual(lower, parsed)
            self.assertLessEqual(parsed, upper)

    def test_second_precision_no_microseconds(self):
        """
        Should represent time with second-level precision only (no microseconds).
        """
        # ARRANGE & ACT
        text_ts = jio._now_utc_iso()
        parsed = datetime.strptime(text_ts, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)

        # ASSERT
        with self.subTest(Out=parsed.microsecond, Exp=0):
            self.assertEqual(parsed.microsecond, 0)


class TestVerifyJsonPayloadChecksum(unittest.TestCase):
    """
    Unit tests for `verify_json_payload_checksum`
    """

    def test_int_checksum(self):
        """
        Should return True when int checksum stored in metadata matches the computed checksum of the payload.
        """
        # ARRANGE
        data = {"a": "1", "b": "2", "Δ": "é"}  # Realistic sample including Unicode
        checksum = jio._compute_payload_sha256(data)
        obj = {jio._KEY_META: {jio._KEY_SHA256: checksum}, jio._KEY_PAYLOAD: data}
        expected = True

        # ACT
        result = jio.verify_json_payload_checksum(obj)

        # ASSERT
        with self.subTest(Out=result, Exp=expected):
            self.assertEqual(result, expected)

    def test_string_checksum(self):
        """
        Should return True when str checksum stored in metadata matches the computed checksum of the payload.
        """
        # ARRANGE
        data = {"x": 10, "y": True,
                "z": "ok"}  # Non-string values get stringified in checksum helper
        checksum = jio._compute_payload_sha256(data)
        obj = {jio._KEY_META: {jio._KEY_SHA256: checksum}, jio._KEY_PAYLOAD: data}
        expected = True

        # ACT
        result = jio.verify_json_payload_checksum(obj)

        # ASSERT
        with self.subTest(Out=result, Exp=expected):
            self.assertEqual(result, expected)

    def test_payload_tamper(self):
        """
        Should return False if payload data changes after checksum was computed and stored.
        """
        # ARRANGE
        original_data = {"k1": "v1", "k2": "v2"}
        checksum = jio._compute_payload_sha256(original_data)

        # Create object but tamper the data (simulate drift) without updating checksum
        obj = {jio._KEY_META: {jio._KEY_SHA256: checksum}, jio._KEY_PAYLOAD: {"k1": "v1", "k2": "v2X"}}
        expected = False

        # ACT
        result = jio.verify_json_payload_checksum(obj)

        # ASSERT
        with self.subTest(Out=result, Exp=expected):
            self.assertEqual(result, expected)

    def test_incorrect_metadata_checksum(self):
        """
        Should return False if the stored checksum does not match the computed checksum.
        """
        # ARRANGE
        data = {"alpha": "A", "beta": "B"}
        not_data = {"one": "1", "two": "2"} # Not the same as data
        incorrect_checksum = jio._compute_payload_sha256(not_data)
        obj = {jio._KEY_META: {jio._KEY_SHA256: incorrect_checksum}, jio._KEY_PAYLOAD: data}
        expected = False

        # ACT
        result = jio.verify_json_payload_checksum(obj)

        # ASSERT
        with self.subTest(Out=result, Exp=expected):
            self.assertEqual(result, expected)


class TestExtractPayload(unittest.TestCase):
    """
    Unit tests for `extract_payload`.
    """

    def test_new_equal_dict(self):
        """
        Should return a new dict equal in content, not the same object identity.
        """
        # ARRANGE
        packet = {jio._KEY_PAYLOAD: {"a": 1, "b": 2}}
        expected = {"a": 1, "b": 2}

        # ACT
        result = jio.extract_payload(packet)

        # ASSERT
        with self.subTest(Out=isinstance(result, dict), Exp=True):
            self.assertIsInstance(result, dict)

        with self.subTest(Out=result, Exp=expected):
            self.assertEqual(result, expected)

        with self.subTest(Out=(result is packet[jio._KEY_PAYLOAD]), Exp=False):
            self.assertIsNot(result, packet[jio._KEY_PAYLOAD])

    def test_shallow_copy_semantics(self):
        """
        Should behave as a shallow copy:
          - Top-level mutations on the returned dict do not affect the source.
          - Nested objects remain shared (mutations reflect in both).
        """
        # ARRANGE
        nested = {"count": 1}
        packet = {jio._KEY_PAYLOAD: {"x": 10, jio._KEY_META: nested}}
        original_top_level = copy.deepcopy(packet[jio._KEY_PAYLOAD])  # Snapshot of original top-level

        # ACT
        result = jio.extract_payload(packet)

        # Mutate top-level of result (add a new key)
        result["y"] = 99

        # Mutate a nested shared object from result
        result[jio._KEY_META]["count"] = 42

        # ASSERT
        # Top-level addition should NOT appear in source (different dict objects)
        with self.subTest(Out=("y" in packet[jio._KEY_PAYLOAD]), Exp=False):
            self.assertNotIn("y", packet[jio._KEY_PAYLOAD])

        # Nested mutation should reflect in both (since nested object is shared in shallow copy)
        with self.subTest(Out=packet[jio._KEY_PAYLOAD][jio._KEY_META]["count"], Exp=42):
            self.assertEqual(packet[jio._KEY_PAYLOAD][jio._KEY_META]["count"], 42)

        # Unchanged original keys remain intact aside from intentional nested change
        with self.subTest(Out=packet[jio._KEY_PAYLOAD]["x"], Exp=original_top_level["x"]):
            self.assertEqual(packet[jio._KEY_PAYLOAD]["x"], original_top_level["x"])

    def test_accepts_mapping_convertible_value(self):
        """
        Should accept a `payload['data']` value that can be converted to a dict (e.g., list of pairs).
        """
        # ARRANGE
        packet = {jio._KEY_PAYLOAD: [("a", "1"), ("b", "2")]}
        expected = {"a": "1", "b": "2"}

        # ACT
        result = jio.extract_payload(packet)

        # ASSERT
        with self.subTest(Out=result, Exp=expected):
            self.assertEqual(result, expected)


if __name__ == "__main__":
    unittest.main()
