"""ISO-8601 timestamps in the owner's timezone for server-written text."""

import os
import sys
from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import patch

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.utils.dates import format_local_iso


def test_uses_owner_zone_and_offset():
    owner = SimpleNamespace(timezone="America/New_York")

    assert format_local_iso(datetime(2026, 1, 15, 17, 0), owner) == "2026-01-15T12:00:00-05:00"
    assert format_local_iso(datetime(2026, 7, 15, 17, 0), owner) == "2026-07-15T13:00:00-04:00"


def test_aware_datetimes_and_none():
    owner = SimpleNamespace(timezone="Asia/Tokyo")
    aware = datetime(2026, 3, 4, 23, 30, tzinfo=timezone.utc)

    assert format_local_iso(aware, owner) == "2026-03-05T08:30:00+09:00"
    assert format_local_iso(None, owner) == ""


def test_falls_back_to_deployment_zone():
    owner = SimpleNamespace(timezone=None)

    with patch("src.utils.timezones.deployment_timezone", return_value="Europe/Berlin"):
        assert format_local_iso(datetime(2026, 1, 15, 17, 0), owner) == "2026-01-15T18:00:00+01:00"
