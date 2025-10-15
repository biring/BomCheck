"""
Datatypes for coercion module.

Example Usage:
    # Preferred usage via package interface:
    # Not exposed publicly; this is an internal module.

    # Direct internal access (for tests or internal scripts only):
    from src.coerce import _types
    result = _types.Result(attr_name="manufacturer", value_in="Acme  Corporation", value_out="ACME", logs=[
        _types.Log(before="Acme  Corporation", after="Acme Corporation", description="Collapsed repeated spaces"),
        _types.Log(before="Acme Corporation", after="ACME", description="Mapped to canonical vendor code"),
    ])
    lines = result.render()

Dependencies:
 - Python >= 3.10
 - Standard Library: dataclasses, typing (Union, Callable, Match), re

Notes:
 - Rule compiles its regex at initialization and raises ValueError on invalid patterns.
 - These types are internal implementation details of the coerce package.

License:
 - Internal Use Only
"""
__all__ = []  # Internal-only; not part of public API. Star import from this module gets nothing.

import re
from dataclasses import dataclass, field
from typing import Union, Callable, Match


@dataclass(frozen=True)
class Log:
    """
    Record a single text transformation.

    Captures the before/after values and an explanation of the change for traceability.

    Args:
        before (str): Input text prior to applying a rule.
        after (str): Output text after applying the rule.
        description (str): Human-readable explanation of the change.

    Returns:
        None: Dataclass container; no return value.

    Raises:
        None
    """
    before: str
    after: str
    description: str


@dataclass
class Result:
    """
    Hold the outcome of one or more coercion rules.

    Stores the original and final values along with an ordered log of changes suitable for reporting or auditing.

    Args:
        attr_name (str): Name of the field being coerced.
        original_value (str): Original input value.
        coerced_value (str): Final coerced value.
        changes (list[Log]): Ordered list of applied transformation entries.

    Returns:
        Result: Populated outcome object including applied-change trace.

    Raises:
        None
    """
    attr_name: str = ""
    original_value: str = ""
    coerced_value: str = ""
    changes: list[Log] = field(default_factory=list)

    def render_changes(self) -> tuple[str, ...]:
        """
        Render human-readable change lines for reporting.

        Emits one formatted line per applied change, or an empty tuple when no effective change exists.

        Args:
            None

        Returns:
            tuple[str, ...]: One line per logged transformation, suitable for UI or logs.

        Raises:
            None
        """
        formatted_logs: list[str] = []
        # Optional guard; keeps log empty if no effective change
        if self.original_value != self.coerced_value:
            msg_template = "'{a}' changed from '{b}' to '{c}'. {d}"
            for entry in self.changes:
                formatted_logs.append(
                    msg_template.format(a=self.attr_name, b=entry.before, c=entry.after, d=entry.description)
                )
        # Return immutable tuple for consistency
        return tuple(formatted_logs)


@dataclass(frozen=True)
class Rule:
    """
    Represent a single regex-based coercion rule.

    Compiles the provided pattern at initialization and stores a replacement (string or callable) with a human-readable message.

    Args:
        pattern (str): Regular expression pattern to match.
        replacement (str | Callable[[Match[str]], str]): Replacement text or callable.
        description (str): Description of the transformation for logs.

    Returns:
        None: Dataclass container; no return value.

    Raises:
        ValueError: If the regex pattern fails to compile.
    """
    pattern: str
    replacement: Union[str, Callable[[Match[str]], str]]
    description: str
    _compiled_pattern: re.Pattern | None = field(init=False, repr=False, default=None)

    def __post_init__(self):
        """
        Compile the regex pattern and store it.

        Args:
            None

        Returns:
            None

        Raises:
            ValueError: If the pattern cannot be compiled by re.compile.
        """
        try:
            compiled = re.compile(self.pattern)
        except re.error as exc:
            raise ValueError(
                f"Rule pattern failed to compile: {self.pattern!r}. Reason: {exc}. "
                "Verify the regex syntax or escape special characters."
            ) from exc
        # Use object.__setattr__ because the dataclass is frozen.
        # This bypasses immutability checks, allowing assignment only during initialization.
        object.__setattr__(self, "_compiled_pattern", compiled)
