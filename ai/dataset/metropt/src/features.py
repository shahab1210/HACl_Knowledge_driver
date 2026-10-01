"""
MetroPT-3 Feature Extractor.
Extracts continuous statistical metrics, machine state distributions,
and domain-specific derived features from APU telemetry.
"""

from typing import Dict, Any, List, Optional
import pandas as pd
import numpy as np


class MetroPTFeatureExtractor:
    """Extracts statistical and domain-specific features from MetroPT-3."""

    CONTINUOUS_SIGNALS = [
        "Oil_temperature",
        "Motor_current",
        "TP2",
        "TP3",
        "H1",
        "DV_pressure",
        "Reservoirs",
    ]

    STATE_SIGNALS = [
        "COMP",
        "DV_eletric",
        "Towers",
        "MPG",
        "LPS",
        "Pressure_switch",
        "Oil_level",
        "Caudal_impulses",
    ]

    STATE_DESCRIPTIONS = {
        "COMP": "Air intake valve control (1.0 = closed/intake blocked, 0.0 = open/compressing)",
        "DV_eletric": "Compressor outlet valve control (1.0 = open under load, 0.0 = closed/offload)",
        "Towers": "Active desiccant drying tower selection (0 = Tower 1, 1 = Tower 2)",
        "MPG": "Main Pressure Governor signal (activates when system pressure drops below 8.2 bar)",
        "LPS": "Low Pressure Safety switch (activates when pressure drops below 7.0 bar critical limit)",
        "Pressure_switch": "Drying towers discharge pressure sensor",
        "Oil_level": "Oil reservoir level sensor (1.0 = low oil level warning)",
        "Caudal_impulses": "Pulse counter representing volumetric airflow delivered from APU to reservoirs",
    }

    def compute_continuous_statistics(self, df: pd.DataFrame) -> Dict[str, Dict[str, float]]:
        """Computes comprehensive distribution statistics for continuous signals."""
        stats = {}
        for col in self.CONTINUOUS_SIGNALS:
            if col in df.columns:
                series = df[col].dropna()
                q25 = float(series.quantile(0.25))
                q75 = float(series.quantile(0.75))
                iqr = float(q75 - q25)
                
                stats[col] = {
                    "count": int(series.count()),
                    "mean": round(float(series.mean()), 3),
                    "std": round(float(series.std()), 3),
                    "min": round(float(series.min()), 3),
                    "p5": round(float(series.quantile(0.05)), 3),
                    "p25": round(q25, 3),
                    "median": round(float(series.median()), 3),
                    "p75": round(q75, 3),
                    "p95": round(float(series.quantile(0.95)), 3),
                    "p99": round(float(series.quantile(0.99)), 3),
                    "max": round(float(series.max()), 3),
                    "iqr": round(iqr, 3),
                }
        return stats

    def compute_state_signal_distributions(self, df: pd.DataFrame) -> Dict[str, Dict[str, Any]]:
        """Computes duty cycles and categorical distributions for machine state signals."""
        state_stats = {}
        total_rows = len(df)
        if total_rows == 0:
            return state_stats

        for col in self.STATE_SIGNALS:
            if col in df.columns:
                series = df[col].dropna()
                val_counts = series.value_counts().to_dict()
                
                # Check if binary (predominantly 0 or 1)
                is_binary = set(val_counts.keys()).issubset({0.0, 1.0, 0, 1})
                active_pct = 0.0
                if is_binary:
                    active_count = int((series == 1.0).sum())
                    active_pct = round((active_count / total_rows) * 100.0, 2)

                formatted_counts = {str(k): int(v) for k, v in val_counts.items()}

                state_stats[col] = {
                    "description": self.STATE_DESCRIPTIONS.get(col, ""),
                    "is_binary": is_binary,
                    "unique_values_count": len(val_counts),
                    "active_percentage": active_pct if is_binary else None,
                    "value_counts": formatted_counts,
                }
        return state_stats

    def compute_correlation_matrix(self, df: pd.DataFrame) -> Dict[str, Dict[str, float]]:
        """Computes pairwise Pearson correlation between continuous signals."""
        cols = [c for c in self.CONTINUOUS_SIGNALS if c in df.columns]
        if not cols:
            return {}
        corr_df = df[cols].corr().round(3)
        return corr_df.to_dict()

    def extract_summary(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Extracts complete feature summary."""
        continuous_stats = self.compute_continuous_statistics(df)
        state_stats = self.compute_state_signal_distributions(df)
        correlation_matrix = self.compute_correlation_matrix(df)

        return {
            "continuous_signals": continuous_stats,
            "machine_state_signals": state_stats,
            "correlation_matrix": correlation_matrix,
        }
