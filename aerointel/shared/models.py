"""Data models and schemas for AeroIntel."""

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class LifecycleStatus(str, Enum):
    """Lifecycle statuses for preliminary incident & anomaly reports."""
    DETECTED = "Detected"
    PRELIMINARY = "Preliminary"
    UNDER_REVIEW = "Under Review"
    ENRICHED = "Enriched"
    CONFIRMED_BY_SOURCE = "Confirmed by Source"
    CLOSED = "Closed"


class AnomalyType(str, Enum):
    """Types of detected telemetry anomalies."""
    RAPID_ALTITUDE_CHANGE = "Rapid Altitude Change"
    ABRUPT_SPEED_DROP = "Abrupt Speed Drop"
    STALE_TELEMETRY = "Stale / Missing Telemetry"
    ISOLATION_FOREST_OUTLIER = "Statistical Outlier (Isolation Forest)"
    HEADING_INVERSION = "Unusual Heading Shift"
    LOW_ALTITUDE_SPEED_EXCEEDANCE = "Low Altitude High-Speed Exceedance"


class FlightObservation(BaseModel):
    """Schema for a single aircraft telemetry observation."""
    aircraft_id: str
    timestamp: datetime
    latitude: float
    longitude: float
    altitude_ft: Optional[float] = None
    ground_speed_kt: Optional[float] = None
    heading_deg: Optional[float] = None
    vertical_rate_fpm: Optional[float] = None
    source: str = "Synthetic Demo Dataset"
    is_synthetic: bool = True


class AnomalyAlert(BaseModel):
    """Schema for a detected telemetry anomaly alert."""
    alert_id: str
    aircraft_id: str
    event_type: AnomalyType
    triggered_at_utc: datetime
    window_start_utc: datetime
    window_end_utc: datetime
    detection_method: str  # e.g., "Rule: Vertical Rate Threshold"
    threshold_value: Optional[float] = None
    observed_value: Optional[float] = None
    unit: str = ""
    anomaly_score: Optional[float] = None  # -1.0 to 1.0 or confidence
    quality_warnings: List[str] = Field(default_factory=list)
    source_name: str = "Synthetic Demo Dataset"
    is_synthetic: bool = True
    supporting_measurements: Dict[str, Any] = Field(default_factory=dict)


class RevisionEntry(BaseModel):
    """Audit trail revision entry for reports."""
    timestamp_utc: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    author_or_system: str
    action: str
    notes: str


class PreliminaryReport(BaseModel):
    """Standard Preliminary Report conforming to AeroIntel Brief Section 7."""
    report_id: str
    alert_id: str
    created_at_utc: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    event_start_utc: datetime
    event_end_utc: datetime
    aircraft_id: Optional[str] = None
    event_type: str
    observed_measurements: Dict[str, Any] = Field(default_factory=dict)
    calculated_changes: Dict[str, Any] = Field(default_factory=dict)
    detection_method: str
    thresholds_or_model_version: str
    anomaly_score: Optional[float] = None
    score_interpretation: str = "Demo setting; uncalibrated operational risk"
    source_name: str = "Synthetic Demo Dataset"
    source_retrieved_at_utc: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    data_quality_warnings: List[str] = Field(default_factory=list)
    evidence_references: List[str] = Field(default_factory=list)
    initial_assessment: str
    unknowns: List[str] = Field(default_factory=list)
    lifecycle_status: LifecycleStatus = LifecycleStatus.DETECTED
    revision_history: List[RevisionEntry] = Field(default_factory=list)
    associated_incident_id: Optional[str] = None
    association_rationale: Optional[str] = None
    association_confidence: Optional[str] = None


class IncidentRecord(BaseModel):
    """Schema for an aviation safety incident narrative."""
    report_id: str
    event_date: datetime
    location: str
    category: str
    narrative: str
    aircraft_type: Optional[str] = None
    source_name: str = "Demo Safety Database"
    source_url: Optional[str] = None
    is_synthetic: bool = True
    summary: Optional[str] = None
    extracted_entities: Dict[str, List[str]] = Field(default_factory=dict)
    predicted_category: Optional[str] = None
    classifier_confidence: Optional[float] = None


class EvidenceLink(BaseModel):
    """Evidence-backed link between a telemetry alert and an incident report."""
    alert_id: str
    incident_id: str
    link_rationale: str
    supporting_evidence: List[str]
    limitations: List[str]
    confidence_level: str  # e.g., "Low", "Medium", "High", "Needs Review"
    is_supported: bool = False
