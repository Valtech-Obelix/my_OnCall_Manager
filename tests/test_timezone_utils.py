from src.infrastructure.timezone_utils import format_utc_as_berlin


def test_winter_time_conversion_uses_cet() -> None:
    # 23:00 UTC am 31.12 entspricht 00:00 CET am 01.01
    value = format_utc_as_berlin("2025-12-31T23:00:00Z")
    assert value == "01.01.2026 00:00:00 (CET)"


def test_summer_time_conversion_uses_cest() -> None:
    # 00:00 UTC im Sommer entspricht 02:00 CEST
    value = format_utc_as_berlin("2026-06-01T00:00:00Z")
    assert value == "01.06.2026 02:00:00 (CEST)"
