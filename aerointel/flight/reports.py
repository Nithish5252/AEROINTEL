"""Preliminary report generation from telemetry anomaly alerts."""

import uuid
from datetime import datetime, timezone
from typing import Dict, Any, Optional

from aerointel.shared.models import (
    AnomalyAlert,
    PreliminaryReport,
    LifecycleStatus,
    RevisionEntry,
)


def generate_preliminary_report(
    alert: AnomalyAlert,
    additional_context: Optional[Dict[str, Any]] = None,
) -> PreliminaryReport:
    """Generate a structured Preliminary Report from an Anomaly Alert adhering to Section 7 schema.
    
    Ensures that factual telemetry observations, statistical indicators,
    and unknowns are strictly separated.
    """
    now_utc = datetime.now(timezone.utc)
    report_id = f"REP-{alert.aircraft_id}-{now_utc.strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"

    initial_assessment = (
        f"AeroIntel detected a {alert.event_type.value.lower()} that exceeded configured demonstration threshold "
        f"({alert.threshold_value} {alert.unit}) during the observed interval [{alert.window_start_utc.strftime('%H:%M:%S UTC')} - "
        f"{alert.window_end_utc.strftime('%H:%M:%S UTC')}]. Observed measurement: {alert.observed_value} {alert.unit}. "
        f"The cause and operational significance are unknown. This alert is not, by itself, evidence of an emergency, "
        f"mechanical fault, or accident."
    )

    unknowns = [
        "Pilot control inputs and flight crew intent are unknown.",
        "Air Traffic Control (ATC) clearances, altitude assignments, and vectoring instructions are not recorded in this telemetry.",
        "Micro-scale atmospheric conditions (convective activity, clear-air turbulence, mountain wave activity) are unknown.",
        "Aircraft maintenance status and onboard avionics health cannot be determined from external ADS-B state vectors.",
        "Whether this telemetry behavior was an intentional procedural maneuver or an uncommanded excursion remains unverified.",
    ]

    calculated_changes = {}
    if alert.supporting_measurements:
        calculated_changes = {
            k: v for k, v in alert.supporting_measurements.items()
            if "delta" in k or "calculated" in k or "rate" in k or "acceleration" in k
        }

    initial_revision = RevisionEntry(
        timestamp_utc=now_utc,
        author_or_system="AeroIntel Automated Detector",
        action="Report Creation",
        notes=f"Initial preliminary report generated automatically for alert {alert.alert_id}.",
    )

    return PreliminaryReport(
        report_id=report_id,
        alert_id=alert.alert_id,
        created_at_utc=now_utc,
        event_start_utc=alert.window_start_utc,
        event_end_utc=alert.window_end_utc,
        aircraft_id=alert.aircraft_id,
        event_type=alert.event_type.value,
        observed_measurements=alert.supporting_measurements,
        calculated_changes=calculated_changes,
        detection_method=alert.detection_method,
        thresholds_or_model_version=f"Threshold: {alert.threshold_value} {alert.unit}",
        anomaly_score=alert.anomaly_score,
        score_interpretation="Demonstration score indicating relative deviation magnitude; uncalibrated risk.",
        source_name=alert.source_name,
        source_retrieved_at_utc=alert.triggered_at_utc,
        data_quality_warnings=alert.quality_warnings or ["Demonstration synthetic telemetry."],
        evidence_references=[
            f"Telemetry record: Aircraft {alert.aircraft_id} at {alert.window_end_utc.isoformat()}"
        ],
        initial_assessment=initial_assessment,
        unknowns=unknowns,
        lifecycle_status=LifecycleStatus.DETECTED,
        revision_history=[initial_revision],
    )
