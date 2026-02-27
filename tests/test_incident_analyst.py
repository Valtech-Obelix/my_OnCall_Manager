from datetime import date

import pytest

from src.domain.exceptions import DomainException
from src.domain.incident_analyst import IncidentAnalyst


def test_generates_buchungsname_when_missing() -> None:
    analyst = IncidentAnalyst(
        p_id=None,
        p_vornamen="Max",
        p_nachname="Mustermann",
        p_email="max.mustermann@example.com",
        p_start_datum=date(2026, 1, 1),
    )

    assert analyst.buchungsname == "Max Mustermann"


def test_rejects_invalid_email() -> None:
    with pytest.raises(DomainException, match="Ungültiges Email-Format"):
        IncidentAnalyst(
            p_id=None,
            p_vornamen="Max",
            p_nachname="Mustermann",
            p_email="ungueltig",
            p_start_datum=date(2026, 1, 1),
        )
