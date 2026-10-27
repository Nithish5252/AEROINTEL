"""Report lifecycle management and audit revision tracking."""

from datetime import datetime, timezone
from typing import Tuple, List
from aerointel.shared.models import PreliminaryReport, LifecycleStatus, RevisionEntry


VALID_TRANSITIONS = {
    LifecycleStatus.DETECTED: [LifecycleStatus.PRELIMINARY, LifecycleStatus.CLOSED],
    LifecycleStatus.PRELIMINARY: [LifecycleStatus.UNDER_REVIEW, LifecycleStatus.CLOSED],
    LifecycleStatus.UNDER_REVIEW: [LifecycleStatus.ENRICHED, LifecycleStatus.CONFIRMED_BY_SOURCE, LifecycleStatus.CLOSED],
    LifecycleStatus.ENRICHED: [LifecycleStatus.CONFIRMED_BY_SOURCE, LifecycleStatus.CLOSED],
    LifecycleStatus.CONFIRMED_BY_SOURCE: [LifecycleStatus.CLOSED],
    LifecycleStatus.CLOSED: [LifecycleStatus.UNDER_REVIEW],  # Allow reopening if new evidence emerges
}


def transition_report_status(
    report: PreliminaryReport,
    new_status: LifecycleStatus,
    author: str,
    notes: str,
) -> Tuple[bool, str]:
    """Transition a report's lifecycle status with audit logging.
    
    Rules:
    - Verifies valid lifecycle transition
    - "Confirmed by Source" requires cited evidence references
    - Automatically appends a timestamped RevisionEntry
    """
    current_status = report.lifecycle_status

    if current_status == new_status:
        return False, f"Report is already in status '{current_status.value}'."

    allowed = VALID_TRANSITIONS.get(current_status, [])
    if new_status not in allowed:
        allowed_str = ", ".join([s.value for s in allowed])
        return False, f"Invalid transition from '{current_status.value}' to '{new_status.value}'. Allowed: [{allowed_str}]."

    # Special check: "Confirmed by Source" must have evidence references
    if new_status == LifecycleStatus.CONFIRMED_BY_SOURCE and not report.evidence_references:
        return False, "Cannot transition to 'Confirmed by Source' without explicit cited evidence references."

    # Perform transition
    now_utc = datetime.now(timezone.utc)
    report.lifecycle_status = new_status
    report.revision_history.append(
        RevisionEntry(
            timestamp_utc=now_utc,
            author_or_system=author,
            action=f"Status changed from {current_status.value} to {new_status.value}",
            notes=notes,
        )
    )
    return True, f"Successfully updated report status to '{new_status.value}'."


def add_report_revision(
    report: PreliminaryReport,
    author: str,
    action: str,
    notes: str,
) -> None:
    """Add an audit trail revision entry without changing status."""
    report.revision_history.append(
        RevisionEntry(
            timestamp_utc=datetime.now(timezone.utc),
            author_or_system=author,
            action=action,
            notes=notes,
        )
    )
