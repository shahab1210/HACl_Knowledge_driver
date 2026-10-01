"""
Unit tests for P13 TelemetryParser.
"""

import sys
import json
import pytest
from pathlib import Path

SRC_DIR = Path(__file__).resolve().parents[1] / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from models import TelemetryMessage
from parser import TelemetryParser, parse_telemetry
from exceptions import TelemetryParsingError


def test_parse_valid_json_string():
    raw = json.dumps({
        "device_id": "ESP32_001",
        "temperature": 88.5,
        "vibration": 5.4,
        "current": 6.1,
        "pressure": 3.0,
        "humidity": 40.0,
        "recorded_at": "2026-10-01T01:00:00"
    })
    parser = TelemetryParser()
    msg = parser.parse(raw)
    assert isinstance(msg, TelemetryMessage)
    assert msg.device_id == "ESP32_001"
    assert msg.temperature == 88.5
    assert msg.vibration == 5.4
    assert msg.current == 6.1
    assert msg.pressure == 3.0
    assert msg.humidity == 40.0
    assert msg.recorded_at == "2026-10-01T01:00:00"


def test_parse_valid_bytes():
    payload = b'{"device_id": "ESP32_002", "temperature": 45.0, "humidity": 60.0}'
    msg = parse_telemetry(payload)
    assert msg.device_id == "ESP32_002"
    assert msg.temperature == 45.0
    assert msg.humidity == 60.0
    assert msg.vibration is None


def test_parse_valid_dict():
    data = {"device_id": "ESP32_003", "current": 7.5}
    parser = TelemetryParser()
    msg = parser.parse(data)
    assert msg.device_id == "ESP32_003"
    assert msg.current == 7.5


def test_parse_field_aliases():
    data = {
        "deviceId": "ESP32_004",
        "temp": 92.0,
        "vib": 8.1,
        "timestamp": "2026-10-01T01:05:00"
    }
    msg = parse_telemetry(data)
    assert msg.device_id == "ESP32_004"
    assert msg.temperature == 92.0
    assert msg.vibration == 8.1
    assert msg.recorded_at == "2026-10-01T01:05:00"


def test_parse_empty_payload_raises_error():
    parser = TelemetryParser()
    with pytest.raises(TelemetryParsingError, match="cannot be None"):
        parser.parse(None)

    with pytest.raises(TelemetryParsingError, match="empty"):
        parser.parse("")

    with pytest.raises(TelemetryParsingError, match="empty"):
        parser.parse(b"   ")


def test_parse_malformed_json_raises_error():
    parser = TelemetryParser()
    with pytest.raises(TelemetryParsingError, match="Malformed JSON"):
        parser.parse("{device_id: invalid_json}")

    with pytest.raises(TelemetryParsingError, match="Malformed JSON"):
        parser.parse(b'{"device_id": "ESP32_001", "temperature": }')


def test_parse_invalid_payload_type():
    parser = TelemetryParser()
    with pytest.raises(TelemetryParsingError, match="Unsupported payload type"):
        parser.parse(12345)

    with pytest.raises(TelemetryParsingError, match="Expected JSON object"):
        parser.parse("[1, 2, 3]")


def test_parse_invalid_utf8_bytes():
    parser = TelemetryParser()
    with pytest.raises(TelemetryParsingError, match="Failed to decode MQTT payload"):
        parser.parse(b"\xff\xfe\xfd")
