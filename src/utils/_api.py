"""
Public API aggregator for the `utils` package.

This module defines and re-exports the curated, stable surface of `utils`. All symbols listed in `__all__` are imported from internal implementation modules (e.g., `_sanitizer`) and exposed here for external use.

Example Usage:
    # Preferred usage via the package interface:
    # Not exposed publicly; this is an internal module.

    # Direct module usage (intended for testing or internal tooling only):
    import src.utils._api as api
    text = api.normalize_spaces("A    B")

Dependencies:
    - Python >= 3.9
    - Standard Library: re, typing

Notes:
    - This module acts only as a stable facade; implementation lives in internal modules.
    - Keep this file logic-free to preserve clarity and predictable imports.
    - Public imports should always go through `src.utils` rather than `_api`.

License:
 - Internal Use Only

"""

# Import implementation symbols from internal modules

# noinspection PyProtectedMember
from ._console import (
    prompt_string_input,
)

# noinspection PyProtectedMember
from ._excel_io import (
    map_excel_sheets_to_string_dataframes,
    read_excel_file,
    sanitize_sheet_name_for_excel,
    write_frame_to_excel,
    write_sheets_to_excel,
)

# noinspection PyProtectedMember
from ._file_path import (
    TEXT_FILE_TYPE,
    EXCEL_FILE_TYPE,
    JSON_FILE_EXT,
    assert_filename_with_extension,
    build_file_path,
    escape_backslashes,
    get_files_in_directory,
    is_existing_file_path,
    is_valid_file_path,
)

# noinspection PyProtectedMember
from ._folder_path import (
    construct_folder_path,
    create_folder_if_missing,
    find_drive_letter,
    find_root_folder,
    is_folder_path,
    list_immediate_sub_folders,
    go_up_one_folder,
)

# noinspection PyProtectedMember
from ._json_io import (
    create_json_packet,
    dict_to_json_string,
    extract_payload,
    json_string_to_dict,
    load_json_file,
    parse_strict_key_value_to_dict,
    save_json_file,
    verify_json_payload_checksum,
)

# noinspection PyProtectedMember
from ._parser import (
    is_float,
    is_integer,
    is_non_empty_string,
    is_strict_empty_string,
    is_valid_date_string,
    parse_to_empty_string,
    parse_to_float,
    parse_to_integer,
    parse_to_iso_date_string,
    parse_to_non_empty_string,
)

# noinspection PyProtectedMember
from ._sanitizer import (
    normalize_spaces,
    normalize_to_string,
    remove_all_whitespace,
)

# noinspection PyProtectedMember
from ._text_io import (
    load_text_file,
    save_text_file,
)

# Define exactly what is public. __all__ is the single source of truth for the public API.
__all__ = [
    # console
    "prompt_string_input",

    # excel_io
    "map_excel_sheets_to_string_dataframes",
    "read_excel_file",
    "sanitize_sheet_name_for_excel",
    "write_frame_to_excel",
    "write_sheets_to_excel",

    # file_path
    "TEXT_FILE_TYPE",
    "EXCEL_FILE_TYPE",
    "JSON_FILE_EXT",
    "assert_filename_with_extension",
    "build_file_path",
    "escape_backslashes",
    "get_files_in_directory",
    "is_existing_file_path",
    "is_valid_file_path",

    # folder_path
    "construct_folder_path",
    "create_folder_if_missing",
    "find_drive_letter",
    "find_root_folder",
    "is_folder_path",
    "list_immediate_sub_folders",
    "go_up_one_folder",

    # json_io
    "create_json_packet",
    "dict_to_json_string",
    "extract_payload",
    "json_string_to_dict",
    "load_json_file",
    "parse_strict_key_value_to_dict",
    "save_json_file",
    "verify_json_payload_checksum",

    # parser
    "is_float",
    "is_integer",
    "is_non_empty_string",
    "is_strict_empty_string",
    "is_valid_date_string",
    "parse_to_empty_string",
    "parse_to_float",
    "parse_to_integer",
    "parse_to_iso_date_string",
    "parse_to_non_empty_string",

    # sanitizer
    "normalize_spaces",
    "normalize_to_string",
    "remove_all_whitespace",

    # text_io
    "load_text_file",
    "save_text_file",
]
