"""
P13 MQTT + AI Integration - Non-blocking Background AI Worker

Manages an asynchronous, bounded queue for incoming telemetry messages,
triggering P12 Diagnosis Engine inference in a dedicated worker thread so that
the MQTT network event loop is never blocked.
"""

import sys
import time
import queue
import logging
import threading
from pathlib import Path
from typing import Optional, Any, Callable, List, Dict

from models import TelemetryMessage, MQTTDiagnosisEvent
from exceptions import AIWorkerError
from loader import load_diagnosis_engine

logger = logging.getLogger("MQTT_AI_Worker")


class AIWorker:
    """
    Background worker thread processing telemetry diagnosis tasks from a thread-safe queue.
    """

    def __init__(
        self,
        engine: Optional[Any] = None,
        queue_size: int = 50,
        on_diagnosis_callback: Optional[Callable[[MQTTDiagnosisEvent], None]] = None,
        top_k: int = 3,
        model: Optional[str] = None,
        base_url: Optional[str] = None
    ):
        self.queue_size = queue_size
        self._queue: queue.Queue = queue.Queue(maxsize=queue_size)
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._callbacks: List[Callable[[MQTTDiagnosisEvent], None]] = []

        if on_diagnosis_callback:
            self._callbacks.append(on_diagnosis_callback)

        if engine is not None:
            self.engine = engine
        else:
            self.engine = load_diagnosis_engine(
                top_k=top_k,
                model=model,
                base_url=base_url
            )

        # Telemetry statistics
        self._stats = {
            "processed_count": 0,
            "error_count": 0,
            "dropped_count": 0,
            "last_event": None
        }
        self._lock = threading.Lock()

    def register_callback(self, callback: Callable[[MQTTDiagnosisEvent], None]) -> None:
        """Register a subscriber callback to receive completed diagnosis events."""
        if callable(callback) and callback not in self._callbacks:
            self._callbacks.append(callback)

    def submit(self, topic: str, telemetry: TelemetryMessage) -> bool:
        """
        Submit a telemetry message to the worker queue.
        Non-blocking: if queue is full, logs a warning and returns False.
        """
        item = (topic, telemetry, telemetry.received_at)
        try:
            self._queue.put_nowait(item)
            return True
        except queue.Full:
            with self._lock:
                self._stats["dropped_count"] += 1
            logger.warning(
                f"AI worker queue is full ({self.queue_size}). Dropping telemetry from device '{telemetry.device_id}'."
            )
            return False

    def start(self) -> None:
        """Start the background worker thread."""
        if self._running:
            return

        self._running = True
        self._thread = threading.Thread(target=self._run_loop, daemon=True, name="MQTT-AIWorker-Thread")
        self._thread.start()

    def stop(self, timeout: float = 3.0) -> None:
        """Signal the worker thread to stop and wait for termination."""
        if not self._running:
            return

        self._running = False
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=timeout)

    def _run_loop(self) -> None:
        """Worker loop continuously popping items and executing P12 diagnosis."""
        while self._running:
            try:
                # Wait with timeout so thread can exit cleanly when _running is False
                item = self._queue.get(timeout=0.5)
            except queue.Empty:
                continue

            topic, telemetry, received_at = item
            start_time = time.time()

            try:
                query = telemetry.to_diagnosis_query()
                structured_diag = self.engine.diagnose(query=query)
                completed_time = time.time()
                total_latency = completed_time - received_at

                event = MQTTDiagnosisEvent(
                    device_id=telemetry.device_id,
                    topic=topic,
                    telemetry=telemetry,
                    diagnosis=structured_diag,
                    received_at=received_at,
                    diagnosis_started_at=start_time,
                    diagnosis_completed_at=completed_time,
                    latency_seconds=total_latency
                )

                with self._lock:
                    self._stats["processed_count"] += 1
                    self._stats["last_event"] = event

                # Dispatch to all registered callbacks
                for cb in self._callbacks:
                    try:
                        cb(event)
                    except Exception as e:
                        logger.error(f"Error in diagnosis event callback: {e}", exc_info=True)

            except Exception as e:
                with self._lock:
                    self._stats["error_count"] += 1
                logger.error(f"AI diagnosis execution failed for device '{telemetry.device_id}': {e}", exc_info=True)

            finally:
                self._queue.task_done()

    def get_stats(self) -> Dict[str, Any]:
        """Return worker performance and queue statistics."""
        with self._lock:
            return {
                "queue_pending": self._queue.qsize(),
                "processed_count": self._stats["processed_count"],
                "error_count": self._stats["error_count"],
                "dropped_count": self._stats["dropped_count"],
                "last_event": self._stats["last_event"]
            }
