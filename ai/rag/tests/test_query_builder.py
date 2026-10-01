import sys
from pathlib import Path

SRC_DIR = Path(__file__).resolve().parents[1] / "src"

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

import pytest

from query_builder import build_telemetry_query


def test_build_complete_telemetry_query():
    telemetry = {
        "device_id": "MOTOR_01",
        "temperature": 92.4,
        "humidity": 43.2,
        "vibration": 8.1,
        "current": 12.7,
        "pressure": 2.4
    }

    query = build_telemetry_query(telemetry)

    assert "MOTOR_01" in query
    assert "temperature 92.4°C" in query
    assert "humidity 43.2%" in query
    assert "vibration 8.1" in query
    assert "current 12.7 A" in query
    assert "pressure 2.4 bar" in query
    assert "Identify relevant industrial faults." in query


def test_build_query_with_partial_telemetry():
    telemetry = {
        "device_id": "MOTOR_02",
        "temperature": 88.5,
        "vibration": 6.2
    }

    query = build_telemetry_query(telemetry)

    assert "MOTOR_02" in query
    assert "temperature 88.5°C" in query
    assert "vibration 6.2" in query


def test_build_query_without_sensor_values():
    telemetry = {
        "device_id": "MOTOR_03"
    }

    query = build_telemetry_query(telemetry)

    assert "MOTOR_03" in query
    assert "no sensor readings" in query


def test_empty_telemetry_raises_error():
    with pytest.raises(ValueError):
        build_telemetry_query({})


def test_invalid_telemetry_type_raises_error():
    with pytest.raises(TypeError):
        build_telemetry_query("invalid telemetry")
