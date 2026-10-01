import sys
from pathlib import Path
import pandas as pd
import pytest

SRC_DIR = Path(__file__).resolve().parents[1] / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from validator import MetroPTValidator
from loader import MetroPTLoader


def test_validator_with_real_sample():
    loader = MetroPTLoader()
    df, _ = loader.load_data(nrows=50)

    validator = MetroPTValidator()
    results = validator.validate(df)

    assert results["is_valid"] is True
    assert results["schema_valid"] is True
    assert results["isolation_confirmed"] is True
    assert results["timestamp_valid"] is True
    assert len(results["errors"]) == 0


def test_validator_detects_forbidden_signals():
    loader = MetroPTLoader()
    df, _ = loader.load_data(nrows=10)

    # Contaminate df with humidity and vibration (simulating ESP32 confusion)
    bad_df = df.copy()
    bad_df["humidity"] = 45.0
    bad_df["vibration_x"] = 0.02

    validator = MetroPTValidator()
    results = validator.validate(bad_df)

    assert results["is_valid"] is False
    assert results["isolation_confirmed"] is False
    assert any("Isolation violation" in err for err in results["errors"])
    assert "humidity" in results["forbidden_signals_found"]
    assert "vibration_x" in results["forbidden_signals_found"]


def test_validator_detects_missing_columns():
    loader = MetroPTLoader()
    df, _ = loader.load_data(nrows=10)

    incomplete_df = df.drop(columns=["Oil_temperature", "Motor_current"])

    validator = MetroPTValidator()
    results = validator.validate(incomplete_df)

    assert results["is_valid"] is False
    assert results["schema_valid"] is False
    assert "Oil_temperature" in results["missing_columns"]
    assert "Motor_current" in results["missing_columns"]


def test_validator_physical_bounds_warning():
    loader = MetroPTLoader()
    df, _ = loader.load_data(nrows=10)

    extreme_df = df.copy()
    # Inject impossible oil temperature (200°C)
    extreme_df.loc[0, "Oil_temperature"] = 200.0

    validator = MetroPTValidator()
    results = validator.validate(extreme_df)

    # Valid is still true unless schema error, but warning is emitted
    assert results["boundary_checks"]["Oil_temperature"]["valid"] is False
    assert results["warnings_count"] > 0
    assert any("Oil_temperature" in w for w in results["warnings"])
