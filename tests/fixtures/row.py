"""
Test fixtures for rules package unit tests.

Provides reusable, well-typed GOOD_/BAD_ string constants for row field validation. Use these to keep tests concise, deterministic, and aligned with validator behavior.

Example Usage:
    from tests.fixtures import rows as fx
    assert MODEL_REGEX.fullmatch(fx.ITEM_GOOD_1)

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

# GOOD items (they satisfy the regex)
ITEM_GOOD: dict[str, str] = {
    "empty": "",  # empty string
    "smallest": "1",  # smallest positive integer
    "standard": "45",  # standard positive integer
    "large": "9999",  # large positive integer
}

# BAD items (they fail the regex for specific reasons)
ITEM_BAD: dict[str, str] = {
    "zero": "0",  # zero not allowed (not positive)
    "leading_zero": "012",  # leading zero not allowed
    "negative": "-5",  # negative not allowed
    "decimal": "3.14",  # decimal not allowed
    "letters": "abc",  # letters not allowed
    "whitespace": "   ",  # whitespace not allowed
}

# GOOD component types (they satisfy the regex)
COMP_TYPE_GOOD: dict[str, str] = {
    "simple": "Fuse",  # simple alphabetic word
    "acronym": "BJT",  # all caps letters
    "space": "Battery Terminal",  # two words with space
    "slash": "Diode/SCR",  # with '/'
    "alt_only": "ALT",  # keyword only
    "alt_one": "ALT1",  # keyword + digit
    "alt_multi": "ALT23",  # keyword + multiple digits
}
# BAD component types (they fail the regex for specific reasons)
COMP_TYPE_BAD: dict[str, str] = {
    "empty": "",  # empty string not allowed
    "digits_only": "123",  # digits only
    "alt_letters": "ALTXYZ",  # ALT must be digits only
    "invalid_char": "Fuse@",  # invalid char '@'
    "hyphen": "Battery-Terminal",  # hyphen not allowed
    "leading_space": " Diode",  # leading space not allowed
    "trailing_space": "SCR ",  # trailing space not allowed
    "double_slash": "Diode//SCR",  # double '/' not allowed
    "alt_space_digit": "ALT 1",  # space between ALT and digit not allowed
}

DEVICE_PACKAGE_GOOD: dict[str, str] = {
    "empty": "",  # empty string allowed
    "numeric": "0603",  # digits only
    "letters": "SMA",  # alphabets only
    "letters_digits": "QFN32",  # letters + numbers, no dash
    "letters_dash": "QFN-32",  # with dash
    "multi_dash": "BGA-256-X",  # multiple dashes
}

DEVICE_PACKAGE_BAD: dict[str, str] = {
    "space_inside": "QFN 32",  # space not allowed
    "leading_dash": "-QFN32",  # cannot start with dash
    "trailing_dash": "QFN32-",  # cannot end with dash
    "double_dash": "QFN--32",  # cannot have consecutive dashes
    "special_char": "QFN@32",  # special chars not allowed
    "underscore": "QFN_32",  # underscore not allowed
}

DESCRIPTION_GOOD: dict[str, str] = {
    "resistor": "1k,1%,0.5W",  # alphanumeric + commas + percent
    "capacitor": "1uF,10%,50V",  # unit + tolerance + voltage
    "diode": "Rectifier,1A,50V",  # word + ratings
    "complex": "MOSFET,N-CH,30V,10A",  # multiple segments
    "symbols": "IC,3.3V,100mA",  # includes dot and uppercase letters
}

DESCRIPTION_BAD: dict[str, str] = {
    "empty": "",  # empty string not allowed
    "space_inside": "1k, 1%, 0.5W",  # space between values
    "leading_space": " 1uF,10%,50V",  # leading whitespace
    "trailing_space": "1uF,10%,50V ",  # trailing whitespace
    "tab": "IC,\t3.3V,100mA",  # tab is whitespace
    "newline": "Rectifier,\n1A,50V",  # newline is whitespace
}

UNITS_GOOD: dict[str, str] = {
    "empty": "",  # empty string allowed
    "uppercase": "PCS",  # all uppercase letters
    "capitalized": "Each",  # standard word
    "lowercase": "grams",  # lowercase letters
    "with_dot": "lb.",  # optional trailing dot
}

UNITS_BAD: dict[str, str] = {
    "digits": "123",  # digits not allowed
    "letters_digits": "g2",  # mix of letters and digits not allowed
    "internal_dot": "g.ram",  # dot only allowed at the end
    "trailing_space": "PCS ",  # whitespace not allowed
    "leading_space": " Each",  # leading whitespace not allowed
    "special_char": "kg!",  # special character not allowed
}

CLASSIFICATION_GOOD: dict[str, str] = {
    "A": "A",  # allowed
    "B": "B",  # allowed
    "C": "C",  # allowed
}

CLASSIFICATION_BAD: dict[str, str] = {
    "empty": "",  # not allowed (must have one char)
    "lower_a": "a",  # lowercase not allowed
    "lower_b": "b",  # lowercase not allowed
    "lower_c": "c",  # lowercase not allowed
    "multi_chars": "AB",  # more than one character
    "digit": "1",  # digit not allowed
    "symbol": "#",  # special char not allowed
}

MFG_NAME_GOOD: dict[str, str] = {
    "letters_space": "ST Microelectronics",  # letters + space
    "letters_dot": "Delta Pvt. Ltd",  # with dot
    "letters_dash": "Hewlett-Packard",  # with dash
    "letters_amp": "Procter & Gamble",  # with ampersand
    "digits": "3M",  # digits + letters
    "letters_digits": "TI-89",  # mix of digits + dash + letters
}

MFG_NAME_BAD: dict[str, str] = {
    "empty": "",  # cannot be empty
    "leading_space": " STMicro",  # cannot start with space
    "trailing_space": "Intel ",  # cannot end with space
    "symbol": "Nokia@",  # invalid symbol '@'
    "underscore": "Micro_chip",  # underscore not allowed
}

MFG_PART_NO_GOOD: dict[str, str] = {
    "letters_digits": "LM358N",  # simple alphanumeric
    "dash": "SN74HC595N-TR",  # with dash
    "underscore": "AT328P_U",  # with underscore
    "dot": "ADXL345.B",  # with dot
    "combo": "XC7Z010-1CLG400C",  # realistic complex part number
    "letters_only": "BC547B",  # all letters and digits
}

MFG_PART_NO_BAD: dict[str, str] = {
    "empty": "",  # must not be empty
    "space_inside": "AT 328P",  # whitespace not allowed
    "leading_space": " LM358N",  # leading space
    "trailing_space": "BC547B ",  # trailing space
    "star": "Part*123",  # '*' not allowed
    "at_symbol": "SN74HC595N@TR",  # '@' not allowed
    "hash": "LM358#N",  # '#' not allowed
}
UL_VDE_NO_GOOD: dict[str, str] = {
    "single_letter": "E1234",  # 1 letter + digits
    "two_letters_space": "UL 567890",  # 2 letters + space + digits
    "three_letters_dash": "VDE-12345678",  # 3 letters + dash + 8 digits
    "four_letters": "ULVD123",  # 4 letters + digits
    "max_digits": "UL12345678",  # 2 letters + 8 digits, no separator
}

UL_VDE_NO_BAD: dict[str, str] = {
    "empty": "",  # not allowed
    "digits_only": "12345",  # must start with letters
    "letters_only": "ULVD",  # missing digits
    "too_many_letters": "ABCDE1234",  # >4 letters not allowed
    "too_many_digits": "UL123456789",  # >8 digits not allowed
    "double_separator": "UL--1234",  # only one separator allowed
    "wrong_separator": "UL_1234",  # underscore not allowed
    "space_and_dash": "UL- 1234",  # mixed separators not allowed
    "leading_space": " UL1234",  # cannot start with space
}

# GOOD validated-at strings (they satisfy the regex)
VALIDATED_AT_GOOD: dict[str, str] = {
    "empty": "",
    "P_simple": "P1",
    "P_zero": "P0",
    "P_decimal": "P12.3",
    "EB_simple": "EB0",
    "EB_decimal": "EB10.25",
    "ECN_bare": "ECN",
    "ECN_numbered": "ECN123",
    "MB": "MB",
    "MP": "MP",
    "FOT": "FOT",
    "slash_list": "P1/EB0/MP",
    "comma_list": "P2,ECN5,MB",
    "mixed_separators": "P10/EB2.1,ECN,MP/FOT",
    "long_mixed": "P3.2,EB1/P0,ECN,MB/FOT",
}

# BAD validated-at strings (they fail the regex for specific reasons)
VALIDATED_AT_BAD: dict[str, str] = {
    "space_inside": "P1 / EB0",  # whitespace not allowed
    "leading_sep": "/P1",  # cannot start with separator
    "trailing_sep": "P1/",  # cannot end with separator
    "double_slash": "P1//EB0",  # consecutive separators not allowed
    "double_comma": "P1,,EB0",  # consecutive separators not allowed
    "empty_token_between": "P1,/EB0",  # empty token between separators
    "wrong_sep_dot": "P1.EB0",  # '.' is not a valid separator
    "p_missing_digits": "P",  # P must be followed by digits
    "p_bad_decimal": "P.1",  # must be digits then optional .digits
    "p_two_dots": "P1.2.3",  # only one optional decimal part
    "eb_missing_digits": "EB",  # EB must be followed by digits
    "eb_bad_decimal": "EB1.",  # trailing dot not allowed
    "ecn_with_dash": "ECN-1",  # only digits allowed after ECN
    "ecn_with_dot": "ECN.1",  # dot not allowed after ECN
    "lowercase": "p1,eb0,ecn",  # tokens are case-sensitive
    "mb_with_number": "MB1",  # MB must be exact
    "mp_with_number": "MP0",  # MP must be exact
    "fot_with_number": "FOT1",  # FOT must be exact
    "invalid_prefix": "PX1",  # prefix must be P, EB, ECN, MB, MP, FOT
    "tab_inside": "P1\tEB0",  # any whitespace is invalid
}
QUANTITY_GOOD: dict[str, str] = {
    "zero": "0",  # smallest valid
    "single_digit": "2",  # simple integer
    "multi_digit": "123",  # larger integer
    "decimal_small": "0.34",  # decimal less than 1
    "decimal_large": "10.5",  # decimal greater than 1
    "decimal_multi": "2500.125",  # long decimal
}

QUANTITY_BAD: dict[str, str] = {
    "empty": "",  # must not be empty
    "negative": "-1",  # negatives not allowed
    "leading_zero": "01",  # no leading zeros (except '0')
    "just_dot": ".",  # dot alone not allowed
    "dot_no_fraction": "5.",  # must have digits after dot
    "dot_leading": ".25",  # must have leading digits
    "letters": "12A",  # letters not allowed
    "space_inside": "1 2",  # spaces not allowed
    "trailing_space": "3 ",  # trailing space not allowed
}

DESIGNATOR_GOOD: dict[str, str] = {
    "empty": "",  # allowed empty
    "letter_digit": "R1",  # 1 letter + digit
    "multi_letters_digits": "ACL123",  # up to 5 letters + digits
    "with_plus": "ACL+",  # letters + '+'
    "with_minus": "V-",  # letters + '-'
    "letters_only": "MP",  # letters only
    "max_letters_digits": "ABCDE12345",  # 5 letters + 5 digits
}

DESIGNATOR_BAD: dict[str, str] = {
    "digits_only": "123",  # must start with letters
    "too_many_letters": "ABCDEF1",  # >5 letters
    "too_many_digits": "R123456",  # >5 digits
    "letters_plus_digits_plus": "R1+",  # cannot have both digits and '+'
    "letters_plus_digits_minus": "C2-",  # cannot have both digits and '-'
    "double_plus": "R++",  # only single '+' or '-' allowed
    "special_char": "R1#",  # special chars not allowed
    "leading_space": " R1",  # whitespace not allowed
    "trailing_space": "C3 ",  # whitespace not allowed
}

PRICE_GOOD: dict[str, str] = {
    "zero": "0",  # smallest valid
    "integer": "2",  # simple integer
    "multi_digit": "123",  # larger integer
    "decimal_small": "0.34",  # decimal < 1
    "decimal_large": "10.5",  # decimal > 1
    "decimal_long": "2500.125",  # multi-digit decimal
}
PRICE_BAD: dict[str, str] = {
    "empty": "",  # must not be empty
    "negative": "-1",  # negatives not allowed
    "leading_zero": "01",  # no leading zeros (except '0')
    "just_dot": ".",  # dot alone not allowed
    "dot_no_fraction": "5.",  # must have digits after dot
    "dot_leading": ".25",  # must have leading digits
    "letters": "12A",  # letters not allowed
    "space_inside": "1 2",  # spaces not allowed
    "trailing_space": "3 ",  # trailing space not allowed
}
