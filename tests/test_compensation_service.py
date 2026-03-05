from datetime import date
from decimal import Decimal
from pathlib import Path

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


@pytest.mark.parametrize(
    "location,day,slot,expected",
    [
        ("GER", "2026-03-03", "F", "Rufbereitschaft Werktags"),
        ("GER", "2026-03-03", "S", "Rufbereitschaft Werktags"),
        ("GER", "2026-03-03", "T", None),
        ("GER", "2026-03-07", "T", "Rufbereitschaft Samstags und Betriebsurlaub"),
        ("GER", "2026-05-01", "F", "Rufbereitschaft Sonn- und Feiertags"),
        ("IND", "2026-03-03", "F", "On Call Shift Working days"),
        ("IND", "2026-03-08", "S", "On Call Shift Weekend and Holidays"),
    ],
)
def test_determine_expected_booking_task(
    location: str,
    day: str,
    slot: str,
    expected: str | None,
) -> None:
    service = CompensationService()
    assert (
        service.determine_expected_booking_task(
            p_oncall_location_id=location,
            p_day=date.fromisoformat(day),
            p_slot=slot,
        )
        == expected
    )


def test_determine_expected_booking_task_rejects_unknown_slot() -> None:
    service = CompensationService()
    with pytest.raises(DomainException):
        service.determine_expected_booking_task(
            p_oncall_location_id="GER",
            p_day=date(2026, 3, 3),
            p_slot="X",
        )


@pytest.mark.parametrize(
    "hours,expected",
    [
        ("1,00", 1),
        ("-1,00", -1),
        ("2.00", 2),
        ("1.000,00", 1000),
        ("foo", None),
        ("0,50", None),
    ],
)
def test_parse_booking_units(hours: str, expected: int | None) -> None:
    service = CompensationService()
    assert service.parse_booking_units(hours) == expected


def test_load_monthly_booking_entries_applies_counter_bookings(monkeypatch, tmp_path: Path) -> None:
    csv_path = tmp_path / "bookings.csv"
    csv_path.write_text(
        (
            "\"report\"\n"
            "\"Internal id\";\"Date\";\"User\";\"Client\";\"Project\";\"Task - Task type\";\"Task\";\"Time (Hours)\";\"Notes\"\n"
            "\"1\";\"03-02-26\";\"Aysel, Mecnur\";\"c\";\"p\";\"On Call\";\"Rufbereitschaft Werktags\";\"1,00\";\"[Früh]\"\n"
            "\"2\";\"03-02-26\";\"Aysel, Mecnur\";\"c\";\"p\";\"On Call\";\"Rufbereitschaft Werktags\";\"1,00\";\"[Früh]\"\n"
            "\"3\";\"03-02-26\";\"Aysel, Mecnur\";\"c\";\"p\";\"On Call\";\"Rufbereitschaft Werktags\";\"-1,00\";\"[Früh]\"\n"
            "\"4\";\"03-02-26\";\"Aysel, Mecnur\";\"c\";\"p\";\"Client Utilized\";\"RB-Abstimmung\";\"1,00\";\"Weekly\"\n"
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr(
        "src.services.compensation_service.booking_csv_files",
        lambda: [csv_path],
    )

    service = CompensationService()
    entries = service.load_monthly_booking_entries(2026, 2)

    assert len(entries) == 1
    assert entries[0]["booking_date"] == "2026-02-03"
    assert entries[0]["user"] == "Aysel, Mecnur"
    assert entries[0]["slot"] == "F"


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
        p_overtime_entries=[],
        p_analysts=[
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
    assert max_row["overtime_ger_25_hours"] == "0"
    assert max_row["overtime_ger_50_hours"] == "0"

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
        p_overtime_entries=[],
        p_analysts=[
            _Analyst(1, "Aktiv, Max", "GER"),
            _Analyst(2, "West, Sue", "IND"),
        ],
        p_location_filter="GER",
    )

    assert len(rows) == 1
    assert rows[0]["buchungsname"] == "Aktiv, Max"


def test_summarize_monthly_compensation_includes_overtime_hours() -> None:
    service = CompensationService()
    rows = service.summarize_monthly_compensation_from_bookings(
        p_booking_entries=[],
        p_overtime_entries=[
            {
                "booking_date": "2026-02-03",
                "user": "Aysel, Mecnur",
                "task_name": "Arbeit (25%) WT (6-9, 17-20) Sa (6-20)",
                "hours": Decimal("1.5"),
                "notes": "",
                "source_file": "a.csv",
            }
        ],
        p_analysts=[_Analyst(1, "Aysel, Mecnur", "GER")],
    )

    assert len(rows) == 1
    assert rows[0]["overtime_ger_25_hours"] == "1.5"
    assert rows[0]["overtime_ger_50_hours"] == "0"
    assert rows[0]["overtime_ind_mo_sa_hours"] == "0"
    assert rows[0]["overtime_ind_so_hours"] == "0"


def test_summarize_monthly_compensation_includes_india_overtime_buckets() -> None:
    service = CompensationService()
    rows = service.summarize_monthly_compensation_from_bookings(
        p_booking_entries=[],
        p_overtime_entries=[
            {
                "booking_date": "2026-02-08",
                "user": "West, Sue",
                "task_name": "Work On Call Shift (Mo-Sat)",
                "hours": Decimal("2"),
                "notes": "",
                "source_file": "a.csv",
            },
            {
                "booking_date": "2026-02-09",
                "user": "West, Sue",
                "task_name": "Work On Call Shift (Sunday)",
                "hours": Decimal("1.5"),
                "notes": "",
                "source_file": "a.csv",
            },
        ],
        p_analysts=[_Analyst(2, "West, Sue", "IND")],
        p_location_filter="IND",
    )

    assert len(rows) == 1
    assert rows[0]["overtime_ind_mo_sa_hours"] == "2"
    assert rows[0]["overtime_ind_so_hours"] == "1.5"


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
        p_overtime_entries=[],
        p_analysts=[_Analyst(1, "Aktiv, Max", "GER")],
        p_analyst_id=1,
    )

    assert len(details) == 1
    detail = details[0]
    assert detail["entry_type"] == "On Call"
    assert detail["task_or_slot"] == "F"
    assert detail["hours"] == "1"
    assert detail["day_type"] == "WEEKDAY"
    assert detail["amount_eur"] == 125
    assert detail["source_file"] == "a.csv"


def test_load_monthly_overtime_entries_applies_counter_bookings(monkeypatch, tmp_path: Path) -> None:
    csv_path = tmp_path / "bookings.csv"
    csv_path.write_text(
        (
            "\"report\"\n"
            "\"Internal id\";\"Date\";\"User\";\"Client\";\"Project\";\"Task - Task type\";\"Task\";\"Time (Hours)\";\"Notes\"\n"
            "\"1\";\"03-02-26\";\"Aysel, Mecnur\";\"c\";\"p\";\"Overtime\";\"Arbeit (25%) WT (6-9, 17-20) Sa (6-20)\";\"1,50\";\"n\"\n"
            "\"2\";\"03-02-26\";\"Aysel, Mecnur\";\"c\";\"p\";\"Overtime\";\"Arbeit (25%) WT (6-9, 17-20) Sa (6-20)\";\"-0,50\";\"n\"\n"
            "\"3\";\"03-02-26\";\"Aysel, Mecnur\";\"c\";\"p\";\"On Call\";\"Rufbereitschaft Werktags\";\"1,00\";\"[Früh]\"\n"
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr(
        "src.services.compensation_service.booking_csv_files",
        lambda: [csv_path],
    )

    service = CompensationService()
    entries = service.load_monthly_overtime_entries(2026, 2)

    assert len(entries) == 1
    assert entries[0]["booking_date"] == "2026-02-03"
    assert entries[0]["user"] == "Aysel, Mecnur"
    assert entries[0]["task_name"] == "Arbeit (25%) WT (6-9, 17-20) Sa (6-20)"
    assert entries[0]["hours"] == Decimal("1.00")
