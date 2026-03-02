import pytest

from src.domain.exceptions import DomainException
from src.services.compensation_service import CompensationService


def test_shift_slot_mapping() -> None:
    service = CompensationService()
    assert service.determine_shift_slot("2026-03-02T00:30:00Z") in ("F", "T", "S")


@pytest.mark.parametrize(
    "location,start_time,expected",
    [
        ("GER", "2026-03-03T01:00:00Z", 125),  # Dienstag, Frueh/Spät vergütet
        ("GER", "2026-03-03T09:00:00Z", 0),    # Dienstag, Tag
        ("GER", "2026-03-07T01:00:00Z", 150),  # Samstag
        ("GER", "2026-03-08T01:00:00Z", 180),  # Sonntag
        ("GER", "2026-05-01T01:00:00Z", 180),  # Feiertag (Tag der Arbeit)
        ("IND", "2026-03-03T01:00:00Z", 6),    # Werktag
        ("IND", "2026-03-07T01:00:00Z", 10),   # Samstag
        ("IND", "2026-03-08T01:00:00Z", 10),   # Sonntag
        ("IND", "2026-05-01T01:00:00Z", 10),   # Feiertag
    ],
)
def test_calculate_shift_compensation(location: str, start_time: str, expected: int) -> None:
    service = CompensationService()
    assert service.calculate_shift_compensation(location, start_time) == expected


def test_unknown_location_raises_domain_exception() -> None:
    service = CompensationService()
    with pytest.raises(DomainException):
        service.calculate_shift_compensation("USA", "2026-03-03T01:00:00Z")
