"""
Exceptions for P13 MQTT + AI Integration Layer.
"""


class MQTTIntegrationError(Exception):
    """Base exception for all P13 MQTT + AI integration errors."""
    pass


class MQTTConfigError(MQTTIntegrationError, ValueError):
    """Raised when MQTT broker or topic configuration is invalid."""
    pass


class MQTTConnectionError(MQTTIntegrationError):
    """Raised when connection to MQTT broker fails or is lost."""
    pass


class TelemetryParsingError(MQTTIntegrationError, ValueError):
    """Raised when raw MQTT payload is malformed or cannot be parsed as JSON."""
    pass


class TelemetryValidationError(MQTTIntegrationError, ValueError):
    """Raised when telemetry payload fails required field or type validation."""
    pass


class AIWorkerError(MQTTIntegrationError):
    """Raised when background AI worker encounters an unrecoverable error."""
    pass
