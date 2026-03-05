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

    assert analyst.buchungsname == "Mustermann, Max"


def test_rejects_invalid_email() -> None:
    with pytest.raises(DomainException, match="Ungültiges Email-Format"):
        IncidentAnalyst(
            p_id=None,
            p_vornamen="Max",
            p_nachname="Mustermann",
            p_email="ungueltig",
            p_start_datum=date(2026, 1, 1),
        )


def test_defaults_oncall_location_to_ger() -> None:
    analyst = IncidentAnalyst(
        p_id=None,
        p_vornamen="Erika",
        p_nachname="Muster",
        p_email="erika@example.com",
        p_start_datum=date(2026, 1, 1),
    )

    assert analyst.oncall_location_id == "GER"


def test_defaults_mitarbeitertyp_to_incident_analyst() -> None:
    analyst = IncidentAnalyst(
        p_id=None,
        p_vornamen="Erika",
        p_nachname="Muster",
        p_email="erika@example.com",
        p_start_datum=date(2026, 1, 1),
    )

    assert analyst.mitarbeitertyp == "INCIDENT_ANALYST"
