"""Live OpenSky Network Radar Service — Scans real-time aircraft and detects anomalies."""

from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Tuple
import pandas as pd

from aerointel.flight.geo import filter_by_radius
from aerointel.flight.source import FlightDataSource
from aerointel.flight.features import compute_flight_features
from aerointel.flight.detector import AnomalyDetector
from aerointel.config import AnomalyThresholds
from aerointel.shared.models import AnomalyAlert


# Standard Indian & Global Airspace Presets (India as Primary)
AIRSPACE_PRESETS: Dict[str, Tuple[float, float, float]] = {
    "🇮🇳 All India Airspace (National Trunk Corridors)": (21.15, 79.09, 850.0),
    "🇮🇳 Delhi NCR Airspace (DEL / IGI Airport)": (28.556, 77.100, 300.0),
    "🇮🇳 Mumbai TMA (BOM / Chhatrapati Shivaji)": (19.089, 72.865, 300.0),
    "🇮🇳 Bengaluru Airspace (BLR / Kempegowda)": (13.198, 77.706, 300.0),
    "🇮🇳 Chennai Airspace (MAA / Meenambakkam)": (12.994, 80.170, 300.0),
    "🇮🇳 Kolkata Airspace (CCU / Netaji Subhash)": (22.654, 88.446, 300.0),
    "🇮🇳 Hyderabad Airspace (HYD / Rajiv Gandhi)": (17.240, 78.429, 300.0),
    "🗽 New York Metro (JFK / EWR / LGA)": (40.71, -73.95, 150.0),
    "🇬🇧 London Airspace (Heathrow / Gatwick)": (51.50, -0.12, 130.0),
    "🏙️ Chicago Airspace (O'Hare / Midway)": (41.88, -87.63, 140.0),
    "🎯 Custom Search Coordinates": (21.15, 79.09, 850.0),
}

# Real-World Airline Call Sign Mapping
AIRLINE_IATA_MAPPING = {
    "IGO": ("IndiGo", "6E", "🇮🇳"),
    "AIC": ("Air India", "AI", "🇮🇳"),
    "SEJ": ("SpiceJet", "SG", "🇮🇳"),
    "AKJ": ("Akasa Air", "QP", "🇮🇳"),
    "VTI": ("Vistara", "UK", "🇮🇳"),
    "AXB": ("Air India Express", "IX", "🇮🇳"),
    "IXR": ("Air India Express", "IX", "🇮🇳"),
    "GOW": ("Go First", "G8", "🇮🇳"),
    "BAW": ("British Airways", "BA", "🇬🇧"),
    "UAE": ("Emirates", "EK", "🇦🇪"),
    "QTR": ("Qatar Airways", "QR", "🇶🇦"),
    "ETD": ("Etihad Airways", "EY", "🇦🇪"),
    "SIA": ("Singapore Airlines", "SQ", "🇸🇬"),
    "THA": ("Thai Airways", "TG", "🇹🇭"),
    "LHA": ("Lufthansa", "LH", "🇩🇪"),
    "KLM": ("KLM Royal Dutch", "KL", "🇳🇱"),
    "AFR": ("Air France", "AF", "🇫🇷"),
    "DAL": ("Delta Air Lines", "DL", "🇺🇸"),
    "UAL": ("United Airlines", "UA", "🇺🇸"),
}


def decode_airline_info(callsign: str) -> Tuple[str, str, str]:
    """Decode airline name, IATA code, and flag from callsign."""
    cs = (callsign or "").strip().upper()
    for prefix, (name, iata, flag) in AIRLINE_IATA_MAPPING.items():
        if cs.startswith(prefix):
            return name, iata, flag
    return "Commercial / General Aviation", "", "✈️"


def scan_live_airspace(
    center_lat: float,
    center_lon: float,
    radius_km: float = 850.0,
    history_df: Optional[pd.DataFrame] = None,
    thresholds: Optional[AnomalyThresholds] = None,
    airborne_only: bool = True,
    timeout_sec: float = 14.0,
) -> Tuple[pd.DataFrame, pd.DataFrame, List[AnomalyAlert], bool, str, pd.DataFrame]:
    """Execute a real-time scan of aircraft via OpenSky Network and detect anomalies.
    
    Args:
        center_lat: Search area latitude
        center_lon: Search area longitude
        radius_km: Radius in kilometers
        history_df: Optional previous observations DataFrame for building multi-point trails
        thresholds: Detection thresholds
        airborne_only: Whether to ignore parked/taxiing aircraft
        timeout_sec: Network timeout
        
    Returns:
        (latest_df, features_df, alerts, success, message, updated_history_df)
    """
    df_new, success, msg = FlightDataSource.fetch_live_opensky(
        center_lat=center_lat,
        center_lon=center_lon,
        radius_km=radius_km,
        airborne_only=airborne_only,
        timeout_sec=timeout_sec,
    )

    if not success or df_new.empty:
        existing_history = history_df if history_df is not None else pd.DataFrame()
        return df_new, pd.DataFrame(), [], success, msg, existing_history

    # Maintain history buffer for multi-point trajectory tracking
    if history_df is not None and not history_df.empty:
        now = datetime.now(timezone.utc)
        cutoff = now - timedelta(minutes=30)
        history_clean = history_df[history_df["timestamp"] >= cutoff]
        updated_history = pd.concat([history_clean, df_new], ignore_index=True)
        updated_history = updated_history.drop_duplicates(subset=["aircraft_id", "timestamp"], keep="last")
        if len(updated_history) > 6000:
            updated_history = updated_history.iloc[-6000:].copy()
    else:
        updated_history = df_new.copy()

    # Compute features on accumulated history (or single snapshot)
    features_df = compute_flight_features(updated_history)

    # Detect anomalies
    detector = AnomalyDetector(thresholds)
    rule_alerts = detector.detect_rule_anomalies(features_df)
    ml_alerts = detector.detect_isolation_forest_anomalies(features_df)
    all_alerts = rule_alerts + ml_alerts

    status_message = (
        f"✅ Live Radar Active: {len(df_new)} airborne aircraft tracked within {radius_km:.0f} km. "
        f"Found {len(all_alerts)} movement alert(s)."
    )

    return df_new, features_df, all_alerts, True, status_message, updated_history
