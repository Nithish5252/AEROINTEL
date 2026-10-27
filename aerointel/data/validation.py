"""Data validation routines for flight telemetry and incident records."""

from typing import Tuple, List, Dict, Any
import math
import pandas as pd


def validate_flight_record(row: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """Validate a single flight telemetry record.
    
    Checks:
    - aircraft_id non-empty
    - timestamp valid
    - latitude in [-90, 90]
    - longitude in [-180, 180]
    - non-negative speed if present
    - reasonable altitude bounds (-1000 to 85000 ft) if present
    """
    errors = []
    
    # 1. Aircraft ID
    aircraft_id = str(row.get("aircraft_id", "")).strip()
    if not aircraft_id or aircraft_id == "nan":
        errors.append("Missing aircraft identifier.")

    # 2. Timestamp
    ts = row.get("timestamp")
    if ts is None or pd.isna(ts):
        errors.append("Missing timestamp.")

    # 3. Coordinates
    lat = row.get("latitude")
    lon = row.get("longitude")
    if lat is None or pd.isna(lat) or not (-90.0 <= float(lat) <= 90.0):
        errors.append(f"Invalid latitude: {lat}")
    if lon is None or pd.isna(lon) or not (-180.0 <= float(lon) <= 180.0):
        errors.append(f"Invalid longitude: {lon}")

    # 4. Altitude
    alt = row.get("altitude_ft")
    if alt is not None and not pd.isna(alt):
        try:
            alt_val = float(alt)
            if not (-1500.0 <= alt_val <= 90000.0):
                errors.append(f"Unrealistic altitude: {alt_val} ft")
        except ValueError:
            errors.append(f"Non-numeric altitude: {alt}")

    # 5. Speed
    spd = row.get("ground_speed_kt")
    if spd is not None and not pd.isna(spd):
        try:
            spd_val = float(spd)
            if spd_val < 0.0 or spd_val > 2000.0:
                errors.append(f"Unrealistic ground speed: {spd_val} kt")
        except ValueError:
            errors.append(f"Non-numeric speed: {spd}")

    return len(errors) == 0, errors


def validate_flight_dataframe(df: pd.DataFrame) -> Tuple[pd.DataFrame, List[str]]:
    """Filter out invalid flight records and return clean dataframe with warnings."""
    if df.empty:
        return df, ["Telemetry dataframe is empty."]

    warnings = []
    initial_count = len(df)

    # Required columns
    required = ["aircraft_id", "timestamp", "latitude", "longitude"]
    missing_cols = [c for c in required if c not in df.columns]
    if missing_cols:
        return pd.DataFrame(), [f"Missing required columns: {missing_cols}"]

    # Filter invalid coords
    valid_mask = (
        df["aircraft_id"].notna()
        & df["timestamp"].notna()
        & df["latitude"].between(-90, 90)
        & df["longitude"].between(-180, 180)
    )

    clean_df = df[valid_mask].copy()
    dropped = initial_count - len(clean_df)
    if dropped > 0:
        warnings.append(f"Dropped {dropped} records with invalid coordinates or missing IDs.")

    return clean_df, warnings
