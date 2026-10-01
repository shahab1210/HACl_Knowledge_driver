import sys
from pathlib import Path
import pandas as pd
import pytest

SRC_DIR = Path(__file__).resolve().parents[1] / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from analyzer import MetroPTAnalyzer
from loader import MetroPTLoader


def test_analyzer_operating_states_classification():
    analyzer = MetroPTAnalyzer()

    # Construct test dataframe with distinct motor currents
    test_df = pd.DataFrame({
        "Motor_current": [0.04, 3.8, 6.8],
        "Oil_temperature": [50.0, 60.0, 75.0],
        "Reservoirs": [9.0, 8.5, 7.8],
    })

    states = analyzer.classify_operating_states(test_df)
    assert states.iloc[0] == "Standby"
    assert states.iloc[1] == "Offloaded"
    assert states.iloc[2] == "UnderLoad"

    breakdown = analyzer.analyze_operating_states(test_df)
    assert "Standby" in breakdown
    assert "Offloaded" in breakdown
    assert "UnderLoad" in breakdown
    assert breakdown["Standby"]["count"] == 1
    assert breakdown["Offloaded"]["count"] == 1
    assert breakdown["UnderLoad"]["count"] == 1


def test_analyzer_iqr_and_zscore():
    loader = MetroPTLoader()
    df, _ = loader.load_data(nrows=200)

    analyzer = MetroPTAnalyzer()
    iqr_res = analyzer.detect_anomalies_iqr(df)
    z_res = analyzer.detect_anomalies_zscore(df)

    assert "Oil_temperature" in iqr_res
    assert "Motor_current" in iqr_res
    assert "Reservoirs" in iqr_res

    assert "Oil_temperature" in z_res
    assert "Motor_current" in z_res
    assert "Reservoirs" in z_res

    assert iqr_res["Oil_temperature"]["anomaly_count"] >= 0
    assert z_res["Oil_temperature"]["anomaly_count"] >= 0


def test_analyzer_ground_truth_events():
    analyzer = MetroPTAnalyzer()
    assert len(analyzer.GROUND_TRUTH_EVENTS) == 4
    assert analyzer.GROUND_TRUTH_EVENTS[0]["id"] == "EV-01"

    loader = MetroPTLoader()
    df, _ = loader.load_data(nrows=100)
    # Even on small slice, evaluate function executes gracefully without error
    evals = analyzer.evaluate_ground_truth_events(df)
    assert isinstance(evals, list)
