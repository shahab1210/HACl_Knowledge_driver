"""
P13 MQTT + AI Integration - Service Orchestrator

Integrates the MQTTTelemetryClient, TelemetryParser, TelemetryValidator,
and AIWorker into a cohesive, high-availability service for IoT telemetry fault diagnosis.
"""

import time
import logging
from typing import Optional, Callable, Any, Dict, List, Set, Tuple

from config import (
    DEFAULT_MQTT_HOST,
    DEFAULT_MQTT_PORT,
    DEFAULT_MQTT_TOPIC,
    DEFAULT_MQTT_CLIENT_ID,
    DEFAULT_MQTT_QOS,
    DEFAULT_QUEUE_SIZE,
    DEFAULT_TOP_K,
    DEFAULT_LLM_MODEL,
    DEFAULT_OLLAMA_BASE_URL,
    MQTTConfig,
)
from models import TelemetryMessage, MQTTDiagnosisEvent
from parser import TelemetryParser
from validator import TelemetryValidator
from client import MQTTTelemetryClient
from worker import AIWorker
from exceptions import TelemetryParsingError, TelemetryValidationError, MQTTIntegrationError

logger = logging.getLogger("MQTT_Diagnosis_Service")


class MQTTDiagnosisService:
    """
    Unified service managing MQTT subscription, telemetry decoding, validation,
    non-blocking queuing, and asynchronous AI fault diagnosis.
    """

    def __init__(
        self,
        config: Optional[MQTTConfig] = None,
        parser: Optional[TelemetryParser] = None,
        validator: Optional[TelemetryValidator] = None,
        worker: Optional[AIWorker] = None,
        client: Optional[MQTTTelemetryClient] = None,
        on_diagnosis: Optional[Callable[[MQTTDiagnosisEvent], None]] = None
    ):
        self.config = config or MQTTConfig()
        self.parser = parser or TelemetryParser()
        self.validator = validator or TelemetryValidator()

        self.worker = worker or AIWorker(
            queue_size=self.config.queue_size,
            top_k=self.config.top_k,
            model=self.config.model,
            base_url=self.config.base_url,
            on_diagnosis_callback=on_diagnosis
        )

        self.client = client or MQTTTelemetryClient(
            host=self.config.host,
            port=self.config.port,
            topic=self.config.topic,
            client_id=self.config.client_id,
            qos=self.config.qos,
            on_message_callback=self._handle_raw_message
        )

        # Sliding window for basic deduplication
        self._dedup_window: List[Tuple[str, Optional[float], Optional[float], Optional[float], str]] = []
        self._max_dedup_size = 50

    def register_diagnosis_callback(self, callback: Callable[[MQTTDiagnosisEvent], None]) -> None:
        """Register a callback for completed diagnosis events."""
        self.worker.register_callback(callback)

    def _handle_raw_message(self, topic: str, payload_bytes: bytes) -> None:
        """
        Internal message handler triggered by MQTT client.
        Parses, validates, deduplicates, and enqueues telemetry without blocking.
        """
        receive_time = time.time()

        # Step 1: Parse JSON payload
        try:
            telemetry = self.parser.parse(payload_bytes, received_at=receive_time)
        except TelemetryParsingError as e:
            logger.warning(f"Rejected unparsable MQTT payload on topic '{topic}': {e}")
            return
        except Exception as e:
            logger.error(f"Unexpected error during telemetry parsing on topic '{topic}': {e}", exc_info=True)
            return

        # Step 2: Validate telemetry schema and numeric constraints
        try:
            self.validator.validate(telemetry)
        except TelemetryValidationError as e:
            logger.warning(f"Rejected invalid telemetry from device '{telemetry.device_id}' on topic '{topic}': {e}")
            return
        except Exception as e:
            logger.error(f"Unexpected error during telemetry validation: {e}", exc_info=True)
            return

        # Step 3: Simple sliding window deduplication
        dedup_key = (
            telemetry.device_id,
            telemetry.temperature,
            telemetry.vibration,
            telemetry.current,
            telemetry.recorded_at or ""
        )
        if dedup_key in self._dedup_window:
            logger.debug(f"Ignoring duplicate telemetry message for device '{telemetry.device_id}'.")
            return

        self._dedup_window.append(dedup_key)
        if len(self._dedup_window) > self._max_dedup_size:
            self._dedup_window.pop(0)

        # Step 4: Submit to non-blocking worker queue
        queued = self.worker.submit(topic=topic, telemetry=telemetry)
        if queued:
            logger.debug(f"Enqueued telemetry for device '{telemetry.device_id}'.")

    def start(self) -> None:
        """Start the background AI worker and connect to the MQTT broker."""
        logger.info("Starting P13 AI Worker thread...")
        self.worker.start()

        logger.info(f"Connecting to MQTT broker at {self.config.host}:{self.config.port}...")
        self.client.connect()

    def stop(self) -> None:
        """Disconnect from the broker and cleanly shut down the AI worker."""
        logger.info("Stopping MQTT client connection...")
        self.client.disconnect()

        logger.info("Stopping P13 AI Worker thread...")
        self.worker.stop()

    def get_status(self) -> Dict[str, Any]:
        """Return combined status of MQTT connection and AI worker."""
        worker_stats = self.worker.get_stats()
        return {
            "mqtt_connected": self.client.is_connected(),
            "broker": f"{self.config.host}:{self.config.port}",
            "topic": self.config.topic,
            "worker_queue_pending": worker_stats["queue_pending"],
            "processed_count": worker_stats["processed_count"],
            "error_count": worker_stats["error_count"],
            "dropped_count": worker_stats["dropped_count"],
        }
