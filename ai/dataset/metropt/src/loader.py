"""
MetroPT-3 Dataset Loader.
Loads and audits real industrial telemetry from Metro do Porto APU (Air Production Unit).
"""

import os
from pathlib import Path
from typing import Dict, Any, Tuple, Optional
import pandas as pd
import numpy as np


class MetroPTLoader:
    """Loads and audits the MetroPT-3 industrial dataset."""

    DEFAULT_PATH = Path(__file__).resolve().parent.parent / "data" / "metropt3.csv"

    def __init__(self, data_path: Optional[str] = None):
        self.data_path = Path(data_path) if data_path else self.DEFAULT_PATH

    def load_data(
        self,
        nrows: Optional[int] = None,
        sample_fraction: Optional[float] = None
    ) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """
        Loads the MetroPT-3 CSV and produces an audit summary.

        Args:
            nrows: Optional row limit for fast testing.
            sample_fraction: Optional fraction for random sampling.

        Returns:
            Tuple of (cleaned_df, audit_summary_dict).
        """
        if not self.data_path.exists():
            raise FileNotFoundError(f"MetroPT-3 dataset not found at: {self.data_path}")

        # Read CSV. Handle unnamed index column if present.
        df = pd.read_csv(self.data_path, nrows=nrows)

        # Drop unnamed index column if present
        unnamed_cols = [c for c in df.columns if c.startswith("Unnamed:") or c == ""]
        if unnamed_cols:
            df = df.drop(columns=unnamed_cols)

        # Parse timestamp
        if "timestamp" not in df.columns:
            raise ValueError("Required column 'timestamp' missing from dataset.")

        df["timestamp"] = pd.to_datetime(df["timestamp"])

        # Optional sampling
        if sample_fraction is not None and 0.0 < sample_fraction < 1.0:
            df = df.sample(frac=sample_fraction, random_state=42).sort_values("timestamp").reset_index(drop=True)
        else:
            # Ensure chronological order
            if not df["timestamp"].is_monotonic_increasing:
                df = df.sort_values("timestamp").reset_index(drop=True)

        # Calculate data quality and audit statistics
        total_rows = len(df)
        total_cols = len(df.columns)
        null_counts = df.isna().sum().to_dict()
        total_nulls = int(sum(null_counts.values()))
        duplicate_timestamps = int(df["timestamp"].duplicated().sum())

        start_time = str(df["timestamp"].min()) if total_rows > 0 else None
        end_time = str(df["timestamp"].max()) if total_rows > 0 else None

        duration_days = 0.0
        median_interval_sec = 0.0
        mean_interval_sec = 0.0

        if total_rows > 1:
            duration_days = round(
                (df["timestamp"].max() - df["timestamp"].min()).total_seconds() / 86400.0, 2
            )
            time_diffs = df["timestamp"].diff().dropna().dt.total_seconds()
            median_interval_sec = float(time_diffs.median())
            mean_interval_sec = round(float(time_diffs.mean()), 2)

        mem_mb = round(df.memory_usage(deep=True).sum() / (1024 * 1024), 2)

        audit_summary = {
            "source_path": str(self.data_path),
            "total_rows": total_rows,
            "total_columns": total_cols,
            "columns": list(df.columns),
            "start_time": start_time,
            "end_time": end_time,
            "duration_days": duration_days,
            "nominal_sampling_interval_sec": 10.0,
            "observed_median_interval_sec": median_interval_sec,
            "observed_mean_interval_sec": mean_interval_sec,
            "null_values_count": null_counts,
            "total_nulls": total_nulls,
            "duplicate_timestamps": duplicate_timestamps,
            "memory_usage_mb": mem_mb,
            "is_clean": (total_nulls == 0 and duplicate_timestamps == 0),
        }

        return df, audit_summary
