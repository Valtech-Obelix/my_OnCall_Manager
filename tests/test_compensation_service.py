import pytest

from src.domain.exceptions import DomainException
from src.services.compensation_service import CompensationService


class _Analyst:
    def __init__(self, p_id: int, p_buchungsname: str, p_oncall_location_id: str):
        self.id = p_id
        self.buchungsname = p_buchungsname
        self.oncall_location_id = p_oncall_location_id


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


def test_summarize_monthly_compensation_from_bookings_groups_by_analyst() -> None:
    service = CompensationService()
    rows = service.summarize_monthly_compensation_from_bookings(
        [
            {
                "booking_date": "2026-03-03",
                "user": "Aktiv, Max",
                "slot": "F",
                "notes": "Früh",
                "source_file": "a.csv",
            },
            {
                "booking_date": "2026-03-03",
                "user": "Aktiv, Max",
                "slot": "T",
                "notes": "Tag",
                "source_file": "a.csv",
            },
            {
                "booking_date": "2026-03-07",
                "user": "West, Sue",
                "slot": "F",
                "notes": "Early",
                "source_file": "a.csv",
            },
        ],
        [
            _Analyst(1, "Aktiv, Max", "GER"),
            _Analyst(2, "West, Sue", "IND"),
        ],
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


def test_summarize_monthly_compensation_from_bookings_with_location_filter() -> None:
    service = CompensationService()
    rows = service.summarize_monthly_compensation_from_bookings(
        [
            {
                "booking_date": "2026-03-03",
                "user": "Aktiv, Max",
                "slot": "F",
                "notes": "Früh",
                "source_file": "a.csv",
            },
            {
                "booking_date": "2026-03-07",
                "user": "West, Sue",
                "slot": "F",
                "notes": "Early",
                "source_file": "a.csv",
            },
        ],
        [
            _Analyst(1, "Aktiv, Max", "GER"),
            _Analyst(2, "West, Sue", "IND"),
        ],
        p_location_filter="GER",
    )

    assert len(rows) == 1
    assert rows[0]["buchungsname"] == "Aktiv, Max"


def test_build_booking_compensation_details() -> None:
    service = CompensationService()
    details = service.build_booking_compensation_details(
        p_booking_entries=[
            {
                "booking_date": "2026-03-03",
                "user": "Aktiv, Max",
                "slot": "F",
                "notes": "[Früh]",
                "source_file": "a.csv",
            }
        ],
        p_analysts=[_Analyst(1, "Aktiv, Max", "GER")],
        p_analyst_id=1,
    )

    assert len(details) == 1
    detail = details[0]
    assert detail["slot"] == "F"
    assert detail["day_type"] == "WEEKDAY"
    assert detail["amount_eur"] == 125
    assert detail["source_file"] == "a.csv"
