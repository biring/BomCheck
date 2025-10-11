"""
Regex-based coercion engine with traceable change logs.

This module provides helpers to apply regex-based transformations with traceable change logs. It is the shared engine used by BOM cell value coercers.

Example Usage:
    # Preferred usage via package interface:
    Not allowed. This is an internal module.

    # Direct internal usage (tests or internal scripts):
    from src.coerce import _common as common
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

    Encapsulates both the final coerced string and a trace of all transformations applied during the coercion process. Each transformation is logged with a before/after snapshot and description. This object is immutable once populated and is typically returned by `apply_coerce`.

    Args:
        attr_name (str): Attribute name associated with the coercion.
        value_in (str): Original input text before applying rules.
        value_out (str): Final transformed output text after all rules.
        logs (list[Log]): Ordered list of log entries describing applied changes.

    Returns:
        Result: A fully populated coercion outcome with logs for each effective rule.

    Raises:
        None
    """
    attr_name:str = ""
    value_in: str = ""
    value_out: str = ""
    logs: list[Log] = field(default_factory=list)

    def format_to_change_log(self) -> tuple[str, ...]:
        """
        Render human-readable change messages from a Result's logs.

        Returns:
            tuple[str, ...]: One formatted line per applied rule. Empty if no effective change.
        """
        formatted_logs: list[str] = []
        # Optional guard; keeps log empty if no effective change
        if self.value_in != self.value_out:
            msg_template = "'{a}' changed from '{b}' to '{c}'. {d}"
            for entry in self.logs:
                formatted_logs.append(
                    msg_template.format(a=self.attr_name, b=entry.before, c=entry.after, d=entry.description)
                )
        # Return immutable tuple for consistency
        return tuple(formatted_logs)


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


def apply_coerce(str_in: str, rules: list[Rule], attr_name: str) -> Result:
    """
    Apply a sequence of coercion rules to the input text.

    Each regex rule is applied in order. A log entry is created only if
    the rule makes at least one substitution.

    Args:
        str_in (str): The raw input string to transform.
        rules (list[Rule]): List of regex-based coercion rules.
        attr_name (str): Attribute name associated with the coercion.

    Returns:
        Result: The final output string with associated transformation logs.
    """
    result = Result(attr_name=attr_name, value_in=str_in, value_out="", logs=[])
    text_in = str_in
    text_out = str_in

    for rule in rules:
        # Apply the regex substitution
        text_out = re.sub(rule.pattern, rule.replacement, text_in)

        if text_out != text_in:
            # Only log if the rule actually made a change
            log = Log(before=_show(text_in), after=_show(text_out), description=rule.msg)
            result.logs.append(log)

        # Carry forward output as input for next rule
        text_in = text_out

    result.value_out = text_out

    return result

class CoerceLog:
    """
    Aggregates coercion for a current (file, sheet, section) context.

    Maintains contextual state so call sites avoid repeating file/sheet/section. Provides append and read helpers for simple, intention-revealing usage.

    Args:
        self

    Returns:
        None

    Raises:
        None
    """

    def __init__(self) -> None:
        self.file_name = ""
        self.sheet_name = ""
        self.section_name = ""
        self.entries: list[str] = []

    def set_file_name(self, file: str) -> None:
        """
        Set the active file context for subsequent coercions.

        Args:
            file (str): File name to associate with added coercions.

        Returns:
            None
     """
        self.file_name = file

    def set_sheet_name(self, sheet: str) -> None:
        """
        Set the active worksheet context for subsequent coercions.

        Args:
            sheet (str): Worksheet name to associate with added coercions.

        Returns:
            None
        """
        self.sheet_name = sheet

    def set_section_name(self, section: str) -> None:
        """
        Set the active section context for subsequent coercions.

        Args:
            section (str): Section or block name to associate with added coercions.

        Returns:
            None
        """
        self.section_name = section

    def add(self, message: str) -> None:
        """
        Add a single coercion message if it is a non-empty string after trimming.

        Args:
            message (str): Human-readable description of the coercion.

        Returns:
            None
        """
        if message:
            self.entries.append(message)

    def snapshot(self) -> tuple[str, ...]:
        """
        Return an immutable tuple of formatted rows: "filename | sheet_name | section_name | message".

        Args:
            self

        Returns:
            tuple[str, ...]: One formatted row per stored coercion message.

        Raises:
            None
        """
        render_list: list[str] = []
        for coercion in self.entries:
            msg_format = "{a} | {b} | {c} | {d}"
            msg = msg_format.format(a=self.file_name, b=self.sheet_name, c=self.section_name, d=coercion)
            render_list.append(msg)
        return tuple(render_list)
