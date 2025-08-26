"""
Validators for Version 3 BOM cell values (fail‑fast assertions).

This module enforces strict value formats and ranges for individual cells in the V3 BOM template. Each function raises `ValueError` with contextual details when validation fails to keep upstream parsing and rule checks clean.

Commonly used during BOM ingestion prior to schema/rule evaluation.

Example Usage:
    # Preferred usage via public package interface:
    # Not exposed publicly; this is an internal module.

    # Direct module usage (acceptable in unit tests or internal scripts only):
    import src.rules._v3_cell_value as cv
    cv.assert_board_name("Main Control PCBA")d

Dependencies:
    - Python: >= 3.9
    - Standard Library: re
    - Internal: src.utils.parser

Notes:
    - Fail-fast philosophy: each function raises `ValueError` with a precise hint.
    - Assumes upstream text normalization (e.g., trimming) has already occurred.
    - Date validation delegates to `src.utils.parser.parse_to_iso_date_string`; time components (e.g., 'YYYY-MM-DD HH:MM') are tolerated—only the date part is enforced.
    - Empty-string allowances are intentional for certain fields:
         * price: "" or float >= 0.0
         * item: "" or positive integer
         * classification: "" or one of A/B/C
    - Internal module: `__all__` is empty; these functions are not part of the public API. Prefer package‑level re‑exports if/when provided.

License:
 - Internal Use Only
"""

__all__ = []  # Internal-only; not part of public API

import re
import src.utils.parser as p

# REGULAR EXPRESSIONS
_RE_BOARD_NAME = re.compile(r'^[A-Za-z][A-Za-z0-9 ]*PCBA$')
_RE_BUILD_STAGE = re.compile(r'^(?:P\d+(?:\.\d+)?|EB\d+(?:\.\d+)?|ECN\d*|MP|MB|FOT)$')
_RE_MODEL_NUMBER = re.compile(r'^[A-Za-z]+[0-9]+[A-Za-z]*$')
_RE_CLASSIFICATION = re.compile(f'^[ABC]?$')

# MODULE CONSTANTS
_INFO_BOARD_NAME: str = "Correct board name starts with a letter, contain only letters, digits, and spaces, and end with 'PCBA' (uppercase, exact)."
_INFO_BUILD_STAGE: str = "Correct build stage formats are Pn, Pn.n, EBn, EBn.n, MB, MP and ECNn."
_INFO_CLASSIFICATION: str = "Correct classification is A, B, C or empty value. "
_INFO_MODEL_NUMBER: str = "Correct model number starts with letters, followed by digits, and may optionally end with letters."
_INFO_PRICE: str = "Correct price is greater than or equal to 0.0"
_INFO_QTY: str = "Correct quantity is greater than or equal to 0.0"
_INFO_ITEM: str = "Correct item is empty or greater than or equal to 1"
_ERR_INVALID_VALUE: str = "'{x}' is not correct. "


def assert_model_number(model_number_str: str) -> None:
    """
    Assert that the input value is a valid model number.

    A valid model number must start with letters, followed by digits, and optionally end with additional letters.

    Args:
        model_number_str (str): The string to validate as a model number.

    Returns:
        None: Succeeds silently if valid.

    Raises:
        ValueError: If the input string does not match the model number pattern.
    """
    if not _RE_MODEL_NUMBER.fullmatch(str(model_number_str)):
        raise ValueError(_ERR_INVALID_VALUE.format(x=model_number_str) + _INFO_MODEL_NUMBER)


def assert_board_name(board_name_str: str) -> None:
    """
    Assert that the input value is a valid board name.

    A valid board name must start with a letter, may contain letters, digits, and spaces, and must end exactly with 'PCBA' (uppercase).

    Args:
        board_name_str (str): The string to validate as a board name.

    Returns:
        None: Succeeds silently if valid.

    Raises:
        ValueError: If the value does not match the required pattern.
    """
    if not _RE_BOARD_NAME.fullmatch(str(board_name_str)):
        raise ValueError(_ERR_INVALID_VALUE.format(x=board_name_str) + _INFO_BOARD_NAME)


def assert_build_stage(build_stage_str: str) -> None:
    """
    Assert that the input value is a valid build stage label.

    Accepted formats include:
        - Pn or Pn.n
        - EBn or EBn.n
        - ECN or ECNn
        - MB, MP, FOT

    Args:
        build_stage_str (str): The string to validate as build stage string.

    Returns:
        None: Succeeds silently if valid.

    Raises:
        ValueError: If the value does not match the required pattern.
    """
    if not _RE_BUILD_STAGE.fullmatch(str(build_stage_str)):
        raise ValueError(_ERR_INVALID_VALUE.format(x=build_stage_str) + _INFO_BUILD_STAGE)


def assert_date_format(date_str: str) -> None:
    """
    Assert that the value is a valid date in one of the allowed formats.

    Allowed exact formats (zero-padded where applicable):
        - YYYY-MM-DD
        - DD/MM/YYYY
        - MM/DD/YYYY

    If a time component is present (e.g., '2025-08-06T12:30' or '2025-08-06 12:30'), only the date portion before 'T' or space is checked.

    Args:
        date_str (str): The string to validate as date.

    Returns:
        None: Succeeds silently if valid.

    Raises:
        ValueError: If the value does not parse to any allowed exact format.
    """
    try:
        p.parse_to_iso_date_string(date_str)
    except ValueError as err:
        raise ValueError(_ERR_INVALID_VALUE.format(x=date_str) + f"{err}") from err


def assert_price(price_str: str) -> None:
    """
    Assert that the input value is a valid price.

    Valid price is empty string, or greater than and equal to zero floats (e.g., "0", "0.00",  "0.12", "12.5"). Negative number or string inputs are invalid price.

    Args:
        price_str (str): The string to validate as price.

    Returns:
        None: Succeeds silently if valid.

    Raises:
        ValueError: If the value is not a float >= 0.0.
    """
    if p.is_strict_empty_string(price_str):
        return
    if p.is_float(price_str):
        if p.parse_to_float(price_str) >= 0.0:
            return

    raise ValueError(_ERR_INVALID_VALUE.format(x=price_str) + _INFO_PRICE)


def assert_qty(qty_str: str) -> None:
    """
    Assert that the input value is a valid quantity.

    This check accepts zero or strictly positive floats (e.g., "0", "1", "3.75"). Negative values and non-float inputs fail.

    Args:
        qty_str (str): The string to validate as quantity.

    Returns:
        None: Succeeds silently if valid.

    Raises:
        ValueError: If the value is not a float >= 0.0.
    """
    if p.is_float(qty_str):
        if p.parse_to_float(qty_str) >= 0.0:
            return

    raise ValueError(_ERR_INVALID_VALUE.format(x=qty_str) + _INFO_QTY)


def assert_item(item_str: str) -> None:
    """
    Assert that the item string represents a valid item.

    A valid item must be an empty string ("") or positive integer (e.g., "1", "42"). Any other value raises an error.

    Args:
        item_str (str): The string to validate as Item.

    Returns:
        None: Succeeds silently if valid.

    Raises:
        ValueError: If the value is neither empty nor a positive integer.
    """
    if p.is_strict_empty_string(item_str):
        return

    if p.is_integer(item_str):
        if p.parse_to_integer(item_str) > 0:
            return

    raise ValueError(_ERR_INVALID_VALUE.format(x=item_str) + _INFO_ITEM)


def assert_classification(classification_str: str) -> None:
    """
    Assert that the classification string is a valid classification

    A valid classification is A, B, C or empty string

    Args:
        classification_str: The string to validate as Classification.

    Returns:
          None: Succeeds silently if valid.

    Raises:
          ValueError: If the value is not valid
    """
    if not _RE_CLASSIFICATION.fullmatch(classification_str):
        raise ValueError(_ERR_INVALID_VALUE.format(x=classification_str) + _INFO_CLASSIFICATION)
