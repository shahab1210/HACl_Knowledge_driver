"""
P13 MQTT + AI Integration - Telemetry Parser

Parses raw MQTT message payloads (JSON strings or bytes) into structured
TelemetryMessage instances.
"""

import json
from typing import Any, Dict, Union, Optional

from models import TelemetryMessage
from exceptions import TelemetryParsingError


class TelemetryParser:
    """
    Decodes and parses raw MQTT payloads into TelemetryMessage objects.
    """

    def parse(
        self,
        payload: Union[bytes, str, Dict[str, Any]],
        received_at: Optional[float] = None
    ) -> TelemetryMessage:
        """
        Parse raw payload bytes, string, or dictionary into TelemetryMessage.
        """
        if payload is None:
            raise TelemetryParsingError("MQTT payload cannot be None.")

        data: Dict[str, Any]

        if isinstance(payload, bytes):
            try:
                decoded = payload.decode("utf-8").strip()
            except UnicodeDecodeError as e:
                raise TelemetryParsingError(f"Failed to decode MQTT payload bytes as UTF-8: {e}") from e
            if not decoded:
                raise TelemetryParsingError("MQTT payload bytes are empty.")
            try:
                data = json.loads(decoded)
            except json.JSONDecodeError as e:
                raise TelemetryParsingError(f"Malformed JSON in MQTT payload: {e}") from e

        elif isinstance(payload, str):
            clean_str = payload.strip()
            if not clean_str:
                raise TelemetryParsingError("MQTT payload string cannot be empty or whitespace only.")
            try:
                data = json.loads(clean_str)
            except json.JSONDecodeError as e:
                raise TelemetryParsingError(f"Malformed JSON in MQTT payload: {e}") from e

        elif isinstance(payload, dict):
            data = payload

        else:
            raise TelemetryParsingError(f"Unsupported payload type: {type(payload).__name__}")

        if not isinstance(data, dict):
            raise TelemetryParsingError(f"Expected JSON object (dict) in MQTT payload, got {type(data).__name__}")

        # Parse fields into TelemetryMessage
        try:
            return TelemetryMessage.from_dict(data, received_at=received_at)
        except (ValueError, TypeError) as e:
            raise TelemetryParsingError(f"Failed to parse telemetry fields: {e}") from e


# Functional helper
_default_parser = TelemetryParser()


def parse_telemetry(payload: Union[bytes, str, Dict[str, Any]]) -> TelemetryMessage:
    """Convenience function to parse telemetry using the default parser."""
    return _default_parser.parse(payload)
