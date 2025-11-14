"""
ChangeLog component for recording human-readable change events across (module, file, sheet, section) contexts.

This module provides a lightweight stateful object used across parsing, cleaning, fixing, and reporting stages to accumulate text entries and render them as flat, context-rich report rows.

Example Usage:
    # Preferred usage via package interface:
    from src.common import ChangeLog
    log = ChangeLog()
    log.set_section_name("Row:4")
    log.add_entry("Invalid Quantity")

    # Direct internal usage (acceptable for tests or internal scripts only):
    from src.common._change_log import ChangeLog
    log = ChangeLog()
    log.set_section_name("Items")
    log.add_entry("Collapsed whitespace")

Dependencies:
    - Python >= 3.10
    - Standard Library: typing

Notes:
    - Context values apply at render time; entries do not store their own context.
    - Empty or whitespace-only messages are ignored.
    - Internal-only module; ChangeLog is publicly exposed via the package __init__.

License:
    - Internal Use Only
"""

__all__ = []  # Internal-only; not part of public API.


class ChangeLog:
    """
    Accumulate change messages under a shared (module, file, sheet, section) context.

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
        self._module_name = ""
        self._file_name = ""
        self._sheet_name = ""
        self._section_name = ""
        self._entries: list[str] = []

    def set_module_name(self, file: str) -> None:
        """
        Set the active module context.

        Args:
            file (str): Module name to associate with subsequent entries.

        Returns:
            None
        """
        self._module_name = file

    def set_file_name(self, file: str) -> None:
        """
        Set the active file context.

        Args:
            file (str): File name to associate with subsequent entries.

        Returns:
            None
        """
        self._file_name = file

    def set_sheet_name(self, sheet: str) -> None:
        """
        Set the active sheet context.

        Args:
            sheet (str): Worksheet name to associate with subsequent entries.

        Returns:
            None
        """
        self._sheet_name = sheet

    def set_section_name(self, section: str) -> None:
        """
        Set the active section context.

        Args:
            section (str): Section or block name to associate with subsequent entries.

        Returns:
            None
        """
        self._section_name = section

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
            self._entries.append(entry)

    def render(self) -> tuple[str, ...]:
        """
        Render all entries as flat rows: "module | file | sheet | section | message".

        Args:
            self

        Returns:
            tuple[str, ...]: One formatted row per entry, in insertion order.
        """
        render_list: list[str] = []
        for entry in self._entries:
            # Flatten messages to "module | file | sheet | section | message"
            msg_format = "{a} | {b} | {c} | {d} | {e}"
            msg = msg_format.format(
                a=self._module_name, b=self._file_name, c=self._sheet_name, d=self._section_name, e=entry
            )
            render_list.append(msg)

        return tuple(render_list)
