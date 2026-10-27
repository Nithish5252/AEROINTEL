"""Dataset loaders with automatic fallback, initialization, and validation."""

from pathlib import Path
from typing import Tuple, List, Optional
import pandas as pd

from aerointel.config import config
from aerointel.data.generator import ensure_demo_datasets
from aerointel.data.validation import validate_flight_dataframe


def load_flight_data(filepath: Optional[Path] = None) -> Tuple[pd.DataFrame, List[str]]:
    """Load flight telemetry dataset with validation and automatic demo dataset generation."""
    target_path = filepath or config.demo_flights_path
    warnings: List[str] = []

    if not target_path.exists():
        ensure_demo_datasets(config.data_dir)
        warnings.append(f"Initialized demo flight dataset at {target_path}.")

    try:
        df = pd.read_csv(target_path)
        if "timestamp" in df.columns:
            df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
        if "is_synthetic" not in df.columns:
            df["is_synthetic"] = True
        if "source" not in df.columns:
            df["source"] = "Demo Dataset"

        clean_df, val_warnings = validate_flight_dataframe(df)
        warnings.extend(val_warnings)
        return clean_df, warnings
    except Exception as e:
        warnings.append(f"Error loading flight data: {e}")
        return pd.DataFrame(), warnings


def load_incident_data(filepath: Optional[Path] = None) -> Tuple[pd.DataFrame, List[str]]:
    """Load incident narrative dataset with automatic demo generation."""
    target_path = filepath or config.demo_incidents_path
    warnings: List[str] = []

    if not target_path.exists():
        ensure_demo_datasets(config.data_dir)
        warnings.append(f"Initialized demo incidents dataset at {target_path}.")

    try:
        df = pd.read_csv(target_path)
        if "event_date" in df.columns:
            df["event_date"] = pd.to_datetime(df["event_date"], errors="coerce")
        if "is_synthetic" not in df.columns:
            df["is_synthetic"] = True

        # Drop records with missing report_id or narrative
        valid_mask = df["report_id"].notna() & df["narrative"].notna() & (df["narrative"].str.strip() != "")
        clean_df = df[valid_mask].copy()

        dropped = len(df) - len(clean_df)
        if dropped > 0:
            warnings.append(f"Filtered out {dropped} incident records with missing narratives or IDs.")

        return clean_df, warnings
    except Exception as e:
        warnings.append(f"Error loading incident data: {e}")
        return pd.DataFrame(), warnings
