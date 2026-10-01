"""
Unit tests for P13 AIWorker.
"""

import sys
import time
import pytest
from pathlib import Path
from unittest.mock import MagicMock

SRC_DIR = Path(__file__).resolve().parents[1] / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from models import TelemetryMessage, MQTTDiagnosisEvent
from worker import AIWorker


class MockDiagnosisEngine:
    def __init__(self, response_delay=0.01, should_fail=False):
        self.response_delay = response_delay
        self.should_fail = should_fail
        self.call_count = 0
        self.last_query = None

    def diagnose(self, query: str):
        self.call_count += 1
        self.last_query = query
        if self.should_fail:
            raise RuntimeError("Simulated LLM inference error")
        time.sleep(self.response_delay)
        return {
            "primary_fault": "FAULT-003 Motor Overheating",
            "alternative_faults": ["FAULT-001 Bearing Degradation"],
            "recommended_actions": ["Inspect cooling fan"],
            "risk_assessment": "High risk of motor stator failure",
            "confidence": "high",
            "structured_output": {
                "fault_category": "thermal",
                "severity_level": "critical",
                "recommended_action_summary": "Inspect cooling fan"
            },
            "evidence": [
                {
                    "source": "motor_maintenance_manual.md",
                    "chunk_id": "chunk-001",
                    "score": 0.88,
                    "excerpt": "Temperature exceeding 85°C indicates overheating."
                }
            ],
            "metadata": {
                "rag_chunks_retrieved": 1,
                "model_name": "qwen2.5:1.5b",
                "engine_version": "1.0.0"
            }
        }


def test_worker_lifecycle():
    engine = MockDiagnosisEngine()
    worker = AIWorker(engine=engine, queue_size=10)

    assert not worker._running
    worker.start()
    assert worker._running
    assert worker._thread is not None and worker._thread.is_alive()

    worker.stop()
    assert not worker._running


def test_worker_processes_telemetry_and_triggers_callback():
    engine = MockDiagnosisEngine(response_delay=0.02)
    received_events = []

    def callback(event: MQTTDiagnosisEvent):
        received_events.append(event)

    worker = AIWorker(engine=engine, queue_size=10, on_diagnosis_callback=callback)
    worker.start()

    msg = TelemetryMessage(
        device_id="ESP32_001",
        temperature=95.0,
        vibration=7.2,
        current=8.4
    )

    submitted = worker.submit(topic="iot/ESP32_001/telemetry", telemetry=msg)
    assert submitted is True

    # Wait for processing
    timeout = 2.0
    start = time.time()
    while len(received_events) == 0 and time.time() - start < timeout:
        time.sleep(0.05)

    worker.stop()

    assert len(received_events) == 1
    event = received_events[0]
    assert event.device_id == "ESP32_001"
    assert event.topic == "iot/ESP32_001/telemetry"
    assert event.telemetry.temperature == 95.0
    assert event.diagnosis["primary_fault"] == "FAULT-003 Motor Overheating"
    assert event.diagnosis["confidence"] == "high"
    assert event.latency_seconds > 0

    stats = worker.get_stats()
    assert stats["processed_count"] == 1
    assert stats["error_count"] == 0
    assert stats["dropped_count"] == 0
    assert stats["queue_pending"] == 0


def test_worker_queue_overflow_drops_telemetry():
    # Intentionally do not start the worker so queue fills up
    engine = MockDiagnosisEngine()
    worker = AIWorker(engine=engine, queue_size=2)

    msg1 = TelemetryMessage(device_id="ESP32_001", temperature=50.0)
    msg2 = TelemetryMessage(device_id="ESP32_002", temperature=52.0)
    msg3 = TelemetryMessage(device_id="ESP32_003", temperature=54.0)

    assert worker.submit("topic", msg1) is True
    assert worker.submit("topic", msg2) is True
    # 3rd should overflow and drop
    assert worker.submit("topic", msg3) is False

    stats = worker.get_stats()
    assert stats["dropped_count"] == 1
    assert stats["queue_pending"] == 2


def test_worker_handles_engine_errors_gracefully():
    engine = MockDiagnosisEngine(should_fail=True)
    worker = AIWorker(engine=engine, queue_size=10)
    worker.start()

    msg = TelemetryMessage(device_id="ESP32_001", temperature=95.0)
    worker.submit("topic", msg)

    # Give time for the thread to process and fail
    time.sleep(0.2)
    worker.stop()

    stats = worker.get_stats()
    assert stats["error_count"] == 1
    assert stats["processed_count"] == 0


def test_worker_multiple_callbacks():
    engine = MockDiagnosisEngine()
    calls_a = []
    calls_b = []

    worker = AIWorker(engine=engine, queue_size=10)
    worker.register_callback(lambda e: calls_a.append(e))
    worker.register_callback(lambda e: calls_b.append(e))
    worker.start()

    msg = TelemetryMessage(device_id="ESP32_001", temperature=80.0)
    worker.submit("topic", msg)

    time.sleep(0.2)
    worker.stop()

    assert len(calls_a) == 1
    assert len(calls_b) == 1
