"""
Generate runtime JSON files from colocated *.txt key=value sources.

This module provides:
    - Discovery of sources files defined in `DATA_LOCATION`
    - Strict parsing of key=value content into a dict
    - Construction of per-source `_<basename>.json` outputs
    - Wrapping the payload with metadata/checksum
    - Exit codes suitable for use in build or CI scripts

Common use cases include seeding runtime lookup tables, configuration stubs, and small data dictionaries that should be packaged as JSON at build time.

Example Usage:
    # Preferred usage via package/module import:
    Not applicable. Not for use with other modules.

    # Direct CLI usage (from repo root or the script's directory):
    python -m tools/generate_runtime_json.py
    or:
    python tools/generate_runtime_json.py

Dependencies:
    - Python >= 3.10
    - Standard Library: os, sys
    - Internal Modules: src.utils

Notes:
    - Input format is STRICT `"key"="value"` per line; parsing failures raise exceptions.
    - Output directory is resolved as `<project_root>/src/runtime`; this tool does not create the directory if missing.
    - File name and extension validation are enforced via `src.utils.file`.
    - JSON payload wrapper is produced by `create_json_packet`, which embeds metadata (e.g., source filename) and a checksum over the data.
    - Returns:
         *  0 on success (all files processed)
         * -1 if any generation failed

License:
 - Internal Use Only
"""

import sys
from dataclasses import dataclass

import src.utils as utils

from src.runtime import interfaces as rt

# TODO - make this import via utility interface
# noinspection PyProtectedMember
from src.utils._json_io import _compute_payload_sha256 as sha256 # import of private function is acceptable for tools


@dataclass(frozen=True)
class FileLocation:
    source_folder_path: tuple[str, ...]
    source_file_name: str
    destination_folder_path: tuple[str, ...]


# CONSTANTS
SUCCESS: int = 0
FAILURE: int = -1
TOOLS_FOLDER: tuple[str, ...] = ("tools", )
RUNTIME_FILE_PREFIX: str = rt.RUNTIME_JSON_PREFIX
DATA_LOCATION: tuple[FileLocation, ...] = (
    FileLocation(TOOLS_FOLDER, rt.COMPONENT_TYPE_SOURCE, rt.RUNTIME_FOLDER),
)


def main() -> int:
    project_root = utils.find_root_folder()

    overall_success = True

    print(f"🛠️ Generating runtime JSON files from project location {project_root}")

    for data in DATA_LOCATION:

        print(f"🧪 Processing {data.source_file_name}")
        try:
            # Build source file path
            source_file_name = data.source_file_name + utils.TEXT_FILE_TYPE
            source_folder_path = utils.construct_folder_path(project_root, data.source_folder_path)
            source_file_path = utils.build_file_path(source_folder_path, source_file_name)

            # Verify source file name
            utils.assert_filename_with_extension(source_file_path, utils.TEXT_FILE_TYPE)

            # Verify source file exists
            if not utils.is_existing_file_path(source_file_path):
                raise FileNotFoundError(f"⚠️ Source file missing: {source_file_path}. Create source file to process.")

            # Build destination file path
            dest_file_name = RUNTIME_FILE_PREFIX + source_file_name.rsplit(".", 1)[0] + utils.JSON_FILE_EXT
            dest_folder_path = utils.construct_folder_path(project_root, data.destination_folder_path)
            dest_file_path = utils.build_file_path(dest_folder_path, dest_file_name)

            # Verify destination file name
            utils.assert_filename_with_extension(dest_file_path, utils.JSON_FILE_EXT)

            # Verify destination file folder exists
            if not utils.is_folder_path(dest_folder_path):
                raise RuntimeError("⚠️ Destination folder missing: {dest_folder_path}. This tool does not create directories.")

            # Warn user when creating new destination file
            if not utils.is_existing_file_path(dest_file_path):
                print(f"⚠️ Destination file missing: {dest_file_name}. This tool will create a new file.")

            # Load and parse strict key/value content
            raw_text = utils.load_text_file(source_file_path)
            new_kv_map = utils.parse_strict_key_value_to_dict(source_file_path, raw_text)
            new_sha256 = sha256(new_kv_map)

            # Compare with existing payload if present
            existing_kv_map = None
            try:
                json_package = utils.load_json_file(dest_file_path)
                existing_kv_map = utils.extract_payload(json_package)
                existing_sha256 = sha256(existing_kv_map)
                if new_sha256 == existing_sha256:
                    print(f"⏭️ Skipping {data.source_file_name}. No change detected.")
                    continue
            except FileNotFoundError:
                # No prior file: proceed to create
                pass
            except RuntimeError:
                # Can not load file: proceed to overwrite
                pass
            except Exception as ex:
                # Corrupt/unexpected JSON: log and proceed to regenerate
                print(f"⚠️ Existing JSON invalid at {dest_file_path}. {type(ex).__name__}: {ex}", file=sys.stderr)

            # Create JSON packet and persist it
            payload = utils.create_json_packet(new_kv_map, source_file_name)
            utils.save_json_file(dest_file_path, payload)  # consider sort_keys=True
            created_or_updated = "Created" if existing_kv_map is None else "Updated"
            print(f"✅ {created_or_updated}: {dest_file_name} ({len(new_kv_map)} keys)")

        except Exception as ex:
            print(f'❌ Error processing {data.source_file_name}. {type(ex).__name__}: {ex}', file=sys.stderr)
            overall_success = False
            # continue to next file instead of aborting immediately

    if overall_success:
        print("🎉 All runtime JSON files generated successfully.")
    else:
        print("⚠️ Some files failed to generate. See errors above.", file=sys.stderr)

    return SUCCESS if overall_success else FAILURE


if __name__ == "__main__":
    raise SystemExit(main())
