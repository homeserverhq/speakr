"""
Datetime normalization helpers.

Backend timestamps — including meeting_date — are stored as naive UTC and
converted to the viewer's timezone client-side (parseServerInstant). These
helpers normalize incoming values to that convention.
"""

from datetime import datetime, timezone
from typing import Optional
from zoneinfo import ZoneInfo

from src.utils.timezones import user_timezone


def to_utc_naive(dt: Optional[datetime]) -> Optional[datetime]:
    """Normalize a datetime to naive UTC.

    Aware datetimes are converted to UTC before the tzinfo is stripped.
    Naive datetimes are returned unchanged (assumed to be UTC already).
    """
    if dt is None:
        return None
    if dt.tzinfo is not None:
        return dt.astimezone(timezone.utc).replace(tzinfo=None)
    return dt


def format_local_iso(dt: Optional[datetime], user) -> str:
    """Format a naive-UTC datetime as ISO 8601 in the owner's timezone.

    Example: ``2026-06-22T15:00:00-04:00`` (offset reflects DST automatically).
    Naive datetimes are treated as UTC. Users without a timezone fall back to
    the deployment default, then UTC. Returns an empty string for None.
    """
    if dt is None:
        return ""
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(ZoneInfo(user_timezone(user))).isoformat(timespec="seconds")
