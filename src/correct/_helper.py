"""
Shared helpers for BOM correction flows.

This module provides:
 - floats_equal: compare two floats using fixed precision and epsilon tolerance
 - generate_log_entry: build a one-line change log when a value changes
 - prompt_until_valid: standard CLI loop that shows info on first failure, warns on each invalid entry, and reprompts
 - levenshtein_match: find the closest match using Levenshtein string ratio
 - jaccard_match: find the closest match using character-level Jaccard similarity

Example Usage:
    # Preferred usage via package interface:
    # Not exposed publicly; this is an internal module.

    # Direct usage (internal scripts or unit tests only):
    import src.correct._common as common
    result = common.float_equals("1.3234", "1.32345")

Dependencies:
    - Python >= 3.10
    - Standard Library: typing
    - Project: src.cli.interfaces (for user prompts and messaging)

Notes:
    - Internal-only utilities; keep prompting, messaging, and tolerance settings centralized for consistent UX across correctors.
    - Pure logic aside from CLI calls in prompt_until_valid; floats_equal parameters (_DIGITS_OF_PRECISION, _EPSILON) define comparison strictness.
    - Recommended thresholds: Levenshtein 0.8–0.9, Jaccard 0.6–0.8 depending on string length and expected similarity.


License:
    - Internal Use Only
"""

__all__ = []  # Internal-only; not part of public API. Star import from this module gets nothing.

from typing import Callable
import Levenshtein
from src.cli import interfaces as cli

JACCARD_THRESHOLD = 0.70
LEVENSHTEIN_THRESHOLD = 0.85

_DIGITS_OF_PRECISION = 6  # Number of decimal places to round to before comparison.
_EPSILON = 1e-6  # Acceptable tolerance for equality after rounding. This helps absorb tiny floating-point noise.

TEMPLATE_CORRECTION_MSG = "'{field}' changed from '{before}' to '{after}'. {reason}"
TEMPLATE_CORRECTION_PROMPT = "Enter correct value for '{field}': "


def floats_equal(value_a: float, value_b: float) -> bool:
    """
    Compare two floating-point numbers for approximate equality.

    This function first rounds both numbers to a fixed number of decimal places (set by `_DIGITS_OF_PRECISION`). It then checks whether the absolute difference between the rounded values is smaller than a tolerance (`_EPSILON`).

    Args:
        value_a (float): The first value to compare.
        value_b (float): The second value to compare.

    Returns:
        bool: True if the two numbers are considered equal within the specified precision and tolerance, False otherwise.

    Raises:
        None

    Notes:
        - Use this helper instead of `==` when dealing with floats, since binary floating-point arithmetic can introduce very small errors.
        - Adjust `_DIGITS_OF_PRECISION` if you need more or fewer decimal places (e.g., 4 for four-decimal precision).
        - Adjust `_EPSILON` if you want stricter or looser tolerance.
    """
    # Round both numbers to the configured precision
    rounded_a = round(value_a, _DIGITS_OF_PRECISION)
    rounded_b = round(value_b, _DIGITS_OF_PRECISION)

    # Compute the absolute difference
    difference = abs(rounded_a - rounded_b)

    # Return True if within tolerance, False otherwise
    return difference < _EPSILON


def generate_log_entry(field: str, before: str, after: str, reason: str) -> str:
    """
    Build a one-line change log entry when a value changes; return empty string otherwise.

    Args:
        field (str): Field label being updated.
        before (str): Original value.
        after (str): New value.
        reason (str): Short rationale for the change.

    Returns:
        str: Formatted log entry if 'after' != 'before'; otherwise "".

    Raises:
        None
    """
    msg = ""

    # create log entry only when value changes
    if after != before:
        msg = TEMPLATE_CORRECTION_MSG.format(
            field=field,
            before=before,
            after=after,
            reason=reason
        )

    return msg


def prompt_until_valid(data: str, fn: Callable, value: str, field: str) -> str:
    """
    Prompt the user until the validator returns no error message; return the accepted value.

    Shows an optional context/info message once when the initial value is invalid, then loops: displays the validator's message as a warning, prompts the user, and re-validates. The validator 'fn' must accept a single string and return "" on success or an error message on failure.

    Args:
        data (str): Contextual info to display once when the first validation fails (e.g., sample or guidance).
        fn (Callable): Validator: (candidate: str) -> str; return "" if valid, else a human-readable error.
        value (str): Initial candidate value.
        field (str): Field label to use in the prompt.

    Returns:
        str: The first candidate that passes validation.

    Raises:
        None
    """
    value_out = value

    # Validate the initial value; if invalid, show context once to help the user correct it
    msg = fn(value_out)

    if msg:
        cli.show_info(data)

    # Loop until the validator returns "", prompting with a stable, field-specific message
    while msg:
        cli.show_warning(msg)
        # Keep the prompt template centralized to preserve consistent UX across fields
        prompt = TEMPLATE_CORRECTION_PROMPT.format(field=field)
        value_out = cli.prompt_for_string_value(prompt)
        msg = fn(value_out)

    return value_out


def levenshtein_match(test_string: str, reference_strings: tuple[str, ...],
                      ratio_threshold: float = LEVENSHTEIN_THRESHOLD) -> tuple[str, float]:
    """
    Find the best fuzzy match for a test string from a list of reference strings using Levenshtein ratio.

    Both the test string and reference strings are normalized to lowercase and stripped of leading/trailing spaces. The best match must exceed the provided ratio threshold to be returned.

    Args:
        test_string (str): Input string to match.
        reference_strings (tuple[str, ...]): List of candidate strings to compare against.
        ratio_threshold (float): Minimum acceptable Levenshtein ratio (0.0–1.0).

    Returns:
        tuple[str, float]: The best matching reference string and its ratio. Returns ("", 0.0) if no match meets the threshold.

    Raises:
        None
    """
    # Initialize variables to keep track of the best match and its distance
    best_match: str = ""
    best_ratio: float = 0.0  # start with the lowest possible ratio
    lower_test_string = test_string.lower().strip()

    # Loop through each reference string
    for ref_string in reference_strings:
        lower_ref_string = ref_string.lower().strip()
        # Compute the Levenshtein ratio between the test string and the current reference string
        match_ratio = Levenshtein.ratio(lower_test_string, lower_ref_string)
        # TODO debug log print(f'L = {match_ratio:2.2f} {test_string:20} {ref_string:20}')

        # If the distance is smaller than the current minimum distance, update the best match
        if match_ratio > ratio_threshold and match_ratio >= best_ratio:
            best_ratio = match_ratio
            best_match = ref_string

    # Return the best matching reference string
    return best_match, best_ratio


def jaccard_match(test_string: str, reference_strings: tuple[str, ...], similarity_threshold: float = JACCARD_THRESHOLD) -> \
        tuple[str, float]:
    """
    Find the best fuzzy match for a test string using character-level Jaccard similarity.

    The function compares the character sets of the test string and each reference string, returning the one with the highest similarity above the threshold.

    Args:
        test_string (str): The string to match.
        reference_strings (tuple[str, ...]): List of reference strings to evaluate.
        similarity_threshold (float): Minimum acceptable Jaccard similarity (0.0–1.0).

    Returns:
        tuple[str, float]: The best matching reference string and its similarity score. Returns ("", 0.0) if no candidate meets the threshold.

    Raises:
        None
    """
    best_match: str = ""
    best_similarity: float = 0.0
    set1 = set(test_string.lower().strip())

    # Iterate through each reference string
    for ref_string in reference_strings:
        # Compute Jaccard similarity coefficient
        set2 = set(ref_string.lower().strip())
        intersection = len(set1.intersection(set2))
        union = len(set1.union(set2))
        matching_similarity = 0.0
        if union > 0.0:  # protect against divide by zero
            matching_similarity = intersection / union
        # TODO - Debug log print(f'J = {matching_similarity:2.2f} {test_string:20} {ref_string:20}')

        # Update best match if similarity is higher
        if (matching_similarity > best_similarity) and (matching_similarity >= similarity_threshold):
            best_similarity = matching_similarity
            best_match = ref_string

    # Return the best matching reference string
    return best_match, best_similarity
