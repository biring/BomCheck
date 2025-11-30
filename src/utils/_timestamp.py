"""
Utility functions for working with date and time.

Example Usage:
    # Preferred usage through the utils interface:
    from src.utils import timestamp
    ts = timestamp.now_utc_iso()

    # Direct import for internal scripts or tests:
    import src.utils._timestamp as timestamp
    ts = timestamp.now_utc_iso()

Dependencies:
    - Python >= 3.9
    - Standard Library: datetime

License:
    - Internal Use Only
"""
__all__ = ["now_utc_iso"]

from datetime import datetime, timezone


def now_utc_iso() -> str:
    """
    Get the current UTC time in ISO 8601 format with a 'Z' suffix.

    The output is accurate to the second (microseconds are removed) and uses the 'Z' suffix to indicate UTC, instead of an explicit offset.

    Returns:
        str: Current UTC timestamp in the form 'YYYY-MM-DDTHH:MM:SSZ'.
    """
    return (
        datetime.now(timezone.utc)  # Get current time in UTC
        .replace(microsecond=0)  # Remove microseconds for second precision
        .isoformat()  # Convert to ISO 8601
        .replace("+00:00", "Z")  # Replace '+00:00' with 'Z' for UTC
    )
