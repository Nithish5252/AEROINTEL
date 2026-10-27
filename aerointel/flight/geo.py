"""Geographic calculations and spatial filtering for flight tracking."""

import math
from typing import Tuple, List, Optional
import pandas as pd


EARTH_RADIUS_KM = 6371.0


def validate_coordinates(latitude: float, longitude: float) -> Tuple[bool, Optional[str]]:
    """Validate latitude and longitude ranges.
    
    Returns:
        (is_valid, error_message)
    """
    if not isinstance(latitude, (int, float)) or not isinstance(longitude, (int, float)):
        return False, "Coordinates must be numeric."
    if math.isnan(latitude) or math.isnan(longitude):
        return False, "Coordinates cannot be NaN."
    if not (-90.0 <= latitude <= 90.0):
        return False, f"Latitude {latitude} out of bounds [-90, 90]."
    if not (-180.0 <= longitude <= 180.0):
        return False, f"Longitude {longitude} out of bounds [-180, 180]."
    return True, None


def haversine_distance_km(
    lat1: float, lon1: float, lat2: float, lon2: float
) -> float:
    """Calculate the great-circle distance between two points on Earth using Haversine formula.
    
    Args:
        lat1, lon1: First point in decimal degrees
        lat2, lon2: Second point in decimal degrees
        
    Returns:
        Distance in kilometers
    """
    val1, err1 = validate_coordinates(lat1, lon1)
    val2, err2 = validate_coordinates(lat2, lon2)
    if not val1 or not val2:
        raise ValueError(f"Invalid coordinates: {err1 or err2}")

    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = (
        math.sin(delta_phi / 2.0) ** 2
        + math.cos(phi1) * math.cos(phi2) * (math.sin(delta_lambda / 2.0) ** 2)
    )
    # Clip to [0, 1] to prevent floating point domain errors in sqrt/asin
    a = min(1.0, max(0.0, a))
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))

    return EARTH_RADIUS_KM * c


def filter_by_radius(
    df: pd.DataFrame,
    center_lat: float,
    center_lon: float,
    radius_km: float,
    lat_col: str = "latitude",
    lon_col: str = "longitude",
) -> pd.DataFrame:
    """Filter observations to those within a radius from a center point.
    
    Args:
        df: DataFrame containing flight records
        center_lat, center_lon: Center location
        radius_km: Radius in kilometers
        lat_col, lon_col: Column names for latitude and longitude
        
    Returns:
        Filtered DataFrame with an added 'distance_to_center_km' column
    """
    if df.empty:
        return df.copy()

    val_center, err = validate_coordinates(center_lat, center_lon)
    if not val_center:
        raise ValueError(f"Invalid center coordinate: {err}")

    # Drop rows with invalid coordinates
    valid_coords = df[lat_col].between(-90, 90) & df[lon_col].between(-180, 180)
    filtered = df[valid_coords].copy()

    if filtered.empty:
        filtered["distance_to_center_km"] = []
        return filtered

    distances = [
        haversine_distance_km(center_lat, center_lon, lat, lon)
        for lat, lon in zip(filtered[lat_col], filtered[lon_col])
    ]
    filtered["distance_to_center_km"] = distances
    return filtered[filtered["distance_to_center_km"] <= radius_km].copy()


def get_bounding_box(
    center_lat: float, center_lon: float, radius_km: float
) -> Tuple[float, float, float, float]:
    """Calculate approximate bounding box (min_lat, max_lat, min_lon, max_lon)."""
    delta_lat = radius_km / 111.0
    # Avoid division by zero near poles
    cos_lat = max(0.01, math.cos(math.radians(center_lat)))
    delta_lon = radius_km / (111.0 * cos_lat)

    min_lat = max(-90.0, center_lat - delta_lat)
    max_lat = min(90.0, center_lat + delta_lat)
    min_lon = max(-180.0, center_lon - delta_lon)
    max_lon = min(180.0, center_lon + delta_lon)

    return min_lat, max_lat, min_lon, max_lon
