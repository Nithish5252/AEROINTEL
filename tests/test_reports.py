"""Tests for report lifecycle transitions, evidence validation, and audit tracking."""

from datetime import datetime, timezone
import pytest

from aerointel.shared.models import PreliminaryReport, LifecycleStatus, RevisionEntry
from aerointel.shared.lifecycle import transition_report_status, add_report_revision


@pytest.fixture
def sample_report():
    now = datetime.now(timezone.utc)
    return PreliminaryReport(
        report_id="REP-TEST-001",
        alert_id="ALT-001",
        created_at_utc=now,
        event_start_utc=now,
        event_end_utc=now,
        aircraft_id="SYN-FLT-101",
        event_type="Rapid Altitude Change",
        detection_method="Rule: Vertical Rate",
        thresholds_or_model_version="Threshold: 3000 fpm",
        initial_assessment="Demonstration preliminary assessment.",
        lifecycle_status=LifecycleStatus.DETECTED,
        evidence_references=[],
        revision_history=[],
    )


def test_valid_lifecycle_transitions(sample_report):
    # Detected -> Preliminary
    ok, msg = transition_report_status(sample_report, LifecycleStatus.PRELIMINARY, "Analyst", "Initial review")
    assert ok is True
    assert sample_report.lifecycle_status == LifecycleStatus.PRELIMINARY
    assert len(sample_report.revision_history) == 1

    # Preliminary -> Under Review
    ok, msg = transition_report_status(sample_report, LifecycleStatus.UNDER_REVIEW, "Analyst", "Deep dive")
    assert ok is True
    assert sample_report.lifecycle_status == LifecycleStatus.UNDER_REVIEW
    assert len(sample_report.revision_history) == 2


def test_invalid_lifecycle_transition(sample_report):
    # Cannot jump directly from Detected to Confirmed by Source
    ok, msg = transition_report_status(sample_report, LifecycleStatus.CONFIRMED_BY_SOURCE, "Analyst", "Premature jump")
    assert ok is False
    assert "Invalid transition" in msg
    assert sample_report.lifecycle_status == LifecycleStatus.DETECTED


def test_confirmed_by_source_requires_evidence_reference(sample_report):
    # Fast forward to Under Review
    sample_report.lifecycle_status = LifecycleStatus.UNDER_REVIEW
    sample_report.evidence_references = []  # No citations

    # Attempt to confirm without evidence
    ok, msg = transition_report_status(sample_report, LifecycleStatus.CONFIRMED_BY_SOURCE, "Analyst", "Confirming")
    assert ok is False
    assert "Cannot transition to 'Confirmed by Source' without explicit cited evidence" in msg

    # Add evidence reference and re-attempt
    sample_report.evidence_references.append("ASRS Report #1849204 citation")
    ok, msg = transition_report_status(sample_report, LifecycleStatus.CONFIRMED_BY_SOURCE, "Analyst", "Now cited")
    assert ok is True
    assert sample_report.lifecycle_status == LifecycleStatus.CONFIRMED_BY_SOURCE
