"""
P13 MQTT + AI Integration - Telemetry Validator

Validates telemetry schema, required fields, and numeric constraints.
Distinguishes invalid data (e.g. non-numeric, NaN, missing device ID) from
abnormal but valid telemetry (e.g. high temperatures/vibrations indicating equipment faults).
"""

import math
from typing import Any
from models import TelemetryMessage
from exceptions import TelemetryValidationError


class TelemetryValidator:
    """
    Validates structural and numeric integrity of TelemetryMessage instances.
    """

    NUMERIC_FIELDS = ["temperature", "humidity", "vibration", "current", "pressure"]

    def validate(self, telemetry: Any) -> bool:
        """
        Validate a TelemetryMessage instance. Raises TelemetryValidationError on failure.
        """
        if not isinstance(telemetry, TelemetryMessage):
            raise TelemetryValidationError(
                f"Expected TelemetryMessage object, got {type(telemetry).__name__}"
            )

        # 1. Validate device_id
        if not telemetry.device_id or not telemetry.device_id.strip():
            raise TelemetryValidationError("Telemetry message is missing required 'device_id'.")

        # 2. Validate numeric fields
        has_at_least_one_reading = False

        for field_name in self.NUMERIC_FIELDS:
            val = getattr(telemetry, field_name)
            if val is not None:
                if not isinstance(val, (int, float)):
                    raise TelemetryValidationError(
                        f"Field '{field_name}' must be numeric (int/float), got {type(val).__name__} ({val})."
                    )
                if math.isnan(val) or math.isinf(val):
                    raise TelemetryValidationError(
                        f"Field '{field_name}' contains invalid non-finite value: {val}."
                    )
                has_at_least_one_reading = True

        if not has_at_least_one_reading:
            raise TelemetryValidationError(
                f"Telemetry message for device '{telemetry.device_id}' contains no valid sensor readings."
            )

        return True


# Functional helper
_default_validator = TelemetryValidator()


def validate_telemetry(telemetry: TelemetryMessage) -> bool:
    """Convenience function to validate telemetry using the default validator."""
    return _default_validator.validate(telemetry)
