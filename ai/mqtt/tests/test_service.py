"""
Unit tests for P13 MQTTDiagnosisService.
"""

import sys
import json
import pytest
from pathlib import Path
from unittest.mock import MagicMock

SRC_DIR = Path(__file__).resolve().parents[1] / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from config import MQTTConfig
from models import TelemetryMessage, MQTTDiagnosisEvent
from service import MQTTDiagnosisService


class DummyClient:
    def __init__(self):
        self._connected = False
        self.connect_called = False
        self.disconnect_called = False

    def is_connected(self):
        return self._connected

    def connect(self):
        self._connected = True
        self.connect_called = True

    def disconnect(self):
        self._connected = False
        self.disconnect_called = True


class DummyWorker:
    def __init__(self):
        self.start_called = False
        self.stop_called = False
        self.submitted = []
        self.callbacks = []

    def start(self):
        self.start_called = True

    def stop(self):
        self.stop_called = True

    def register_callback(self, cb):
        self.callbacks.append(cb)

    def submit(self, topic, telemetry):
        self.submitted.append((topic, telemetry))
        return True

    def get_stats(self):
        return {
            "queue_pending": 0,
            "processed_count": len(self.submitted),
            "error_count": 0,
            "dropped_count": 0,
            "last_event": None
        }


def test_service_lifecycle():
    client = DummyClient()
    worker = DummyWorker()
    config = MQTTConfig(host="127.0.0.1", port=1883, topic="iot/ESP32_001/telemetry")

    service = MQTTDiagnosisService(
        config=config,
        client=client,
        worker=worker
    )

    service.start()
    assert worker.start_called is True
    assert client.connect_called is True
    assert client.is_connected() is True

    status = service.get_status()
    assert status["mqtt_connected"] is True
    assert status["broker"] == "127.0.0.1:1883"
    assert status["topic"] == "iot/ESP32_001/telemetry"

    service.stop()
    assert client.disconnect_called is True
    assert worker.stop_called is True
    assert client.is_connected() is False


def test_service_processes_valid_message():
    client = DummyClient()
    worker = DummyWorker()
    service = MQTTDiagnosisService(client=client, worker=worker)

    raw_json = json.dumps({
        "device_id": "ESP32_001",
        "temperature": 92.5,
        "vibration": 6.8,
        "current": 8.0,
        "recorded_at": "2026-10-01T01:00:00"
    }).encode("utf-8")

    service._handle_raw_message("iot/ESP32_001/telemetry", raw_json)

    assert len(worker.submitted) == 1
    topic, tel = worker.submitted[0]
    assert topic == "iot/ESP32_001/telemetry"
    assert tel.device_id == "ESP32_001"
    assert tel.temperature == 92.5
    assert tel.vibration == 6.8


def test_service_drops_malformed_json_gracefully():
    client = DummyClient()
    worker = DummyWorker()
    service = MQTTDiagnosisService(client=client, worker=worker)

    service._handle_raw_message("iot/ESP32_001/telemetry", b"invalid-non-json-bytes")
    assert len(worker.submitted) == 0


def test_service_drops_invalid_telemetry_gracefully():
    client = DummyClient()
    worker = DummyWorker()
    service = MQTTDiagnosisService(client=client, worker=worker)

    # Missing device_id
    invalid_data = json.dumps({"temperature": 50.0}).encode("utf-8")
    service._handle_raw_message("iot/ESP32_001/telemetry", invalid_data)
    assert len(worker.submitted) == 0


def test_service_deduplication_window():
    client = DummyClient()
    worker = DummyWorker()
    service = MQTTDiagnosisService(client=client, worker=worker)

    payload = json.dumps({
        "device_id": "ESP32_001",
        "temperature": 90.0,
        "vibration": 5.0,
        "current": 7.0,
        "recorded_at": "2026-10-01T01:00:00"
    }).encode("utf-8")

    # First send -> enqueued
    service._handle_raw_message("iot/ESP32_001/telemetry", payload)
    assert len(worker.submitted) == 1

    # Immediate identical second send -> ignored by dedup
    service._handle_raw_message("iot/ESP32_001/telemetry", payload)
    assert len(worker.submitted) == 1

    # New reading (e.g. higher temperature) -> enqueued
    payload2 = json.dumps({
        "device_id": "ESP32_001",
        "temperature": 95.0,
        "vibration": 5.0,
        "current": 7.0,
        "recorded_at": "2026-10-01T01:00:01"
    }).encode("utf-8")
    service._handle_raw_message("iot/ESP32_001/telemetry", payload2)
    assert len(worker.submitted) == 2


def test_service_registers_diagnosis_callback():
    client = DummyClient()
    worker = DummyWorker()
    service = MQTTDiagnosisService(client=client, worker=worker)

    cb = lambda event: None
    service.register_diagnosis_callback(cb)
    assert cb in worker.callbacks
