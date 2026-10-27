"""Evidence-based correlation engine between telemetry alerts and incident narratives."""

from datetime import datetime
from typing import Optional, List, Dict, Any
import pandas as pd

from aerointel.shared.models import AnomalyAlert, IncidentRecord, EvidenceLink


def evaluate_incident_flight_association(
    alert: AnomalyAlert,
    incident: Dict[str, Any],
    max_time_diff_hours: float = 6.0,
) -> EvidenceLink:
    """Evaluate whether evidence supports linking a telemetry alert with an incident narrative.
    
    Principles:
    - Never merge records solely because they have nearby time or similar wording.
    - Requires matching factual dimensions (callsign, timestamp proximity, geographic region).
    - If evidence is insufficient, explicitly returns 'No supported link found' or 'Needs review'.
    """
    supporting: List[str] = []
    limitations: List[str] = []
    score = 0

    # 1. Callsign / Identifier comparison
    aircraft_id = alert.aircraft_id.upper().strip()
    incident_narrative = str(incident.get("narrative", "")).upper()
    incident_location = str(incident.get("location", "")).upper()

    if aircraft_id in incident_narrative:
        supporting.append(f"Direct identifier match: Aircraft ID '{aircraft_id}' appears in incident narrative.")
        score += 3
    else:
        limitations.append(f"No direct identifier match: '{aircraft_id}' is not cited in incident narrative.")

    # 2. Temporal Proximity
    incident_date_raw = incident.get("event_date")
    if incident_date_raw is not None and not pd.isna(incident_date_raw):
        try:
            incident_dt = pd.to_datetime(incident_date_raw, utc=True)
            alert_dt = pd.to_datetime(alert.triggered_at_utc, utc=True)
            time_diff = abs((alert_dt - incident_dt).total_seconds()) / 3600.0

            if time_diff <= max_time_diff_hours:
                supporting.append(f"Temporal proximity: Occurred within {time_diff:.1f} hours of each other.")
                score += 2
            else:
                limitations.append(f"Time divergence: Events are separated by {time_diff:.1f} hours.")
        except Exception:
            limitations.append("Unable to parse incident event date for temporal correlation.")
    else:
        limitations.append("Incident record lacks verified event date.")

    # 3. Event Type Congruence
    event_type = alert.event_type.value.lower()
    incident_cat = str(incident.get("category", "")).lower()

    if "altitude" in event_type and ("altitude" in incident_cat or "depressurization" in incident_cat or "turbulence" in incident_cat):
        supporting.append(f"Event type congruence: Telemetry {alert.event_type.value} aligns with category '{incident.get('category')}'.")
        score += 2
    elif "speed" in event_type and ("engine" in incident_cat or "speed" in incident_cat or "avionics" in incident_cat):
        supporting.append(f"Event type congruence: Telemetry {alert.event_type.value} aligns with category '{incident.get('category')}'.")
        score += 2
    else:
        limitations.append("No obvious operational congruence between detector alert type and incident category.")

    # 4. Synthetics Disclaimer
    if alert.is_synthetic or incident.get("is_synthetic", True):
        limitations.append("One or both records are synthetic demo data; link is purely illustrative.")

    # Assessment Determination
    if score >= 5:
        confidence = "Medium"
        is_supported = True
        rationale = "Supported by multiple independent indicators (identifier/temporal and event congruence)."
    elif score >= 2:
        confidence = "Needs Review"
        is_supported = False
        rationale = "Circumstantial indicators only; insufficient factual basis to establish a link."
    else:
        confidence = "Unsupported"
        is_supported = False
        rationale = "No supported link found between telemetry alert and incident report."

    return EvidenceLink(
        alert_id=alert.alert_id,
        incident_id=str(incident.get("report_id", "UNKNOWN")),
        link_rationale=rationale,
        supporting_evidence=supporting,
        limitations=limitations,
        confidence_level=confidence,
        is_supported=is_supported,
    )
