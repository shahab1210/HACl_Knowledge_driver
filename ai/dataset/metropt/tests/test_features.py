import sys
from pathlib import Path
import pandas as pd
import pytest

SRC_DIR = Path(__file__).resolve().parents[1] / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from features import MetroPTFeatureExtractor
from loader import MetroPTLoader


def test_feature_extractor_continuous_stats():
    loader = MetroPTLoader()
    df, _ = loader.load_data(nrows=100)

    extractor = MetroPTFeatureExtractor()
    stats = extractor.compute_continuous_statistics(df)

    assert "Oil_temperature" in stats
    assert "Motor_current" in stats
    assert "Reservoirs" in stats

    oil_stat = stats["Oil_temperature"]
    assert oil_stat["count"] == 100
    assert oil_stat["min"] <= oil_stat["median"] <= oil_stat["max"]
    assert oil_stat["iqr"] >= 0.0


def test_feature_extractor_state_signals():
    loader = MetroPTLoader()
    df, _ = loader.load_data(nrows=100)

    extractor = MetroPTFeatureExtractor()
    state_stats = extractor.compute_state_signal_distributions(df)

    assert "COMP" in state_stats
    assert "DV_eletric" in state_stats
    assert "LPS" in state_stats

    comp_stat = state_stats["COMP"]
    assert comp_stat["is_binary"] is True
    assert 0.0 <= comp_stat["active_percentage"] <= 100.0


def test_feature_extractor_summary():
    loader = MetroPTLoader()
    df, _ = loader.load_data(nrows=50)

    extractor = MetroPTFeatureExtractor()
    summary = extractor.extract_summary(df)

    assert "continuous_signals" in summary
    assert "machine_state_signals" in summary
    assert "correlation_matrix" in summary
    assert "Oil_temperature" in summary["correlation_matrix"]
