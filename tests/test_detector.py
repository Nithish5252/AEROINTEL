"""Tests for telemetry feature extraction, anomaly detector rules, and preliminary reports."""

from datetime import datetime, timedelta, timezone
import pandas as pd
import pytest

from aerointel.config import AnomalyThresholds
from aerointel.flight.features import compute_flight_features
from aerointel.flight.detector import AnomalyDetector
from aerointel.flight.reports import generate_preliminary_report
from aerointel.shared.models import AnomalyType, LifecycleStatus


@pytest.fixture
def base_time():
    return datetime(2026, 10, 26, 12, 0, 0, tzinfo=timezone.utc)


def test_normal_sequence_no_alerts(base_time):
    # Aircraft flying smoothly
    rows = []
    for i in range(10):
        rows.append({
            "aircraft_id": "TEST-NORM",
            "timestamp": base_time + timedelta(seconds=i * 15),
            "latitude": 40.0 + i * 0.01,
            "longitude": -74.0 + i * 0.01,
            "altitude_ft": 30000.0,
            "ground_speed_kt": 450.0,
            "heading_deg": 90.0,
            "vertical_rate_fpm": 0.0,
            "source": "Test",
            "is_synthetic": True,
        })
    df = pd.DataFrame(rows)
    df_feat = compute_flight_features(df)
    
    detector = AnomalyDetector()
    alerts = detector.detect_rule_anomalies(df_feat)
    assert len(alerts) == 0


def test_rapid_altitude_change_alert(base_time):
    rows = [
        {
            "aircraft_id": "TEST-DIVE",
            "timestamp": base_time,
            "latitude": 40.0,
            "longitude": -74.0,
            "altitude_ft": 30000.0,
            "ground_speed_kt": 450.0,
            "heading_deg": 90.0,
            "vertical_rate_fpm": 0.0,
        },
        {
            "aircraft_id": "TEST-DIVE",
            "timestamp": base_time + timedelta(seconds=15),
            "latitude": 40.01,
            "longitude": -73.99,
            "altitude_ft": 29000.0,  # 1000 ft drop in 15s = 4000 fpm
            "ground_speed_kt": 450.0,
            "heading_deg": 90.0,
            "vertical_rate_fpm": -4000.0,
        },
    ]
    df = pd.DataFrame(rows)
    df_feat = compute_flight_features(df)

    thresholds = AnomalyThresholds(max_vertical_rate_fpm=3000.0)
    detector = AnomalyDetector(thresholds)
    alerts = detector.detect_rule_anomalies(df_feat)

    assert len(alerts) >= 1
    alt_alert = [a for a in alerts if a.event_type == AnomalyType.RAPID_ALTITUDE_CHANGE][0]
    assert alt_alert.aircraft_id == "TEST-DIVE"
    assert abs(alt_alert.observed_value) >= 3000.0

    # Test Section 7 preliminary report generation
    report = generate_preliminary_report(alt_alert)
    assert report.alert_id == alt_alert.alert_id
    assert report.aircraft_id == "TEST-DIVE"
    assert report.lifecycle_status == LifecycleStatus.DETECTED
    assert "not, by itself, evidence of an emergency" in report.initial_assessment
    assert len(report.unknowns) >= 3
    assert len(report.revision_history) == 1


def test_abrupt_speed_drop_alert(base_time):
    rows = [
        {"aircraft_id": "TEST-SLOW", "timestamp": base_time, "latitude": 40.0, "longitude": -74.0, "ground_speed_kt": 400.0},
        {"aircraft_id": "TEST-SLOW", "timestamp": base_time + timedelta(seconds=15), "latitude": 40.01, "longitude": -73.99, "ground_speed_kt": 330.0},  # 70 kt loss
    ]
    df = pd.DataFrame(rows)
    df_feat = compute_flight_features(df)

    thresholds = AnomalyThresholds(max_speed_change_kt=45.0)
    detector = AnomalyDetector(thresholds)
    alerts = detector.detect_rule_anomalies(df_feat)

    spd_alerts = [a for a in alerts if a.event_type == AnomalyType.ABRUPT_SPEED_DROP]
    assert len(spd_alerts) == 1
    assert spd_alerts[0].observed_value == -70.0


def test_stale_telemetry_gap_alert(base_time):
    rows = [
        {"aircraft_id": "TEST-GAP", "timestamp": base_time, "latitude": 40.0, "longitude": -74.0, "altitude_ft": 20000.0},
        {"aircraft_id": "TEST-GAP", "timestamp": base_time + timedelta(seconds=240), "latitude": 40.1, "longitude": -74.1, "altitude_ft": 20000.0},
    ]
    df = pd.DataFrame(rows)
    df_feat = compute_flight_features(df)

    thresholds = AnomalyThresholds(max_stale_telemetry_sec=180.0)
    detector = AnomalyDetector(thresholds)
    alerts = detector.detect_rule_anomalies(df_feat)

    gap_alerts = [a for a in alerts if a.event_type == AnomalyType.STALE_TELEMETRY]
    assert len(gap_alerts) == 1
    assert gap_alerts[0].observed_value == 240.0


def test_duplicate_and_out_of_order_timestamps(base_time):
    # Observations intentionally out of order with a duplicate
    rows = [
        {"aircraft_id": "TEST-SORT", "timestamp": base_time + timedelta(seconds=30), "latitude": 40.02, "longitude": -73.98, "altitude_ft": 25000.0},
        {"aircraft_id": "TEST-SORT", "timestamp": base_time, "latitude": 40.00, "longitude": -74.00, "altitude_ft": 25000.0},
        {"aircraft_id": "TEST-SORT", "timestamp": base_time, "latitude": 40.00, "longitude": -74.00, "altitude_ft": 25000.0},  # duplicate
        {"aircraft_id": "TEST-SORT", "timestamp": base_time + timedelta(seconds=15), "latitude": 40.01, "longitude": -73.99, "altitude_ft": 25000.0},
    ]
    df = pd.DataFrame(rows)
    df_feat = compute_flight_features(df)

    # After cleaning and sorting, should have 3 unique sorted timestamps
    assert len(df_feat) == 3
    assert list(df_feat["timestamp"]) == sorted(list(df_feat["timestamp"]))
    assert (df_feat["time_delta_sec"].dropna() == 15.0).all()
