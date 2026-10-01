import sys
from pathlib import Path
import pytest
import pandas as pd

SRC_DIR = Path(__file__).resolve().parents[1] / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from loader import MetroPTLoader


def test_loader_real_sample():
    loader = MetroPTLoader()
    df, audit = loader.load_data(nrows=100)

    assert len(df) == 100
    assert "timestamp" in df.columns
    assert "TP2" in df.columns
    assert "Oil_temperature" in df.columns
    assert "Motor_current" in df.columns

    assert audit["total_rows"] == 100
    assert audit["total_columns"] >= 16
    assert audit["start_time"] is not None
    assert audit["end_time"] is not None
    assert audit["observed_median_interval_sec"] > 0


def test_loader_file_not_found():
    loader = MetroPTLoader(data_path="/non/existent/path/data.csv")
    with pytest.raises(FileNotFoundError):
        loader.load_data()


def test_loader_unnamed_columns_dropped(tmp_path):
    # Create a small CSV with an unnamed index column
    test_csv = tmp_path / "test_unnamed.csv"
    data = (
        ",timestamp,TP2,Oil_temperature,Motor_current\n"
        "0,2020-02-01 00:00:00,-0.01,53.6,0.04\n"
        "10,2020-02-01 00:00:10,-0.01,53.7,0.04\n"
    )
    test_csv.write_text(data)

    loader = MetroPTLoader(data_path=str(test_csv))
    df, audit = loader.load_data()

    assert len(df) == 2
    assert "Unnamed: 0" not in df.columns
    assert list(df.columns) == ["timestamp", "TP2", "Oil_temperature", "Motor_current"]
    assert audit["total_rows"] == 2
    assert audit["total_nulls"] == 0
