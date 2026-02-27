from datetime import datetime
from zoneinfo import ZoneInfo


UTC = ZoneInfo("UTC")
BERLIN = ZoneInfo("Europe/Berlin")


def parse_utc_timestamp(p_timestamp: str) -> datetime:
    """
    Parses OpsGenie/DB UTC timestamps like:
    - 2026-01-01T00:00:00Z
    - 2026-02-27T20:29:09.21Z
    """
    return datetime.fromisoformat(p_timestamp.replace("Z", "+00:00"))


def format_utc_as_berlin(p_timestamp: str) -> str:
    utc_dt = parse_utc_timestamp(p_timestamp).astimezone(UTC)
    local_dt = utc_dt.astimezone(BERLIN)
    return local_dt.strftime("%d.%m.%Y %H:%M:%S (%Z)")
