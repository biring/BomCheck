"""
Test fixtures for rules package unit tests.

Provides reusable, well-typed GOOD_/BAD_ string constants for header field validation. Use these to keep tests concise, deterministic, and aligned with validator behavior.

Example Usage:
    from tests.fixtures import rows as fx
    assert MODEL_REGEX.fullmatch(fx.MODEL_NO_GOOD_1)

Dependencies:
    - Python >= 3.10
    - Standard Library: typing

Notes:
    - Constants are immutable and typed with Final[str]; do not mutate in tests.
    - Names use GOOD_/BAD_ prefixes to make intent obvious at call sites.
    - Keep values synchronized with current regex rules to avoid brittle tests.
    - Fixtures are minimal yet representative; add new cases only when required by behavior changes.

License:
    - Internal Use Only
"""

from typing import Final
from src.models.interfaces import Header

# GOOD model numbers (they satisfy the regex)
MODEL_NO_GOOD_1: Final[str] = "AB100"  # 2 letters + 3 digits
MODEL_NO_GOOD_2: Final[str] = "AB123EU"  # 2 letters + 3 digits + 2 trailing letters
MODEL_NO_GOOD_3: Final[str] = "ABC1234"  # 3 letters + 4 digits
MODEL_NO_GOOD_4: Final[str] = "AB123X"  # 2 letters + 3 digits + 1 trailing letter
MODEL_NO_GOOD_5: Final[str] = "ABC100ZZ"  # 3 letters + 3 digits + 2 trailing letters
MODEL_NO_GOOD_6: Final[str] = "AB123"  # 2 letters + 3 digits, no trailing letters
# BAD model numbers (they fail the regex for specific reasons)
MODEL_NO_BAD_1: Final[str] = "100"  # does not start with 2–3 capital letters
MODEL_NO_BAD_2: Final[str] = "123AB"  # starts with digits, not letters
MODEL_NO_BAD_3: Final[str] = "AB"  # only 2 letters, missing digits
MODEL_NO_BAD_4: Final[str] = "123"  # no leading letters
MODEL_NO_BAD_5: Final[str] = "A_123"  # contains underscore, only A–Z allowed
MODEL_NO_BAD_6: Final[str] = "AB-123"  # contains hyphen, not allowed
MODEL_NO_BAD_7: Final[str] = ""  # empty string
MODEL_NO_BAD_8: Final[str] = "   "  # spaces only
MODEL_NO_BAD_9: Final[str] = "X9Y"  # only 1 digit, needs 3–4
MODEL_NO_BAD_10: Final[str] = "Model42X"  # lowercase letters not allowed
MODEL_NO_BAD_11: Final[str] = "A1"  # 1 letter + 1 digit, too short
MODEL_NO_BAD_12: Final[str] = "abc123xyz"  # lowercase letters, not allowed

# GOOD board names (they satisfy the regex)
BOARD_NAME_GOOD_1: Final[str] = "Power PCBA"  # starts with letter, ends with PCBA
BOARD_NAME_GOOD_2: Final[str] = "Control PCBA"  # valid middle content, correct suffix
BOARD_NAME_GOOD_3: Final[str] = "Brushless motor main PCBA"  # spaces and words allowed
BOARD_NAME_GOOD_4: Final[str] = "Main board 2 PCBA"  # digits allowed in middle, valid ending
BOARD_NAME_GOOD_5: Final[str] = "A PCBA"  # single letter prefix, ends correctly
# BAD board names (they fail the regex for specific reasons)
BOARD_NAME_BAD_1: Final[str] = "Power"  # missing required 'PCBA' suffix
BOARD_NAME_BAD_2: Final[str] = "1Control PCBA"  # starts with digit, must start with letter
BOARD_NAME_BAD_3: Final[str] = "Control pcbA"  # wrong case on suffix, must be exact 'PCBA'
BOARD_NAME_BAD_4: Final[str] = "Control-PCBA"  # hyphen not allowed, only letters/digits/spaces
BOARD_NAME_BAD_5: Final[str] = "Control"  # missing 'PCBA' suffix
BOARD_NAME_BAD_6: Final[str] = " Control PCBA"  # starts with space, must start with letter
BOARD_NAME_BAD_7: Final[str] = "Power PCB left"  # does not end with 'PCBA'
BOARD_NAME_BAD_8: Final[str] = ""  # empty string
BOARD_NAME_BAD_9: Final[str] = "   "  # spaces only

# GOOD board supplier names (match regex)
BOARD_SUPPLIER_GOOD_1: Final[str] = "ABC"  # 3 uppercase letters
BOARD_SUPPLIER_GOOD_2: Final[str] = "Ab1"  # capital + lowercase + digit
BOARD_SUPPLIER_GOOD_3: Final[str] = "Intel123"  # starts with capital, letters + digits
BOARD_SUPPLIER_GOOD_4: Final[str] = "X9Y"  # capital + digit + letter
BOARD_SUPPLIER_GOOD_5: Final[str] = "Sony 2025"  # contains space, valid format
BOARD_SUPPLIER_GOOD_6: Final[str] = "General Electric"  # multiple words with spaces
BOARD_SUPPLIER_GOOD_7: Final[str] = "Bosch Ltd"  # capitalized with space
BOARD_SUPPLIER_GOOD_8: Final[str] = "A B C"  # multiple single-letter words, valid length
# BAD board supplier names (fail regex)
BOARD_SUPPLIER_BAD_1: Final[str] = "abc"  # starts with lowercase
BOARD_SUPPLIER_BAD_2: Final[str] = "12AB"  # starts with digit
BOARD_SUPPLIER_BAD_3: Final[str] = "AB"  # only 2 characters, too short
BOARD_SUPPLIER_BAD_4: Final[str] = "A1"  # only 2 characters, too short
BOARD_SUPPLIER_BAD_5: Final[str] = "-ABC"  # starts with non-letter
BOARD_SUPPLIER_BAD_6: Final[str] = " ab1"  # starts with space
BOARD_SUPPLIER_BAD_7: Final[str] = ""  # empty string
BOARD_SUPPLIER_BAD_8: Final[str] = "A_"  # contains underscore, not allowed
BOARD_SUPPLIER_BAD_9: Final[str] = "Bosch-Group"  # hyphen not allowed
BOARD_SUPPLIER_BAD_10: Final[str] = "Panasonic!"  # exclamation mark not allowed

# GOOD build stage values (match regex)
BUILD_STAGE_GOOD_1: Final[str] = "P1"  # Pn form
BUILD_STAGE_GOOD_2: Final[str] = "P10.5"  # Pn.n form
BUILD_STAGE_GOOD_3: Final[str] = "EB2"  # EBn form
BUILD_STAGE_GOOD_4: Final[str] = "EB12.3"  # EBn.n form
BUILD_STAGE_GOOD_5: Final[str] = "MB"  # MB exact
BUILD_STAGE_GOOD_6: Final[str] = "MP"  # MP exact
BUILD_STAGE_GOOD_7: Final[str] = "FOT"  # FOT exact
BUILD_STAGE_GOOD_8: Final[str] = "ECN"  # ECN with no digits (allowed)
BUILD_STAGE_GOOD_9: Final[str] = "ECN1"  # ECN with digits
BUILD_STAGE_GOOD_10: Final[str] = "ECN123"  # ECN with multiple digits
# BAD build stage values (fail regex)
BUILD_STAGE_BAD_1: Final[str] = "P"  # missing digits
BUILD_STAGE_BAD_2: Final[str] = "EB"  # missing digits
BUILD_STAGE_BAD_3: Final[str] = "P1."  # trailing dot without digits
BUILD_STAGE_BAD_4: Final[str] = "EB2."  # trailing dot without digits
BUILD_STAGE_BAD_5: Final[str] = "ECN.1"  # dot not allowed after ECN
BUILD_STAGE_BAD_6: Final[str] = "ecn1"  # lowercase not allowed
BUILD_STAGE_BAD_7: Final[str] = "MP1"  # MP must be exact
BUILD_STAGE_BAD_8: Final[str] = "MB2"  # MB must be exact
BUILD_STAGE_BAD_9: Final[str] = "FOT1"  # FOT must be exact
BUILD_STAGE_BAD_10: Final[str] = ""  # empty string
BUILD_STAGE_BAD_11: Final[str] = " "  # whitespace only
BUILD_STAGE_BAD_12: Final[str] = "PX1"  # invalid prefix

# GOOD date samples (all normalize to "2025-08-06")
GOOD_BOM_DATE_1: Final[str] = "2025-08-06"  # YYYY-MM-DD (zero-padded)
GOOD_BOM_DATE_2: Final[str] = "2025-8-6"  # YYYY-M-D (non-zero-padded)
GOOD_BOM_DATE_3: Final[str] = "06/08/2025"  # DD/MM/YYYY (zero-padded)
GOOD_BOM_DATE_4: Final[str] = "6/8/2025"  # D/M/YYYY (non-zero-padded)
GOOD_BOM_DATE_5: Final[str] = "08/06/2025"  # MM/DD/YYYY (zero-padded)
GOOD_BOM_DATE_6: Final[str] = "8/6/2025"  # M/D/YYYY (non-zero-padded)
GOOD_BOM_DATE_7: Final[str] = "2025-08-06T12:30"  # date + time w/ 'T'
GOOD_BOM_DATE_8: Final[str] = "2025-08-06 09:15"  # date + time w/ space
# BAD date samples (unsupported formats / invalid calendar dates / junk)
BAD_BOM_DATE_1: Final[str] = "2025.01.01"  # dots not allowed
BAD_BOM_DATE_2: Final[str] = "2025/08/06"  # wrong separator for YYYY-MM-DD
BAD_BOM_DATE_3: Final[str] = "06-08-2025"  # wrong separator for DD/MM/YYYY
BAD_BOM_DATE_4: Final[str] = "2025-13-01"  # invalid month
BAD_BOM_DATE_5: Final[str] = "2025-00-10"  # invalid month
BAD_BOM_DATE_6: Final[str] = "2025-02-30"  # invalid day
BAD_BOM_DATE_7: Final[str] = "not-a-date"  # junk
BAD_BOM_DATE_8: Final[str] = ""  # empty
BAD_BOM_DATE_9: Final[str] = "   "  # whitespace only

# GOOD costs (valid by regex + float >= 0.0)
GOOD_COST_1: Final[str] = "0"  # integer zero
GOOD_COST_2: Final[str] = "0.00"  # zero with decimals
GOOD_COST_3: Final[str] = "0.12"  # cents precision
GOOD_COST_4: Final[str] = "12.5"  # single decimal
GOOD_COST_5: Final[str] = "100"  # whole number
GOOD_COST_6: Final[str] = "100.0"  # trailing .0 accepted
GOOD_COST_7: Final[str] = ".5"  # leading decimal without integer
GOOD_COST_8: Final[str] = "12."  # trailing dot
# BAD costs (fail regex or < 0)
BAD_COST_1: Final[str] = "-1"  # negative integer
BAD_COST_2: Final[str] = "-0.01"  # negative decimal
BAD_COST_3: Final[str] = "."  # just a dot, no digits
BAD_COST_4: Final[str] = "abc"  # non-numeric
BAD_COST_5: Final[str] = ""  # empty string
BAD_COST_6: Final[str] = " "  # whitespace only
BAD_COST_7: Final[str] = "1,000"  # comma not allowed
BAD_COST_8: Final[str] = "12.34.56"  # multiple decimals invalid

GOOD_HEADER_1: Final[Header] = Header(
    model_no="AB100", board_name="Power PCBA", manufacturer="Delta",
    build_stage="MB", date="01/12/2025", material_cost="2.0",
    overhead_cost="0.4", total_cost="2.4")
