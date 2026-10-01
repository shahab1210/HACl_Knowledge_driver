"""
Unit tests for P13 MQTT data models.
"""

import sys
import json
from pathlib import Path

SRC_DIR = Path(__file__).resolve().parents[1] / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from models import TelemetryMessage, MQTTDiagnosisEvent


def test_telemetry_message_serialization():
    data = {
        "device_id": "ESP32_001",
        "temperature": 95.0,
        "humidity": 45.5,
        "vibration": 7.2,
        "current": 8.4,
        "pressure": 2.1,
        "recorded_at": "2026-10-01T01:00:00"
    }
    msg = TelemetryMessage.from_dict(data)
    assert msg.device_id == "ESP32_001"
    assert msg.temperature == 95.0
    assert msg.vibration == 7.2
    assert msg.current == 8.4

    serialized = msg.to_dict()
    assert serialized["device_id"] == "ESP32_001"
    assert serialized["temperature"] == 95.0
    assert serialized["recorded_at"] == "2026-10-01T01:00:00"


def test_telemetry_to_diagnosis_query():
    msg = TelemetryMessage(
        device_id="ESP32_001",
        temperature=95.0,
        vibration=7.2,
        current=8.4,
        pressure=2.1,
        humidity=45.0
    )
    query = msg.to_diagnosis_query()
    assert "Device ESP32_001 telemetry observation:" in query
    assert "temperature is 95.0 °C" in query
    assert "vibration is 7.2 mm/s" in query
    assert "current is 8.4 A" in query
    assert "pressure is 2.1 bar" in query
    assert "humidity is 45.0 %" in query


def test_mqtt_diagnosis_event_serialization():
    msg = TelemetryMessage(device_id="ESP32_001", temperature=95.0)
    event = MQTTDiagnosisEvent(
        device_id="ESP32_001",
        topic="iot/ESP32_001/telemetry",
        telemetry=msg,
        diagnosis={"primary_fault": "FAULT-003 Motor Overheating", "confidence": "high"},
        received_at=100.0,
        diagnosis_started_at=100.1,
        diagnosis_completed_at=102.5,
        latency_seconds=2.5
    )
    d = event.to_dict()
    assert d["device_id"] == "ESP32_001"
    assert d["topic"] == "iot/ESP32_001/telemetry"
    assert d["latency"]["total_latency_seconds"] == 2.5

    json_str = event.to_json()
    parsed = json.loads(json_str)
    assert parsed["device_id"] == "ESP32_001"
