"""Central configuration management for AeroIntel."""

from dataclasses import dataclass, field
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Base project paths
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DEMO_FLIGHTS_PATH = DATA_DIR / "demo_flights.csv"
DEMO_INCIDENTS_PATH = DATA_DIR / "demo_incidents.csv"


@dataclass
class AnomalyThresholds:
    """Demonstration thresholds for rule-assisted anomaly detection.
    
    NOTE: These thresholds are demonstration settings for prototype testing,
    not official aviation safety standards.
    """
    max_vertical_rate_fpm: float = float(
        os.getenv("AEROINTEL_VERTICAL_RATE_THRESHOLD_FPM", 3000.0)
    )
    max_speed_change_kt: float = float(
        os.getenv("AEROINTEL_SPEED_CHANGE_THRESHOLD_KT", 45.0)
    )
    max_stale_telemetry_sec: float = float(
        os.getenv("AEROINTEL_STALE_TELEMETRY_THRESHOLD_SEC", 180.0)
    )
    min_observations_for_ml: int = 15


@dataclass
class AppConfig:
    """Global configuration settings for AeroIntel."""
    app_name: str = "AeroIntel"
    version: str = "1.0.0"
    demo_mode: bool = os.getenv("AEROINTEL_DEMO_MODE", "true").lower() in ("true", "1", "yes")
    env: str = os.getenv("AEROINTEL_ENV", "development")
    
    # OpenSky Network credentials
    opensky_username: str = os.getenv("OPENSKY_USERNAME", "")
    opensky_password: str = os.getenv("OPENSKY_PASSWORD", "")
    opensky_api_url: str = "https://opensky-network.org/api/states/all"
    
    # Paths
    base_dir: Path = BASE_DIR
    data_dir: Path = DATA_DIR
    demo_flights_path: Path = DEMO_FLIGHTS_PATH
    demo_incidents_path: Path = DEMO_INCIDENTS_PATH
    
    # Detector thresholds
    thresholds: AnomalyThresholds = field(default_factory=AnomalyThresholds)


config = AppConfig()
