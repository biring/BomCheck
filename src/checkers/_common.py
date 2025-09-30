"""
Error message utilities for checker modules.

Provides:
    - ErrorMsg: immutable record of a single validation issue with (file, sheet, section, message) context
    - ErrorLog: aggregator that maintains current context and collects ErrorMsg items for later reporting

These helpers let checkers accumulate actionable diagnostics without direct I/O.

Example Usage:
    # Preferred usage via public package interface:
    # Not exposed publicly; this is an internal module.

    # Direct internal usage (acceptable in unit tests or internal scripts only):
    from src.checkers import _common as common
    log = common.ErrorLog()
    log.set_section("Row:4")
    log.append_error("Invalid Quantity")

Notes:
    - Intended strictly for internal use by other checker modules.
    - Keep implementation minimal and generic, avoiding checker-specific logic.
    - ErrorMsg renders as "file | sheet | section | message" for stable CLI/log output.

License:
    - Internal Use Only
"""
__all__ = []  # Internal-only; not part of public API.

from dataclasses import dataclass


@dataclass(frozen=True)
class ErrorMsg:
    """
    Immutable container for a single validation error with BOM context.

    Args:
        file_name (str): Name of the BOM file being checked.
        sheet_name (str): Name of the worksheet within the file.
        section (str): Logical section of the sheet (e.g., "Header", "Row:#").
        message (str): Human-readable description of the problem.

    Returns:
        None: This dataclass stores data only and performs no validation.

    Raises:
        None
    """
    file_name: str = ""
    sheet_name: str = ""
    section: str = ""
    message: str = ""

    def __str__(self) -> str:
        """
        Render a stable, single-line representation suitable for logs and CLI.

        Args:
            self

        Returns:
            str: "file | sheet | section | message".

        Raises:
            None
        """
        return f"{self.file_name} | {self.sheet_name} | {self.section} | {self.message}"


class ErrorLog:
    """
    Aggregates errors for a current (file, sheet, section) context.

    Maintains contextual state so call sites avoid repeating file/sheet/section.
    Provides append and read helpers for simple, intention-revealing usage.

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
        self._errors: list[ErrorMsg] = []

    def __iter__(self):
        """
        Iterate over recorded errors in insertion order.

        Args:
            self

        Returns:
            Iterator[ErrorMsg]: Iterator over ErrorMsg items.

        Raises:
            None
        """
        return iter(self._errors)

    def __len__(self) -> int:
        """
        Return the number of recorded errors.

        Args:
            self

        Returns:
            int: Count of ErrorMsg items.

        Raises:
            None
        """
        return len(self._errors)

    def __str__(self) -> str:
        """
        Join all errors into a newline-separated string for CLI output.

        Args:
            self

        Returns:
            str: One line per error rendered via ErrorMsg.__str__.

        Raises:
            None
        """
        return "\n".join(str(e) for e in self._errors)

    def append_error(self, message: str) -> None:
        """
        Append a single error to the log if the message is non-empty.

        Args:
            message (str): Human-readable description of the problem.

        Returns:
            None

        Raises:
            None
        """
        if message:
            self._errors.append(ErrorMsg(self.file_name, self.sheet_name, self.section_name, message))

    def set_file_name(self, file: str) -> None:
        """
        Set the active file context for subsequent errors.

        Args:
            file (str): File name to associate with added errors.

        Returns:
            None

        Raises:
            None
        """
        self.file_name = file

    def set_sheet_name(self, sheet: str) -> None:
        """
        Set the active worksheet context for subsequent errors.

        Args:
            sheet (str): Worksheet name to associate with added errors.

        Returns:
            None

        Raises:
            None
        """
        self.sheet_name = sheet

    def set_section_name(self, section: str) -> None:
        """
        Set the active logical section context for subsequent errors.

        Args:
            section (str): Section label (e.g., "Header", "Line").

        Returns:
            None

        Raises:
            None
        """
        self.section_name = section
