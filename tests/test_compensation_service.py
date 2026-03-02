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


def test_summarize_monthly_compensation_groups_by_analyst() -> None:
    service = CompensationService()
    rows = service.summarize_monthly_compensation(
        [
            {
                "analyst_id": 1,
                "buchungsname": "Aktiv, Max",
                "oncall_location_id": "GER",
                "start_time": "2026-03-03T01:00:00Z",
            },
            {
                "analyst_id": 1,
                "buchungsname": "Aktiv, Max",
                "oncall_location_id": "GER",
                "start_time": "2026-03-03T09:00:00Z",
            },
            {
                "analyst_id": 2,
                "buchungsname": "West, Sue",
                "oncall_location_id": "IND",
                "start_time": "2026-03-07T01:00:00Z",
            },
        ]
    )

    assert len(rows) == 2
    max_row = rows[0]
    sue_row = rows[1]

    assert max_row["buchungsname"] == "Aktiv, Max"
    assert max_row["shift_count_f"] == 1
    assert max_row["shift_count_t"] == 1
    assert max_row["shift_count_s"] == 0
    assert max_row["total_amount_eur"] == 125

    assert sue_row["buchungsname"] == "West, Sue"
    assert sue_row["total_amount_eur"] == 10
