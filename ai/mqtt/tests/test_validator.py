"""
Unit tests for P13 TelemetryValidator.
"""

import sys
import pytest
from pathlib import Path

SRC_DIR = Path(__file__).resolve().parents[1] / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from models import TelemetryMessage
from validator import TelemetryValidator, validate_telemetry
from exceptions import TelemetryValidationError


def test_validator_accepts_valid_telemetry():
    msg = TelemetryMessage(
        device_id="ESP32_001",
        temperature=72.0,
        humidity=45.0,
        vibration=1.5,
        current=4.2,
        pressure=2.0
    )
    validator = TelemetryValidator()
    assert validator.validate(msg) is True
    assert validate_telemetry(msg) is True


def test_validator_accepts_abnormal_fault_telemetry():
    """Validates that high fault-inducing sensor values are accepted without rejection."""
    msg = TelemetryMessage(
        device_id="ESP32_001",
        temperature=120.5,  # Extreme overheating
        vibration=15.8,     # Extreme vibration
        current=25.0        # Extreme overcurrent
    )
    validator = TelemetryValidator()
    assert validator.validate(msg) is True


def test_validator_rejects_missing_device_id():
    validator = TelemetryValidator()

    msg1 = TelemetryMessage(device_id="", temperature=50.0)
    with pytest.raises(TelemetryValidationError, match="missing required 'device_id'"):
        validator.validate(msg1)

    msg2 = TelemetryMessage(device_id="   ", temperature=50.0)
    with pytest.raises(TelemetryValidationError, match="missing required 'device_id'"):
        validator.validate(msg2)


def test_validator_rejects_non_numeric_fields():
    validator = TelemetryValidator()

    msg = TelemetryMessage(device_id="ESP32_001")
    # Manually inject invalid type
    msg.temperature = "HIGH"  # type: ignore
    with pytest.raises(TelemetryValidationError, match="must be numeric"):
        validator.validate(msg)


def test_validator_rejects_nan_and_infinity():
    validator = TelemetryValidator()

    msg_nan = TelemetryMessage(device_id="ESP32_001", temperature=float("nan"))
    with pytest.raises(TelemetryValidationError, match="non-finite value"):
        validator.validate(msg_nan)

    msg_inf = TelemetryMessage(device_id="ESP32_001", vibration=float("inf"))
    with pytest.raises(TelemetryValidationError, match="non-finite value"):
        validator.validate(msg_inf)


def test_validator_rejects_empty_readings():
    validator = TelemetryValidator()
    msg = TelemetryMessage(device_id="ESP32_001")  # No sensor values
    with pytest.raises(TelemetryValidationError, match="contains no valid sensor readings"):
        validator.validate(msg)


def test_validator_rejects_non_telemetry_message_type():
    validator = TelemetryValidator()
    with pytest.raises(TelemetryValidationError, match="Expected TelemetryMessage object"):
        validator.validate({"device_id": "ESP32_001", "temperature": 50.0})
