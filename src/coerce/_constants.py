"""
Predefined regex-based coercion rules and field-specific rule sets for BOM headers.

This module centralizes reusable `Rule` objects (defined in `_common`) that normalize common BOM text patterns, including spacing, punctuation, and prefix cleanup. It also groups rules into field-specific lists for model numbers, board names/suppliers, build stages, dates, and cost fields.

Example Usage:
    # Preferred usage via package interface:
    # Not exposed publicly; this is an internal module.

    # Direct usage (internal scripts or units tests only):
    from src.rules.coerce import _constants as constant, _common as common
    result = common.coerce_text("ab 123x ", constant.MODEL_NUMBER)
    print(result.value_out)  # "AB123X"

Dependencies:
    - Python >= 3.9
    - Internal: src.rules.coerce._common.Rule

Notes:
    - Each `Rule` defines a regex pattern, replacement, and descriptive message.
    - Rules are designed to be idempotent and composable for sequential application.
    - This module is internal; public API calls should go through coercer functions.

License:
    - Internal Use Only
"""
__all__ = []  # Internal-only; not part of public API. Star import from this module gets nothing.

from src.coerce import _common as common

# General transformations
TO_UPPER = common.Rule(r"(.*)", lambda m: m.group(0).upper(), "Converted to uppercase.")

# Handle Chinese punctuation variants
CHINESE_COMMA = common.Rule(r"[，]", ",", "Converted Chinese comma to ASCII comma.")
CHINESE_LEFT_PAREN = common.Rule(r"[（]", "(", "Converted Chinese left parenthesis to ASCII (.")
CHINESE_RIGHT_PAREN = common.Rule(r"[）]", ")", "Converted Chinese right parenthesis to ASCII ).")
CHINESE_SEMICOLON = common.Rule(r"[；]", ";", "Converted Chinese semicolon to ASCII ;.")
CHINESE_COLON = common.Rule(r"[：]", ":", "Converted Chinese colon to ASCII :.")

# Remove known manufacturer prefixes
REMOVE_PREFIX_MANUFACTURER = common.Rule(r"(?i)^MANUFACTURER", " ", "Removed MANUFACTURER prefix (case-insensitive).")
REMOVE_PREFIX_MANU = common.Rule(r"(?i)^MANU", " ", "Removed MANU prefix (case-insensitive).")
REMOVE_PREFIX_MFG = common.Rule(r"(?i)^MFG", " ", "Removed MFG prefix (case-insensitive).")

# Whitespace normalization
REMOVE_NON_SPACE_WHITES = common.Rule(r"[\t\n\r\f\v]+", "", "Removed whitespace (tabs, newlines, etc.) but preserved spaces.")
REMOVE_ALL_WHITESPACES = common.Rule(r"\s+", "", "Removed all whitespace (spaces, tabs, newlines).")
REMOVE_ASCII_SPACES = common.Rule(r" +", "", "Removed all spaces.")

# Punctuation to comma
NEWLINE_TO_COMMA = common.Rule(r"\n", ",", "Replaced newline with comma.")
COLON_TO_COMMA = common.Rule(r"[:]", ",", "Replaced colon with comma.")
SEMICOLON_TO_COMMA = common.Rule(r"[;]", ",", "Replaced semicolon with comma.")
SPACE_TO_COMMA = common.Rule(r"[ ]", ",", "Replaced space with comma.")
STRIP_LEADING_COMMA = common.Rule(r"^,+", "", "Removed leading commas.")
STRIP_TRAILING_COMMA = common.Rule(r",+$", "", "Removed trailing commas.")
COLLAPSE_MULTIPLE_COMMAS = common.Rule(r",{2,}", ",", "Collapsed multiple commas into one.")

# Punctuation to space
COLON_TO_SPACE = common.Rule(r"[:]", " ", "Replaced colon with space.")
DOT_TO_SPACE = common.Rule(r"[.]", " ", "Replaced dot '.' with space.")
DOT_COMMA_TO_SPACE = common.Rule(r"\.,", " ", "Replaced '.,' with space (e.g., 'Co.,Ltd' → 'Co Ltd').")
NBSP_TO_SPACE = common.Rule(r"\u00A0", " ", "Replaced non-breaking space with normal space.")
STRIP_EDGE_SPACES = common.Rule(r"^ +| +$", "", "Removed leading and trailing spaces.")
COLLAPSE_MULTIPLE_SPACES = common.Rule(r" {2,}", " ", "Collapsed multiple spaces into one.")

# model_no
MODEL_NUMBER: list = [
    TO_UPPER,
    REMOVE_ASCII_SPACES,
]
# board_name
BOARD_NAME: list = [
    COLLAPSE_MULTIPLE_SPACES,
    STRIP_EDGE_SPACES,
]
# manufacturer
BOARD_SUPPLIER: list = [
    COLLAPSE_MULTIPLE_SPACES,
    STRIP_EDGE_SPACES,

]
# build_stage
BUILD_STAGE: list = [
    REMOVE_ASCII_SPACES,
]
# date
BOM_DATE: list = [
    REMOVE_ASCII_SPACES,
]
# material_cost
MATERIAL_COST: list = [
    REMOVE_ASCII_SPACES,
]
# overhead_cost
OVERHEAD_COST: list = [
    REMOVE_ASCII_SPACES,
]
# total_cost
TOTAL_COST: list = [
    REMOVE_ASCII_SPACES,
]
