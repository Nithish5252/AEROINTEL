"""Feature engineering for flight telemetry time-series."""

from typing import Optional
import numpy as np
import pandas as pd


MAX_CONSECUTIVE_GAP_SEC = 900.0  # 15 minutes: beyond this, treat as separate legs


def compute_heading_change(h1: float, h2: float) -> Optional[float]:
    """Calculate the minimal angular change between two headings in [-180, 180]."""
    if pd.isna(h1) or pd.isna(h2):
        return None
    diff = (h2 - h1 + 180.0) % 360.0 - 180.0
    return abs(diff)


def compute_flight_features(
    df: pd.DataFrame,
    aircraft_col: str = "aircraft_id",
    time_col: str = "timestamp",
    alt_col: str = "altitude_ft",
    spd_col: str = "ground_speed_kt",
    hdg_col: str = "heading_deg",
    vrate_col: str = "vertical_rate_fpm",
) -> pd.DataFrame:
    """Compute rates of change and interval features for consecutive aircraft observations.
    
    Safe principles:
    - Sorts by aircraft and timestamp
    - Removes duplicate consecutive timestamps
    - Never calculates changes across different aircraft
    - Does not calculate rates when time gaps exceed MAX_CONSECUTIVE_GAP_SEC
    - Preserves missing values (never converts NaN to 0)
    """
    if df.empty:
        return df.copy()

    df_clean = df.copy()
    
    # Ensure datetime format
    if not pd.api.types.is_datetime64_any_dtype(df_clean[time_col]):
        df_clean[time_col] = pd.to_datetime(df_clean[time_col], utc=True)

    # Sort strictly by aircraft and timestamp
    df_clean = df_clean.sort_values(by=[aircraft_col, time_col]).reset_index(drop=True)

    # Drop duplicate observations for same aircraft & timestamp
    df_clean = df_clean.drop_duplicates(subset=[aircraft_col, time_col], keep="last").reset_index(drop=True)

    # Group by aircraft for consecutive calculations
    groups = df_clean.groupby(aircraft_col, group_keys=False)

    # 1. Time delta in seconds
    df_clean["time_delta_sec"] = groups[time_col].diff().dt.total_seconds()

    # Valid consecutive mask: positive time delta within reasonable threshold
    valid_step = (df_clean["time_delta_sec"] > 0) & (
        df_clean["time_delta_sec"] <= MAX_CONSECUTIVE_GAP_SEC
    )

    # 2. Altitude delta & calculated vertical rate (fpm)
    if alt_col in df_clean.columns:
        df_clean["altitude_delta_ft"] = groups[alt_col].diff()
        # Invalidate if gap was too large or time_delta <= 0
        df_clean.loc[~valid_step, "altitude_delta_ft"] = np.nan
        df_clean["calculated_vrate_fpm"] = np.where(
            valid_step & df_clean[alt_col].notna() & df_clean["altitude_delta_ft"].notna(),
            (df_clean["altitude_delta_ft"] / df_clean["time_delta_sec"]) * 60.0,
            np.nan,
        )
        # Use reported vertical_rate_fpm if present, otherwise fallback to calculated
        if vrate_col in df_clean.columns:
            df_clean["effective_vrate_fpm"] = df_clean[vrate_col].combine_first(
                df_clean["calculated_vrate_fpm"]
            )
        else:
            df_clean["effective_vrate_fpm"] = df_clean["calculated_vrate_fpm"]
    else:
        df_clean["altitude_delta_ft"] = np.nan
        df_clean["calculated_vrate_fpm"] = np.nan
        df_clean["effective_vrate_fpm"] = np.nan

    # 3. Ground speed delta & acceleration (kt/s)
    if spd_col in df_clean.columns:
        df_clean["speed_delta_kt"] = groups[spd_col].diff()
        df_clean.loc[~valid_step, "speed_delta_kt"] = np.nan
        df_clean["acceleration_kt_s"] = np.where(
            valid_step & df_clean[spd_col].notna() & df_clean["speed_delta_kt"].notna(),
            df_clean["speed_delta_kt"] / df_clean["time_delta_sec"],
            np.nan,
        )
    else:
        df_clean["speed_delta_kt"] = np.nan
        df_clean["acceleration_kt_s"] = np.nan

    # 4. Heading delta
    if hdg_col in df_clean.columns:
        prev_hdg = groups[hdg_col].shift(1)
        heading_deltas = [
            compute_heading_change(h1, h2) if vs else np.nan
            for h1, h2, vs in zip(prev_hdg, df_clean[hdg_col], valid_step)
        ]
        df_clean["heading_delta_deg"] = heading_deltas
    else:
        df_clean["heading_delta_deg"] = np.nan

    return df_clean
