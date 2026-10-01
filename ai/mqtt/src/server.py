"""
P14 HTTP Bridge Server for P13/P12 AI Diagnosis Pipeline.

Provides a persistent, lightweight HTTP/JSON REST bridge on localhost:5001
allowing Spring Boot to request real-time on-demand AI fault diagnoses
without executing Python subprocesses per request.
"""

import sys
import json
import time
import logging
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path
from typing import Optional, Any

# Resolve paths
SRC_DIR = Path(__file__).resolve().parent
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from parser import TelemetryParser
from validator import TelemetryValidator
from models import TelemetryMessage, MQTTDiagnosisEvent
from loader import load_diagnosis_engine

logger = logging.getLogger("AIDiagnosisServer")


class AIDiagnosisRequestHandler(BaseHTTPRequestHandler):
    """HTTP Request Handler for AI Diagnosis Bridge."""

    engine = None
    parser = TelemetryParser()
    validator = TelemetryValidator()

    def _send_json(self, status_code: int, data: Any):
        response_bytes = json.dumps(data, indent=2).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(response_bytes)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.end_headers()
        self.wfile.write(response_bytes)

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.end_headers()

    def do_GET(self):
        if self.path in ("/health", "/api/v1/health"):
            self._send_json(200, {
                "status": "UP",
                "service": "ai-diagnosis-bridge",
                "timestamp": time.time()
            })
        else:
            self._send_json(404, {"error": "Not Found", "path": self.path})

    def do_POST(self):
        if self.path in ("/api/v1/diagnose", "/diagnose"):
            start_time = time.time()
            content_length = int(self.headers.get("Content-Length", 0))
            if content_length == 0:
                self._send_json(400, {"error": "Bad Request", "message": "Empty request body"})
                return

            body = self.rfile.read(content_length)
            try:
                data = json.loads(body.decode("utf-8"))
            except Exception as e:
                self._send_json(400, {"error": "Bad Request", "message": f"Malformed JSON: {e}"})
                return

            try:
                telemetry = self.parser.parse(data, received_at=start_time)
                self.validator.validate(telemetry)
            except Exception as e:
                self._send_json(400, {"error": "Bad Request", "message": str(e)})
                return

            if self.engine is None:
                self._send_json(503, {"error": "Service Unavailable", "message": "AI Diagnosis Engine not initialized"})
                return

            try:
                query = telemetry.to_diagnosis_query()
                diag_result = self.engine.diagnose(query=query)
                completed_time = time.time()
                total_latency = completed_time - start_time

                event = MQTTDiagnosisEvent(
                    device_id=telemetry.device_id,
                    topic=f"iot/{telemetry.device_id}/telemetry",
                    telemetry=telemetry,
                    diagnosis=diag_result,
                    received_at=start_time,
                    diagnosis_started_at=start_time,
                    diagnosis_completed_at=completed_time,
                    latency_seconds=total_latency
                )

                self._send_json(200, event.to_dict())

            except Exception as e:
                logger.error(f"Error during AI diagnosis: {e}", exc_info=True)
                self._send_json(500, {"error": "Internal Server Error", "message": str(e)})
        else:
            self._send_json(404, {"error": "Not Found", "path": self.path})

    def log_message(self, format, *args):
        # Suppress noisy default logging
        logger.debug(format % args)


def run_bridge_server(
    host: str = "0.0.0.0",
    port: int = 5001,
    top_k: int = 3,
    model: str = "qwen2.5:1.5b",
    base_url: str = "http://localhost:11434"
):
    """Run persistent HTTP server bridge for AI Diagnosis."""
    logger.info("Initializing P12 Diagnosis Engine for HTTP bridge...")
    engine = load_diagnosis_engine(top_k=top_k, model=model, base_url=base_url)
    AIDiagnosisRequestHandler.engine = engine

    server_address = (host, port)
    httpd = HTTPServer(server_address, AIDiagnosisRequestHandler)
    print(f"🤖 AI Diagnosis HTTP Bridge listening on http://{host}:{port}")
    print(f"Endpoints: POST /api/v1/diagnose, GET /health")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping AI Diagnosis HTTP Bridge...")
    finally:
        httpd.server_close()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    run_bridge_server()
