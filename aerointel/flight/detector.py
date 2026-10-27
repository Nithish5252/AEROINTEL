"""Anomaly detection engine for flight telemetry using transparent rules and ML."""

import uuid
from datetime import datetime, timezone
from typing import List, Optional, Tuple
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest

from aerointel.config import AnomalyThresholds
from aerointel.shared.models import AnomalyAlert, AnomalyType


class AnomalyDetector:
    """Hybrid telemetry anomaly detector combining interpretable rules and Isolation Forest.
    
    IMPORTANT: Detections are demonstration signals based on configured thresholds.
    They never represent verified emergencies or mechanical failures.
    """

    def __init__(self, thresholds: Optional[AnomalyThresholds] = None):
        self.thresholds = thresholds or AnomalyThresholds()

    @staticmethod
    def _safe_window_start(obs_time, td, default_sec: float = 10.0):
        sec = float(td) if pd.notna(td) and td is not None else default_sec
        return obs_time - pd.Timedelta(seconds=sec)

    def detect_rule_anomalies(self, df_features: pd.DataFrame) -> List[AnomalyAlert]:
        """Detect anomalies using transparent, interpretable threshold rules."""
        alerts: List[AnomalyAlert] = []
        if df_features.empty:
            return alerts

        for idx, row in df_features.iterrows():
            aircraft_id = str(row.get("aircraft_id", "UNKNOWN"))
            obs_time = row["timestamp"]
            is_synthetic = bool(row.get("is_synthetic", True))
            source_name = str(row.get("source", "Telemetry Stream"))

            # 1. Rule: Rapid Vertical Rate (Climb or Descent)
            vrate = row.get("effective_vrate_fpm")
            if pd.isna(vrate):
                vrate = row.get("vertical_rate_fpm")
            if pd.notna(vrate) and abs(vrate) >= self.thresholds.max_vertical_rate_fpm:
                prev_time = self._safe_window_start(obs_time, row.get("time_delta_sec"))
                alerts.append(
                    AnomalyAlert(
                        alert_id=f"ALT-VR-{uuid.uuid4().hex[:8].upper()}",
                        aircraft_id=aircraft_id,
                        event_type=AnomalyType.RAPID_ALTITUDE_CHANGE,
                        triggered_at_utc=obs_time.to_pydatetime() if hasattr(obs_time, "to_pydatetime") else obs_time,
                        window_start_utc=prev_time.to_pydatetime() if hasattr(prev_time, "to_pydatetime") else prev_time,
                        window_end_utc=obs_time.to_pydatetime() if hasattr(obs_time, "to_pydatetime") else obs_time,
                        detection_method=f"Rule: Vertical Rate Threshold (>= {self.thresholds.max_vertical_rate_fpm:,.0f} fpm)",
                        threshold_value=self.thresholds.max_vertical_rate_fpm,
                        observed_value=round(float(vrate), 1),
                        unit="fpm",
                        anomaly_score=round(min(1.0, abs(vrate) / (self.thresholds.max_vertical_rate_fpm * 1.5)), 2),
                        quality_warnings=["Vertical rate exceedance triggered; operational context (ATC/weather) unverified."],
                        source_name=source_name,
                        is_synthetic=is_synthetic,
                        supporting_measurements={
                            "vertical_rate_fpm": round(float(vrate), 1),
                            "altitude_ft": row.get("altitude_ft"),
                            "ground_speed_kt": row.get("ground_speed_kt"),
                            "origin_country": row.get("origin_country", "Unknown"),
                            "time_delta_sec": row.get("time_delta_sec"),
                            "altitude_delta_ft": row.get("altitude_delta_ft"),
                        },
                    )
                )

            # 2. Rule: Abrupt Speed Drop
            spd_delta = row.get("speed_delta_kt")
            if pd.notna(spd_delta) and spd_delta <= -self.thresholds.max_speed_change_kt:
                prev_time = self._safe_window_start(obs_time, row.get("time_delta_sec"))
                alerts.append(
                    AnomalyAlert(
                        alert_id=f"ALT-SPD-{uuid.uuid4().hex[:8].upper()}",
                        aircraft_id=aircraft_id,
                        event_type=AnomalyType.ABRUPT_SPEED_DROP,
                        triggered_at_utc=obs_time.to_pydatetime() if hasattr(obs_time, "to_pydatetime") else obs_time,
                        window_start_utc=prev_time.to_pydatetime() if hasattr(prev_time, "to_pydatetime") else prev_time,
                        window_end_utc=obs_time.to_pydatetime() if hasattr(obs_time, "to_pydatetime") else obs_time,
                        detection_method=f"Rule: Abrupt Deceleration (>= {self.thresholds.max_speed_change_kt} kt drop)",
                        threshold_value=-self.thresholds.max_speed_change_kt,
                        observed_value=round(float(spd_delta), 1),
                        unit="kt",
                        anomaly_score=round(min(1.0, abs(spd_delta) / (self.thresholds.max_speed_change_kt * 1.5)), 2),
                        quality_warnings=["Rapid deceleration detected; could be sensor dropout or normal deceleration maneuver."],
                        source_name=source_name,
                        is_synthetic=is_synthetic,
                        supporting_measurements={
                            "speed_delta_kt": round(float(spd_delta), 1),
                            "ground_speed_kt": row.get("ground_speed_kt"),
                            "acceleration_kt_s": row.get("acceleration_kt_s"),
                        },
                    )
                )

            # 3. Rule: Stale / Missing Telemetry Gap
            time_delta = row.get("time_delta_sec")
            if pd.notna(time_delta) and time_delta >= self.thresholds.max_stale_telemetry_sec:
                prev_time = obs_time - pd.Timedelta(seconds=float(time_delta))
                alerts.append(
                    AnomalyAlert(
                        alert_id=f"ALT-GAP-{uuid.uuid4().hex[:8].upper()}",
                        aircraft_id=aircraft_id,
                        event_type=AnomalyType.STALE_TELEMETRY,
                        triggered_at_utc=obs_time.to_pydatetime() if hasattr(obs_time, "to_pydatetime") else obs_time,
                        window_start_utc=prev_time.to_pydatetime() if hasattr(prev_time, "to_pydatetime") else prev_time,
                        window_end_utc=obs_time.to_pydatetime() if hasattr(obs_time, "to_pydatetime") else obs_time,
                        detection_method=f"Rule: Telemetry Interruption (>= {self.thresholds.max_stale_telemetry_sec:,.0f} s gap)",
                        threshold_value=self.thresholds.max_stale_telemetry_sec,
                        observed_value=round(float(time_delta), 1),
                        unit="seconds",
                        anomaly_score=round(min(1.0, float(time_delta) / (self.thresholds.max_stale_telemetry_sec * 2.0)), 2),
                        quality_warnings=["Signal gap detected; likely transponder coverage blind spot or ADS-B receiver range limit."],
                        source_name=source_name,
                        is_synthetic=is_synthetic,
                        supporting_measurements={
                            "gap_seconds": round(float(time_delta), 1),
                            "last_known_altitude": row.get("altitude_ft"),
                        },
                    )
                )
            # 4. Rule: Low Altitude Speed Exceedance (FAA § 91.117 / ICAO 250 kt limit below 10,000 ft)
            alt = row.get("altitude_ft")
            spd = row.get("ground_speed_kt")
            if pd.notna(alt) and pd.notna(spd) and 1000 <= alt <= 10000 and spd >= 275.0:
                prev_time = obs_time - pd.Timedelta(seconds=10)
                alerts.append(
                    AnomalyAlert(
                        alert_id=f"ALT-SPDEX-{uuid.uuid4().hex[:8].upper()}",
                        aircraft_id=aircraft_id,
                        event_type=AnomalyType.LOW_ALTITUDE_SPEED_EXCEEDANCE,
                        triggered_at_utc=obs_time.to_pydatetime() if hasattr(obs_time, "to_pydatetime") else obs_time,
                        window_start_utc=prev_time.to_pydatetime() if hasattr(prev_time, "to_pydatetime") else prev_time,
                        window_end_utc=obs_time.to_pydatetime() if hasattr(obs_time, "to_pydatetime") else obs_time,
                        detection_method="Rule: Low Altitude Speed Exceedance (>= 275 kt below 10,000 ft)",
                        threshold_value=250.0,
                        observed_value=round(float(spd), 1),
                        unit="kt",
                        anomaly_score=round(min(1.0, (spd - 250.0) / 75.0), 2),
                        quality_warnings=["High speed at low altitude detected; ATC may have authorized high-speed climb."],
                        source_name=source_name,
                        is_synthetic=is_synthetic,
                        supporting_measurements={
                            "ground_speed_kt": round(float(spd), 1),
                            "altitude_ft": round(float(alt), 1),
                            "origin_country": row.get("origin_country", "Unknown"),
                        },
                    )
                )

        return alerts

    def detect_isolation_forest_anomalies(
        self, df_features: pd.DataFrame, contamination: float = 0.05
    ) -> List[AnomalyAlert]:
        """Detect statistical outliers using scikit-learn Isolation Forest.
        
        Only runs when at least min_observations_for_ml records with valid numeric features exist.
        """
        alerts: List[AnomalyAlert] = []
        if df_features.empty or len(df_features) < self.thresholds.min_observations_for_ml:
            return alerts

        feature_cols = ["effective_vrate_fpm", "speed_delta_kt", "altitude_ft", "ground_speed_kt"]
        available_cols = [c for c in feature_cols if c in df_features.columns and df_features[c].notna().any()]

        # Filter rows with sufficient numeric features
        valid_mask = df_features[available_cols].notna().all(axis=1)
        sub_df = df_features[valid_mask].copy()

        if len(sub_df) < self.thresholds.min_observations_for_ml:
            return alerts

        X = sub_df[available_cols].values
        model = IsolationForest(
            contamination=contamination,
            random_state=42,
            n_estimators=100,
        )
        preds = model.fit_predict(X)  # -1 for anomaly, 1 for normal
        scores = -model.score_samples(X)  # higher means more anomalous

        anomalies = sub_df[preds == -1].copy()
        anomaly_scores = scores[preds == -1]

        for (_, row), score in zip(anomalies.iterrows(), anomaly_scores):
            obs_time = row["timestamp"]
            aircraft_id = str(row.get("aircraft_id", "UNKNOWN"))
            td = row.get("time_delta_sec")
            td_sec = float(td) if pd.notna(td) and td is not None else 10.0
            prev_time = obs_time - pd.Timedelta(seconds=td_sec)

            alerts.append(
                AnomalyAlert(
                    alert_id=f"ALT-IF-{uuid.uuid4().hex[:8].upper()}",
                    aircraft_id=aircraft_id,
                    event_type=AnomalyType.ISOLATION_FOREST_OUTLIER,
                    triggered_at_utc=obs_time.to_pydatetime() if hasattr(obs_time, "to_pydatetime") else obs_time,
                    window_start_utc=prev_time.to_pydatetime() if hasattr(prev_time, "to_pydatetime") else prev_time,
                    window_end_utc=obs_time.to_pydatetime() if hasattr(obs_time, "to_pydatetime") else obs_time,
                    detection_method=f"Isolation Forest (contamination={contamination}, score={score:.2f})",
                    threshold_value=contamination,
                    observed_value=round(float(score), 3),
                    unit="anomaly score",
                    anomaly_score=round(float(score), 2),
                    quality_warnings=[
                        "Statistical outlier only; uncalibrated risk; not evidence of an emergency or fault."
                    ],
                    source_name=str(row.get("source", "Telemetry Stream")),
                    is_synthetic=bool(row.get("is_synthetic", True)),
                    supporting_measurements={
                        "isolation_forest_score": round(float(score), 3),
                        "effective_vrate_fpm": row.get("effective_vrate_fpm"),
                        "speed_delta_kt": row.get("speed_delta_kt"),
                        "altitude_ft": row.get("altitude_ft"),
                        "ground_speed_kt": row.get("ground_speed_kt"),
                    },
                )
            )

        return alerts
