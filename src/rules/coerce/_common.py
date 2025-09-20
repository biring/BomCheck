"""
Regex-based coercion engine with traceable change logs.

This module provides helpers to apply regex-based transformations with traceable change logs. It is the shared engine used by BOM cell value coercers.

Example Usage:
    # Preferred usage via package interface:
    Not allowed. This is an internal module.

    # Direct internal usage (tests or internal scripts):
    from src.rules.coerce import _common as common
    rules = [common.Rule(r"\t+", " ", "Normalize whitespace")]
    res = common.apply_coerce("a\tb\nc", rules)

Dependencies:
 - Python >= 3.9
 - Standard Library: re, dataclasses, typing
 - External Packages: None

Notes:
 - Rules are applied in order; output of one becomes input to the next.
 - Logs are appended only when a rule changes the text.
 - This is an internal implementation detail; prefer the package façade when available.

License:
    - Internal Use Only
"""
__all__ = []  # Internal-only; not part of public API. Star import from this module gets nothing.

import re
from dataclasses import dataclass, field

from typing import Union, Callable, Match


@dataclass(frozen=True)
class Rule:
    """
    Represents a single regex-based coercion rule.

    Args:
        pattern (str): Regex pattern to match against input text.
        replacement (str | Callable[[Match[str]], str]): Replacement string or callable.
        msg (str): Human-readable description of the transformation.

    Raises:
        ValueError: If the regex pattern does not compile.
    """
    pattern: str
    replacement: Union[str, Callable[[Match[str]], str]]
    msg: str
    _compiled: re.Pattern | None = field(init=False, repr=False, default=None)

    def __post_init__(self):
        try:
            compiled = re.compile(self.pattern)
        except re.error as exc:
            raise ValueError(f"Invalid regex pattern in Rule: {self.pattern}") from exc
        object.__setattr__(self, "_compiled", compiled)


@dataclass(frozen=True)
class Log:
    """
    Records a single transformation event.

    Args:
        before (str): Input text before transformation (sanitized with _show).
        after (str): Output text after transformation (sanitized with _show).
        description (str): Descriptive message explaining the applied rule.
    """
    before: str
    after: str
    description: str


@dataclass
class Result:
    """
    Holds the outcome of applying one or more coercion rules.

    Args:
        value_in (str): Original input text.
        value_out (str): Final transformed output text.
        logs (list[Log]): List of logs describing applied transformations.
    """
    value_in: str = ""
    value_out: str = ""
    logs: list[Log] = field(default_factory=list)


def _show(s: str, max_len: int = 32) -> str:
    """
    Make invisible/control characters visible and truncate long strings.

    Args:
        s (str): Input string to render.
        max_len (int, optional): Maximum visible length. Defaults to 32.

    Returns:
        str: Safe, human-readable string for logging.
    """
    visible = s.replace("\n", "\\n").replace("\t", "\\t")
    if len(visible) > max_len:
        return visible[: max_len - 1] + "…"
    return visible


def apply_coerce(str_in: str, rules: list[Rule]) -> Result:
    """
    Apply a sequence of coercion rules to the input text.

    Each regex rule is applied in order. A log entry is created only if
    the rule makes at least one substitution.

    Args:
        str_in (str): The raw input string to transform.
        rules (list[Rule]): List of regex-based coercion rules.

    Returns:
        Result: The final output string with associated transformation logs.
    """
    result = Result(value_in=str_in, value_out="", logs=[])
    text_in = str_in
    text_out = str_in

    for rule in rules:
        # Apply the regex substitution
        text_out, count = re.subn(rule.pattern, rule.replacement, text_in)

        if count > 0:
            # Only log if the rule actually made a change
            log = Log(before=_show(text_in), after=_show(text_out), description=rule.msg)
            result.logs.append(log)

        # Carry forward output as input for next rule
        text_in = text_out

    result.value_out = text_out

    return result
