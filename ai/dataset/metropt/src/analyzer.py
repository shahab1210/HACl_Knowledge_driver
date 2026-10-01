"""
MetroPT-3 Operating-State and Anomaly Analyzer.
Classifies industrial operating states, runs statistical anomaly detection,
and validates findings against ground truth air leak failure events.
"""

from typing import Dict, Any, List, Optional
import pandas as pd
import numpy as np


class MetroPTAnalyzer:
    """Performs operating state classification and anomaly detection on MetroPT-3."""

    # Ground truth failure events published in MetroPT literature
    GROUND_TRUTH_EVENTS = [
        {
            "id": "EV-01",
            "name": "Air Leak Failure Event 1",
            "start": "2020-04-18 00:00:00",
            "end": "2020-04-18 23:59:59",
            "failure_type": "Air Leak / Excessive Workload",
        },
        {
            "id": "EV-02",
            "name": "Air Leak Failure Event 2",
            "start": "2020-05-29 23:30:00",
            "end": "2020-05-30 06:00:00",
            "failure_type": "Air Leak / Compressor Stress",
        },
        {
            "id": "EV-03",
            "name": "Air Leak Failure Event 3",
            "start": "2020-06-05 10:00:00",
            "end": "2020-06-07 14:30:00",
            "failure_type": "Severe Air Leak / Low Pressure Shutdown",
        },
        {
            "id": "EV-04",
            "name": "Air Leak Failure Event 4",
            "start": "2020-07-15 14:30:00",
            "end": "2020-07-15 19:00:00",
            "failure_type": "Air Leak / Thermal Overheating",
        },
    ]

    def classify_operating_states(self, df: pd.DataFrame) -> pd.Series:
        """
        Classifies each observation into industrial compressor operational states:
        - Standby: Motor current < 1.0 A (APU compressor stopped/idling)
        - Offloaded: 1.0 <= Motor current < 5.5 A (Motor running with intake closed)
        - UnderLoad: Motor current >= 5.5 A (Motor running and actively compressing air)
        """
        current = df["Motor_current"]
        states = pd.Series("Standby", index=df.index)
        states[(current >= 1.0) & (current < 5.5)] = "Offloaded"
        states[current >= 5.5] = "UnderLoad"
        return states

    def analyze_operating_states(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Calculates breakdown and statistical properties of each operational state."""
        states = self.classify_operating_states(df)
        total_rows = len(df)
        if total_rows == 0:
            return {}

        state_counts = states.value_counts().to_dict()
        breakdown = {}

        for state_name in ["Standby", "Offloaded", "UnderLoad"]:
            count = state_counts.get(state_name, 0)
            pct = round((count / total_rows) * 100.0, 2)
            sub = df[states == state_name]

            # Approximate duration in hours assuming ~10s per reading
            duration_hours = round((count * 10.0) / 3600.0, 1)

            breakdown[state_name] = {
                "count": count,
                "percentage": pct,
                "duration_hours": duration_hours,
                "mean_oil_temp_c": round(float(sub["Oil_temperature"].mean()), 2) if len(sub) > 0 else 0.0,
                "mean_motor_current_a": round(float(sub["Motor_current"].mean()), 2) if len(sub) > 0 else 0.0,
                "mean_reservoir_pressure_bar": round(float(sub["Reservoirs"].mean()), 2) if len(sub) > 0 else 0.0,
            }

        return breakdown

    def detect_anomalies_iqr(self, df: pd.DataFrame, multiplier: float = 1.5) -> Dict[str, Any]:
        """Detects anomalies using Interquartile Range (IQR) on key continuous signals."""
        signals = ["Oil_temperature", "Motor_current", "Reservoirs"]
        results = {}
        for sig in signals:
            if sig in df.columns:
                series = df[sig].dropna()
                q25 = series.quantile(0.25)
                q75 = series.quantile(0.75)
                iqr = q75 - q25
                lower_bound = q25 - multiplier * iqr
                upper_bound = q75 + multiplier * iqr

                is_anomaly = (series < lower_bound) | (series > upper_bound)
                anomaly_count = int(is_anomaly.sum())
                anomaly_pct = round((anomaly_count / len(series)) * 100.0, 3)

                results[sig] = {
                    "method": "IQR",
                    "multiplier": multiplier,
                    "q25": round(float(q25), 3),
                    "q75": round(float(q75), 3),
                    "iqr": round(float(iqr), 3),
                    "lower_bound": round(float(lower_bound), 3),
                    "upper_bound": round(float(upper_bound), 3),
                    "anomaly_count": anomaly_count,
                    "anomaly_percentage": anomaly_pct,
                }
        return results

    def detect_anomalies_zscore(self, df: pd.DataFrame, threshold: float = 3.0) -> Dict[str, Any]:
        """Detects anomalies using Z-score (> threshold standard deviations from mean)."""
        signals = ["Oil_temperature", "Motor_current", "Reservoirs"]
        results = {}
        for sig in signals:
            if sig in df.columns:
                series = df[sig].dropna()
                mean = series.mean()
                std = series.std()

                if std > 0:
                    z = (series - mean).abs() / std
                    is_anomaly = z > threshold
                    anomaly_count = int(is_anomaly.sum())
                else:
                    anomaly_count = 0

                results[sig] = {
                    "method": "Z-score",
                    "threshold_std": threshold,
                    "mean": round(float(mean), 3),
                    "std": round(float(std), 3),
                    "anomaly_count": anomaly_count,
                    "anomaly_percentage": round((anomaly_count / len(series)) * 100.0, 3),
                }
        return results

    def detect_system_safety_events(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Detects machine safety events and physical stress indicators."""
        total_rows = len(df)
        lps_count = int((df["LPS"] == 1.0).sum()) if "LPS" in df.columns else 0
        high_temp_80_count = int((df["Oil_temperature"] >= 80.0).sum()) if "Oil_temperature" in df.columns else 0
        crit_temp_85_count = int((df["Oil_temperature"] >= 85.0).sum()) if "Oil_temperature" in df.columns else 0
        crit_low_pressure_count = int((df["Reservoirs"] < 7.0).sum()) if "Reservoirs" in df.columns else 0

        return {
            "lps_trips_count": lps_count,
            "lps_trips_pct": round((lps_count / total_rows) * 100.0, 3) if total_rows > 0 else 0.0,
            "high_temp_80c_count": high_temp_80_count,
            "crit_temp_85c_count": crit_temp_85_count,
            "reservoir_below_7bar_count": crit_low_pressure_count,
        }

    def evaluate_ground_truth_events(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """
        Cross-validates operational and anomaly metrics against published failure events.
        Compares failure event windows against the overall dataset baseline.
        """
        baseline_underload_pct = round(
            float((df["Motor_current"] >= 5.5).mean() * 100.0), 2
        )
        baseline_mean_temp = round(float(df["Oil_temperature"].mean()), 2)
        baseline_mean_current = round(float(df["Motor_current"].mean()), 2)

        results = []
        for event in self.GROUND_TRUTH_EVENTS:
            mask = (df["timestamp"] >= event["start"]) & (df["timestamp"] <= event["end"])
            sub = df[mask]
            event_rows = len(sub)

            if event_rows > 0:
                underload_pct = round(float((sub["Motor_current"] >= 5.5).mean() * 100.0), 2)
                mean_temp = round(float(sub["Oil_temperature"].mean()), 2)
                max_temp = round(float(sub["Oil_temperature"].max()), 2)
                mean_current = round(float(sub["Motor_current"].mean()), 2)
                lps_trips = int((sub["LPS"] == 1.0).sum())

                # Ratio of UnderLoad duty cycle during failure compared to normal baseline
                duty_cycle_ratio = round(underload_pct / max(baseline_underload_pct, 0.01), 2)

                results.append({
                    "event_id": event["id"],
                    "name": event["name"],
                    "failure_type": event["failure_type"],
                    "start": event["start"],
                    "end": event["end"],
                    "reading_count": event_rows,
                    "mean_oil_temp_c": mean_temp,
                    "max_oil_temp_c": max_temp,
                    "mean_motor_current_a": mean_current,
                    "underload_percentage": underload_pct,
                    "duty_cycle_ratio_vs_baseline": duty_cycle_ratio,
                    "lps_trips_count": lps_trips,
                    "anomaly_detected": (duty_cycle_ratio >= 3.5 or lps_trips > 0 or mean_temp > 73.0),
                })

        return results

    def run_full_analysis(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Runs complete operating-state and anomaly detection analysis pipeline."""
        operating_states = self.analyze_operating_states(df)
        iqr_anomalies = self.detect_anomalies_iqr(df)
        zscore_anomalies = self.detect_anomalies_zscore(df)
        safety_events = self.detect_system_safety_events(df)
        ground_truth_eval = self.evaluate_ground_truth_events(df)

        return {
            "operating_states": operating_states,
            "iqr_anomalies": iqr_anomalies,
            "zscore_anomalies": zscore_anomalies,
            "safety_events": safety_events,
            "ground_truth_evaluations": ground_truth_eval,
        }
