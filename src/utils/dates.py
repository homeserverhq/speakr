"""
Datetime normalization helpers.

Backend timestamps — including meeting_date — are stored as naive UTC and
converted to the viewer's timezone client-side (parseServerInstant). These
helpers normalize incoming values to that convention.
"""

import os
from datetime import datetime, timezone
from typing import Optional

import pytz

# Server's local timezone, from the TZ env var (defaults to UTC). Used when
# rendering backend timestamps (stored as naive UTC) into user-facing output.
_local_tz_name = os.environ.get("TZ") or "UTC"
_local_tz = pytz.timezone(_local_tz_name)


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


def to_local(dt: Optional[datetime]) -> Optional[datetime]:
    """Convert a naive-UTC (or aware) datetime to the server's local timezone.

    Naive datetimes are treated as UTC per the codebase convention. Aware
    datetimes are converted in place.
    """
    if dt is None:
        return None
    if dt.tzinfo is None:
        dt = pytz.utc.localize(dt)
    return dt.astimezone(_local_tz)


def format_local_iso(dt: Optional[datetime]) -> str:
    """Format a datetime as local ISO 8601 with UTC offset.

    Example: ``2026-06-22T15:00:00-04:00`` (offset reflects DST automatically).
    Naive datetimes are treated as UTC and converted to the server's local
    timezone. Returns an empty string for None.
    """
    local = to_local(dt)
    if local is None:
        return ""
    return local.isoformat(timespec="seconds")
