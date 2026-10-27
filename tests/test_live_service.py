"""Unit tests for Live OpenSky Radar Service."""

from unittest.mock import patch
import pandas as pd
from datetime import datetime, timezone

from aerointel.flight.live_service import AIRSPACE_PRESETS, scan_live_airspace


def test_airspace_presets_exist():
    assert len(AIRSPACE_PRESETS) >= 5
    assert "🗽 New York Metro (JFK / EWR / LGA)" in AIRSPACE_PRESETS
    lat, lon, r = AIRSPACE_PRESETS["🗽 New York Metro (JFK / EWR / LGA)"]
    assert 35.0 <= lat <= 45.0
    assert -85.0 <= lon <= -70.0
    assert r > 50.0


@patch("aerointel.flight.source.FlightDataSource.fetch_live_opensky")
def test_scan_live_airspace_mock(mock_fetch):
    now = datetime.now(timezone.utc)
    mock_df = pd.DataFrame([
        {
            "aircraft_id": "TEST-101",
            "callsign": "TEST101",
            "icao24": "A1B2C3",
            "origin_country": "United States",
            "timestamp": now,
            "latitude": 40.71,
            "longitude": -73.95,
            "altitude_ft": 3000.0,
            "ground_speed_kt": 310.0,  # Exceeds 275 kt below 10,000 ft -> should trigger Rule 4
            "heading_deg": 180.0,
            "vertical_rate_fpm": -3500.0,  # Exceeds 2,500 fpm -> should trigger Rule 1
            "on_ground": False,
            "source": "OpenSky Network (Live ADS-B)",
            "is_synthetic": False,
        }
    ])
    mock_fetch.return_value = (mock_df, True, "Mock success")

    latest_df, feat_df, alerts, ok, msg, history = scan_live_airspace(40.71, -73.95, 100.0)

    assert ok is True
    assert len(latest_df) == 1
    assert len(history) == 1
    # Both steep vertical rate and speed exceedance should be detected!
    assert len(alerts) >= 1
    alert_types = {a.event_type.value for a in alerts}
    assert "Rapid Altitude Change" in alert_types or "Low Altitude High-Speed Exceedance" in alert_types
