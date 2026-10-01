"""
MetroPT-3 Dataset Validator.
Validates schema integrity, numerical physical boundaries, and enforces strict
dataset isolation (verifying no humidity, no vibration, and no ESP32 mapping).
"""

from typing import Dict, Any, List, Optional
import pandas as pd
import numpy as np


class MetroPTValidator:
    """Validates the schema, domain boundaries, and isolation of MetroPT-3."""

    EXPECTED_COLUMNS = [
        "timestamp",
        "TP2",
        "TP3",
        "H1",
        "DV_pressure",
        "Reservoirs",
        "Oil_temperature",
        "Motor_current",
        "COMP",
        "DV_eletric",
        "Towers",
        "MPG",
        "LPS",
        "Pressure_switch",
        "Oil_level",
        "Caudal_impulses",
    ]

    # Prohibited columns in MetroPT-3 (ensures zero ESP32 simulation contamination)
    PROHIBITED_COLUMNS = [
        "humidity",
        "vibration",
        "vibration_x",
        "vibration_y",
        "vibration_z",
        "accel",
        "accel_x",
        "accel_y",
        "accel_z",
    ]

    # Physical domain boundaries for Metro do Porto APU compressors
    PHYSICAL_BOUNDS = {
        "Oil_temperature": (-20.0, 150.0),  # °C
        "Motor_current": (-1.0, 50.0),      # A (small negative offsets possible due to zero drift)
        "TP2": (-2.0, 20.0),                # bar
        "TP3": (-2.0, 20.0),                # bar
        "H1": (-2.0, 20.0),                 # bar
        "DV_pressure": (-2.0, 20.0),        # bar
        "Reservoirs": (-2.0, 20.0),         # bar
    }

    BINARY_COLUMNS = [
        "COMP",
        "DV_eletric",
        "Towers",
        "MPG",
        "LPS",
        "Pressure_switch",
        "Oil_level",
    ]

    def validate(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Validates the MetroPT-3 dataframe.

        Args:
            df: The loaded pandas DataFrame.

        Returns:
            Dict containing validation results, status, warnings, and errors.
        """
        errors: List[str] = []
        warnings: List[str] = []
        boundary_results: Dict[str, Any] = {}

        # 1. Schema check
        missing_cols = [c for c in self.EXPECTED_COLUMNS if c not in df.columns]
        extra_cols = [c for c in df.columns if c not in self.EXPECTED_COLUMNS]

        if missing_cols:
            errors.append(f"Missing required columns: {missing_cols}")

        schema_valid = (len(missing_cols) == 0)

        # 2. Strict Dataset Isolation Check
        # MetroPT-3 has NO humidity and NO vibration. Verify they do not exist.
        forbidden_present = [c for c in self.PROHIBITED_COLUMNS if c in df.columns]
        if forbidden_present:
            errors.append(
                f"Isolation violation: Forbidden signals found in MetroPT dataset: {forbidden_present}. "
                "MetroPT-3 does NOT contain humidity or vibration."
            )
        isolation_confirmed = (len(forbidden_present) == 0)

        # 3. Timestamp check
        timestamp_valid = False
        if "timestamp" in df.columns:
            if pd.api.types.is_datetime64_any_dtype(df["timestamp"]):
                timestamp_valid = True
            else:
                try:
                    pd.to_datetime(df["timestamp"])
                    timestamp_valid = True
                except Exception as ex:
                    errors.append(f"Timestamp column cannot be parsed as datetime: {ex}")

        # 4. Numerical range / Physical boundary checks
        for signal, (min_val, max_val) in self.PHYSICAL_BOUNDS.items():
            if signal in df.columns:
                col_min = float(df[signal].min())
                col_max = float(df[signal].max())
                out_of_bounds = int(((df[signal] < min_val) | (df[signal] > max_val)).sum())
                
                bound_ok = (out_of_bounds == 0)
                if not bound_ok:
                    warnings.append(
                        f"Signal '{signal}' has {out_of_bounds} values outside expected physical range [{min_val}, {max_val}]: "
                        f"observed min={col_min:.2f}, max={col_max:.2f}"
                    )

                boundary_results[signal] = {
                    "expected_range": [min_val, max_val],
                    "observed_min": col_min,
                    "observed_max": col_max,
                    "out_of_bounds_count": out_of_bounds,
                    "valid": bound_ok,
                }

        # 5. Binary control signal checks
        binary_results: Dict[str, Any] = {}
        for b_col in self.BINARY_COLUMNS:
            if b_col in df.columns:
                unique_vals = sorted(df[b_col].dropna().unique().tolist())
                # Should predominantly be 0.0 or 1.0
                non_binary = int(((df[b_col] < -0.01) | (df[b_col] > 1.01)).sum())
                binary_results[b_col] = {
                    "unique_values_count": len(unique_vals),
                    "unique_sample": unique_vals[:5],
                    "non_binary_count": non_binary,
                    "valid": (non_binary == 0),
                }
                if non_binary > 0:
                    warnings.append(f"Binary control signal '{b_col}' contains {non_binary} non-binary values.")

        is_valid = (len(errors) == 0)

        return {
            "is_valid": is_valid,
            "schema_valid": schema_valid,
            "isolation_confirmed": isolation_confirmed,
            "timestamp_valid": timestamp_valid,
            "missing_columns": missing_cols,
            "extra_columns": extra_cols,
            "forbidden_signals_checked": self.PROHIBITED_COLUMNS,
            "forbidden_signals_found": forbidden_present,
            "boundary_checks": boundary_results,
            "binary_checks": binary_results,
            "warnings_count": len(warnings),
            "warnings": warnings,
            "errors_count": len(errors),
            "errors": errors,
        }
