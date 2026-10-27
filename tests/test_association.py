"""Tests for evidence-backed correlation between telemetry alerts and incident narratives."""

from datetime import datetime, timezone
import pytest

from aerointel.shared.models import AnomalyAlert, AnomalyType
from aerointel.shared.evidence import evaluate_incident_flight_association


@pytest.fixture
def alert():
    now = datetime(2026, 10, 26, 14, 0, 0, tzinfo=timezone.utc)
    return AnomalyAlert(
        alert_id="ALT-001",
        aircraft_id="SYN-FLT-101",
        event_type=AnomalyType.RAPID_ALTITUDE_CHANGE,
        triggered_at_utc=now,
        window_start_utc=now,
        window_end_utc=now,
        detection_method="Rule: Vertical Rate",
        threshold_value=3000.0,
        observed_value=3800.0,
        unit="fpm",
        source_name="Synthetic Demo",
        is_synthetic=True,
    )


def test_supported_association(alert):
    # Incident matching callsign, time, and altitude deviation
    incident = {
        "report_id": "INC-TEST-01",
        "event_date": "2026-10-26 14:15:00",
        "category": "Turbulence / Altitude Deviation",
        "narrative": "Aircraft SYN-FLT-101 experienced sudden altitude loss following clear air turbulence encounter.",
        "location": "BOS",
        "is_synthetic": True,
    }
    link = evaluate_incident_flight_association(alert, incident)

    assert link.is_supported is True
    assert link.confidence_level == "Medium"
    assert any("Direct identifier match" in e for e in link.supporting_evidence)
    assert any("Temporal proximity" in e for e in link.supporting_evidence)


def test_unsupported_association(alert):
    # Completely unrelated incident (runway incursion 3 days prior with different aircraft)
    incident = {
        "report_id": "INC-TEST-02",
        "event_date": "2026-10-20 09:00:00",
        "category": "Runway Incursion",
        "narrative": "Ground conflict at taxiway crossing with Boeing 777.",
        "location": "LAX",
        "is_synthetic": True,
    }
    link = evaluate_incident_flight_association(alert, incident)

    assert link.is_supported is False
    assert link.confidence_level == "Unsupported"
    assert "No supported link found" in link.link_rationale
    assert any("No direct identifier match" in lim for lim in link.limitations)
