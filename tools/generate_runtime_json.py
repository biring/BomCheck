"""
Generate runtime JSON files from colocated *.txt key=value sources.

This module provides:
    - Discovery of `.txt` sources next to the script
    - Strict parsing of key=value content into a dict
    - Construction of per-source `<basename>.json` outputs
    - Wrapping the payload with metadata/checksum
    - Exit codes suitable for use in build or CI scripts

Common use cases include seeding runtime lookup tables, configuration stubs,
and small data dictionaries that should be packaged as JSON at build time.

Example Usage:
    # Preferred usage via package/module import:
    from tools.generate_runtime_foundations import generate_runtime_json_from_txt_sources
    generate_runtime_json_from_txt_sources()

    # Direct CLI usage (from repo root or the script's directory):
    python -m tools.generate_runtime_foundations
    or:
    python tools/generate_runtime_foundations.py

Dependencies:
    - Python >= 3.10
    - Standard Library: os, sys
    - Internal Modules: src.utils.directory, src.utils.file, src.utils.text, src.utils.json

Notes:
    - Input format is STRICT `"key"="value"` per line; parsing failures raise exceptions.
    - Output directory is resolved as `<project_root>/src/runtime`; this tool does not create the directory if missing.
    - File name and extension validation are enforced via `src.utils.file`.
    - JSON payload wrapper is produced by `create_json_packet`, which embeds metadata (e.g., source filename) and a checksum over the data.
    - Returns:
         *  0 on success (all files processed)
         *  1 if one or more files failed
         * -1 if no sources are found or the runtime directory is missing

License:
 - Internal Use Only
"""

import os
import sys

import src.utils as utils

# CONSTANTS
DEST_FOLDER = ("src", "runtime",)


def main() -> int:
    # Discover *.txt sources colocated with this script
    source_dir = os.path.dirname(os.path.abspath(__file__))
    source_filenames = utils.get_files_in_directory(source_dir, list(utils.TEXT_FILE_TYPE))
    if not source_filenames:
        print(f"No '{utils.TEXT_FILE_TYPE}' source files found in {source_dir}")
        return -1

    # Resolve and validate the runtime output directory
    project_root = utils.find_root_folder()
    runtime_dir = utils.construct_folder_path(project_root, DEST_FOLDER)
    if not utils.is_folder_path(runtime_dir):
        print(f"Missing runtime folder structure {DEST_FOLDER} under project root: {project_root}")
        return -1

    exit_code = 0
    for source_filename in source_filenames:
        print(f"Processing: {source_filename}")
        try:
            # Build and validate full input path
            source_path = utils.build_file_path(source_dir, source_filename)
            utils.assert_filename_with_extension(source_path, utils.TEXT_FILE_TYPE)

            # Build and validate full output path
            dest_filename = source_filename.rsplit(".", 1)[0] + utils.JSON_FILE_EXT
            dest_path = utils.build_file_path(runtime_dir, dest_filename)
            utils.assert_filename_with_extension(dest_path, utils.JSON_FILE_EXT)

            # Load and parse strict key/value content
            raw_text = utils.load_text_file(source_path)
            kv_map = utils.parse_strict_key_value_to_dict(source_path, raw_text)

            # Create JSON packet and persist it
            payload = utils.create_json_packet(kv_map, source_filename)
            utils.save_json_file(dest_path, payload)

            print(f"Created: {dest_filename} ({len(kv_map)} keys)")
        except Exception as ex:
            # Include exception type and source path for faster triage
            print(f'Error processing "{source_filename}" '
                  f'[{type(ex).__name__}]: {ex}', file=sys.stderr)
            exit_code = 1

    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
