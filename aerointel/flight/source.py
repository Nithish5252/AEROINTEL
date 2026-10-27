"""Flight data ingestion: local demo provider and OpenSky Network live ADS-B API client."""

import logging
from datetime import datetime, timezone
from typing import Optional, Tuple
import pandas as pd
import requests

from aerointel.config import config
from aerointel.flight.geo import get_bounding_box, filter_by_radius

logger = logging.getLogger(__name__)


class FlightDataSource:
    """Manages flight telemetry ingestion with local demo data and live OpenSky API."""

    def __init__(self, demo_file_path: Optional[str] = None):
        self.demo_file_path = demo_file_path or str(config.demo_flights_path)

    def load_demo_data(self) -> pd.DataFrame:
        """Load the local synthetic demo flight dataset."""
        try:
            df = pd.read_csv(self.demo_file_path)
            df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
            df["is_synthetic"] = True
            return df
        except Exception as e:
            logger.error(f"Failed to load demo flight data from {self.demo_file_path}: {e}")
            return pd.DataFrame()

    @staticmethod
    def fetch_live_opensky(
        center_lat: float,
        center_lon: float,
        radius_km: float = 150.0,
        airborne_only: bool = True,
        timeout_sec: float = 8.0,
    ) -> Tuple[pd.DataFrame, bool, str]:
        """Fetch live ADS-B state vectors from OpenSky Network REST API within search radius.
        
        Args:
            center_lat, center_lon: Center coordinates for the search area
            radius_km: Search radius in kilometers
            airborne_only: Filter out planes parked or taxiing on the ground
            timeout_sec: Network timeout
            
        Returns:
            (df, success, status_message)
        """
        min_lat, max_lat, min_lon, max_lon = get_bounding_box(center_lat, center_lon, radius_km)
        params = {
            "lamin": min_lat,
            "lamax": max_lat,
            "lomin": min_lon,
            "lomax": max_lon,
        }

        auth = None
        if config.opensky_username and config.opensky_password:
            auth = (config.opensky_username, config.opensky_password)

        try:
            response = requests.get(
                config.opensky_api_url,
                params=params,
                auth=auth,
                timeout=timeout_sec,
            )
            if response.status_code == 200:
                data = response.json()
                states = data.get("states", [])
                if not states:
                    return pd.DataFrame(), True, f"OpenSky API connected: 0 aircraft found within {radius_km:.0f} km."

                records = []
                now_utc = datetime.now(timezone.utc)
                for s in states:
                    # s[5]=lon, s[6]=lat. Must have valid coordinates.
                    if s[5] is None or s[6] is None:
                        continue

                    # s[8]=on_ground. Filter if airborne_only requested.
                    on_ground = bool(s[8]) if s[8] is not None else False
                    if airborne_only and on_ground:
                        continue

                    callsign = (s[1] or "").strip()
                    icao24 = (s[0] or "").strip()
                    aircraft_id = callsign if callsign else f"ICAO-{icao24.upper()}"

                    # Timestamps
                    ts_val = s[3] if s[3] is not None else (s[4] if s[4] is not None else int(now_utc.timestamp()))
                    obs_time = pd.to_datetime(ts_val, unit="s", utc=True)

                    # Altitude, speed, vertical rate conversions
                    alt_ft = round(float(s[7]) * 3.28084, 1) if s[7] is not None else None
                    spd_kt = round(float(s[9]) * 1.94384, 1) if s[9] is not None else None
                    hdg_deg = round(float(s[10]), 1) if s[10] is not None else None
                    vrate_fpm = round(float(s[11]) * 196.85, 1) if s[11] is not None else 0.0

                    records.append({
                        "aircraft_id": aircraft_id,
                        "callsign": callsign,
                        "icao24": icao24,
                        "origin_country": s[2] or "Unknown",
                        "timestamp": obs_time,
                        "latitude": float(s[6]),
                        "longitude": float(s[5]),
                        "altitude_ft": alt_ft,
                        "ground_speed_kt": spd_kt,
                        "heading_deg": hdg_deg,
                        "vertical_rate_fpm": vrate_fpm,
                        "on_ground": on_ground,
                        "source": "OpenSky Network (Live ADS-B)",
                        "is_synthetic": False,
                    })

                if not records:
                    return pd.DataFrame(), True, f"OpenSky API returned aircraft, but none were currently airborne with valid positions."

                df = pd.DataFrame(records)

                # Strict radius filtering around center
                filtered_df = filter_by_radius(df, center_lat, center_lon, radius_km)
                
                return (
                    filtered_df,
                    True,
                    f"Successfully retrieved {len(filtered_df)} live airborne aircraft within {radius_km:.0f} km from OpenSky Network.",
                )
            elif response.status_code == 429:
                return (
                    pd.DataFrame(),
                    False,
                    "OpenSky public rate limit reached. Please wait 10 seconds before refreshing, or switch to Demo Mode.",
                )
            else:
                return (
                    pd.DataFrame(),
                    False,
                    f"OpenSky API returned HTTP {response.status_code}. Using demo fallback.",
                )
        except requests.Timeout:
            return (
                pd.DataFrame(),
                False,
                "OpenSky connection timed out. OpenSky public servers may be busy; please retry in a moment.",
            )
        except Exception as e:
            return (
                pd.DataFrame(),
                False,
                f"OpenSky connection notice: {type(e).__name__} ({e}).",
            )
