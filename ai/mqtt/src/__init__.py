"""
P13 MQTT + AI Integration Package
"""

from exceptions import (
    MQTTIntegrationError,
    MQTTConfigError,
    MQTTConnectionError,
    TelemetryParsingError,
    TelemetryValidationError,
    AIWorkerError,
)

from models import (
    TelemetryMessage,
    MQTTDiagnosisEvent,
)

from config import (
    DEFAULT_MQTT_HOST,
    DEFAULT_MQTT_PORT,
    DEFAULT_MQTT_TOPIC,
    DEFAULT_MQTT_CLIENT_ID,
    DEFAULT_MQTT_QOS,
    DEFAULT_QUEUE_SIZE,
    DEFAULT_OLLAMA_BASE_URL,
    DEFAULT_LLM_MODEL,
    DEFAULT_TOP_K,
    MQTTConfig,
)

from parser import (
    TelemetryParser,
    parse_telemetry,
)

from validator import (
    TelemetryValidator,
    validate_telemetry,
)

from client import (
    MQTTTelemetryClient,
)

from worker import (
    AIWorker,
)

from service import (
    MQTTDiagnosisService,
)

__all__ = [
    # Core Service & Client
    "MQTTDiagnosisService",
    "MQTTTelemetryClient",
    "AIWorker",
    # Parsers & Validators
    "TelemetryParser",
    "parse_telemetry",
    "TelemetryValidator",
    "validate_telemetry",
    # Data Models
    "TelemetryMessage",
    "MQTTDiagnosisEvent",
    # Configuration
    "MQTTConfig",
    "DEFAULT_MQTT_HOST",
    "DEFAULT_MQTT_PORT",
    "DEFAULT_MQTT_TOPIC",
    "DEFAULT_MQTT_CLIENT_ID",
    "DEFAULT_MQTT_QOS",
    "DEFAULT_QUEUE_SIZE",
    "DEFAULT_OLLAMA_BASE_URL",
    "DEFAULT_LLM_MODEL",
    "DEFAULT_TOP_K",
    # Exceptions
    "MQTTIntegrationError",
    "MQTTConfigError",
    "MQTTConnectionError",
    "TelemetryParsingError",
    "TelemetryValidationError",
    "AIWorkerError",
]
