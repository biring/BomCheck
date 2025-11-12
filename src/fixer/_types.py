"""
Change-log datatypes for the fixer package.

This module provides a lightweight ChangeLog to accumulate human-readable change messages under a (file, sheet, section) context and render them as flat report rows.

Example Usage:
    # Preferred usage via package interface:
    # Not exposed publicly; this is an internal module.

    # Direct internal access (for tests or internal scripts only):
    from src.fixer import _types as types
    log = types.ChangeLog()

Dependencies:
    - Python >= 3.10
    - Standard Library: typing (for type annotations), builtins

Notes:
    - Internal-only helper used by fixer flows to collect and emit audit-friendly messages.
    - Keep this module private to preserve API boundaries and allow future refactors.

License:
    - Internal Use Only
"""

__all__ = []  # Internal-only; not part of public API.


class ChangeLog:
    """
    Accumulate change messages under a shared (file, sheet, section) context.

    Stores lightweight text events and can render them as flat rows for reporting.

    Args:
        self

    Returns:
        None

    Raises:
        None
    """

    def __init__(self) -> None:
        """
        Initialize an empty log with no active context.

        Args:
            self

        Returns:
            None

        Raises:
            None
        """
        self.file_name = ""
        self.sheet_name = ""
        self.section_name = ""
        self.entries: list[str] = []

    def set_file_name(self, file: str) -> None:
        """
        Set the active file context.

        Args:
            file (str): File name to associate with subsequent entries.

        Returns:
            None
        """
        self.file_name = file

    def set_sheet_name(self, sheet: str) -> None:
        """
        Set the active sheet context.

        Args:
            sheet (str): Worksheet name to associate with subsequent entries.

        Returns:
            None
        """
        self.sheet_name = sheet

    def set_section_name(self, section: str) -> None:
        """
        Set the active section context.

        Args:
            section (str): Section or block name to associate with subsequent entries.

        Returns:
            None
        """
        self.section_name = section

    def add_entry(self, message: str) -> None:
        """
        Append a single message under the current context.

        Skips empty or whitespace-only messages.

        Args:
            message (str): Human-readable description of the change.

        Returns:
            None
        """
        entry = message.strip()
        if entry:
            self.entries.append(entry)

    def to_tuple(self) -> tuple[str, ...]:
        """
        Render all entries as flat rows: "file | sheet | section | message".

        Args:
            self

        Returns:
            tuple[str, ...]: One formatted row per entry, in insertion order.
        """
        render_list: list[str] = []
        for entry in self.entries:
            # Flatten messages to "file | sheet | section | message"
            msg_format = "{a} | {b} | {c} | {d}"
            msg = msg_format.format(a=self.file_name, b=self.sheet_name, c=self.section_name, d=entry)
            render_list.append(msg)
        return tuple(render_list)
