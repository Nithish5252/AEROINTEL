"""Tests for geographic calculations and radius filtering."""

import pytest
import pandas as pd
from aerointel.flight.geo import (
    validate_coordinates,
    haversine_distance_km,
    filter_by_radius,
    get_bounding_box,
)


def test_validate_coordinates():
    # Valid
    assert validate_coordinates(0.0, 0.0)[0] is True
    assert validate_coordinates(40.6413, -73.7781)[0] is True
    assert validate_coordinates(-90.0, 180.0)[0] is True

    # Invalid latitude
    assert validate_coordinates(91.0, 0.0)[0] is False
    assert validate_coordinates(-90.1, 0.0)[0] is False

    # Invalid longitude
    assert validate_coordinates(0.0, 180.1)[0] is False
    assert validate_coordinates(0.0, -180.1)[0] is False

    # Non-numeric / NaN
    assert validate_coordinates(float("nan"), 0.0)[0] is False


def test_haversine_known_distance():
    # JFK (40.6413, -73.7781) to Boston Logan (42.3656, -71.0096) is approximately 300-310 km
    dist = haversine_distance_km(40.6413, -73.7781, 42.3656, -71.0096)
    assert 295.0 <= dist <= 315.0

    # Distance to same point is zero
    assert haversine_distance_km(51.5, -0.1, 51.5, -0.1) == pytest.approx(0.0, abs=1e-5)


def test_filter_by_radius():
    df = pd.DataFrame([
        {"aircraft_id": "AC1", "latitude": 40.6413, "longitude": -73.7781},  # JFK: ~0 km from JFK
        {"aircraft_id": "AC2", "latitude": 42.3656, "longitude": -71.0096},  # BOS: ~300 km from JFK
        {"aircraft_id": "AC3", "latitude": 51.5074, "longitude": -0.1278},   # LHR: ~5500 km from JFK
    ])

    # Radius of 50 km around JFK
    filtered_50 = filter_by_radius(df, 40.6413, -73.7781, radius_km=50.0)
    assert len(filtered_50) == 1
    assert filtered_50.iloc[0]["aircraft_id"] == "AC1"

    # Radius of 350 km around JFK includes JFK and BOS
    filtered_350 = filter_by_radius(df, 40.6413, -73.7781, radius_km=350.0)
    assert len(filtered_350) == 2
    assert set(filtered_350["aircraft_id"]) == {"AC1", "AC2"}


def test_bounding_box():
    min_lat, max_lat, min_lon, max_lon = get_bounding_box(40.0, -70.0, radius_km=111.0)
    # Approx 1 degree lat
    assert min_lat == pytest.approx(39.0, abs=0.1)
    assert max_lat == pytest.approx(41.0, abs=0.1)
    assert min_lon < -70.0 < max_lon
