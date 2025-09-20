"""
Regular expression rules and error message templates for validating BOM fields.

This module centralizes compiled regex patterns and descriptive rule strings for
Bill of Materials (BOM) fields.

Main capabilities:
    - Provide compiled regex patterns for BOM fields (MODEL_NUMBER, BOARD_NAME, etc.)
    - Provide descriptive rule strings for user-facing validation errors
    - Serve as a single source of truth for validation across parsers and checkers

Example Usage:
    # Internal use only (not part of public API):
    from . import _constants as constants
    if not constants.MODEL_NUMBER_PATTERN.fullmatch("AB1234C"):
        print(constants.MODEL_NUMBER_RULE.format(a="Model No", b="AB1234C"))

Dependencies:
    - Python >= 3.9
    - Standard Library: re

Notes:
    - Intended for internal use within the `rules` package as a shared validation layer.
    - Patterns are compiled once and treated as constants; do not mutate at runtime.
    - Rule strings are templates meant to be formatted with `{a}` = field name, `{b}` = value.
    - Business logic (which field uses which rule) should remain in higher-level code.

License:
    - Internal Use Only
"""
__all__ = []  # Internal-only; not part of public API. Star import gets nothing.

import re

GENERIC_VALUE_ERROR_MSG: str = "Invalid '{a}' = '{b}'. "

MODEL_NUMBER_RULE: str = "Correct '{a}' starts with 2–3 capital letters, followed by 3–4 digits, and may optionally end with up 0-3 capital letters."

MODEL_NUMBER_PATTERN = re.compile(r'^[A-Z]{2,3}[0-9]{3,4}[A-Z]{0,3}$')

BOARD_NAME_RULE: str = (
    "Correct '{a}' starts with a letter, contains only letters, digits, and spaces, "
    "and ends with 'PCBA' (uppercase, exact)."
)

BOARD_NAME_PATTERN = re.compile(r'^[A-Za-z][A-Za-z0-9 ]*PCBA$')

BOARD_SUPPLIER_RULE: str = (
    "Correct '{a}' starts with a capital letter, may contain letters, digits, and spaces, "
    "and should be at least 3 characters long."
)

BOARD_SUPPLIER_PATTERN = re.compile(r'^[A-Z][A-Za-z0-9 ]{2,}$')

BUILD_STAGE_RULE: str = "Correct '{a}' formats are Pn, Pn.n, EBn, EBn.n, MB, MP, ECN, ECNn, or FOT."

BUILD_STAGE_PATTERN = re.compile(r'^(?:P\d+(?:\.\d+)?|EB\d+(?:\.\d+)?|ECN\d*|MP|MB|FOT)$')

COST_RULE: str = "Correct '{a}' is a positive number"

COST_PATTERN = re.compile(r'^(?:[0-9]+(?:\.[0-9]*)?|\.[0-9]+)$')
