#!/usr/bin/env python3
"""
CLI entry point for P13 MQTT + AI Integration Layer.

Commands:
- listen: Connect to MQTT broker, listen for telemetry messages, and execute asynchronous AI fault diagnosis.
"""

import sys
import time
import signal
import argparse
from pathlib import Path
from typing import Optional

# Add src to sys.path
SRC_DIR = Path(__file__).resolve().parent / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

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
from service import MQTTDiagnosisService
from models import MQTTDiagnosisEvent


def format_event_output(event: MQTTDiagnosisEvent) -> None:
    """Format and print a diagnosis event to the terminal."""
    tel = event.telemetry
    diag = event.diagnosis

    print("\n==================================================")
    print(f"📡 Telemetry Received — Device: {event.device_id}")
    print(f"Topic: {event.topic}")
    print(f"Received At: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(event.received_at))}")
    print("--------------------------------------------------")
    print("Sensor Readings:")
    if tel.temperature is not None:
        print(f"  • Temperature: {tel.temperature} °C")
    if tel.humidity is not None:
        print(f"  • Humidity:    {tel.humidity} %")
    if tel.vibration is not None:
        print(f"  • Vibration:   {tel.vibration} mm/s")
    if tel.current is not None:
        print(f"  • Current:     {tel.current} A")
    if tel.pressure is not None:
        print(f"  • Pressure:    {tel.pressure} bar")
    if tel.recorded_at:
        print(f"  • Timestamp:   {tel.recorded_at}")

    print("--------------------------------------------------")
    print("🤖 AI Diagnosis Result:")

    # Handle StructuredDiagnosis object or dict
    primary_fault = getattr(diag, "primary_fault", None)
    confidence = getattr(diag, "confidence", None)
    possible_causes = getattr(diag, "possible_causes", [])
    recommended_checks = getattr(diag, "recommended_checks", [])
    knowledge_sources = getattr(diag, "knowledge_sources", [])

    if isinstance(diag, dict):
        primary_fault = diag.get("primary_fault")
        confidence = diag.get("confidence")
        possible_causes = diag.get("possible_causes", [])
        recommended_checks = diag.get("recommended_checks", [])
        knowledge_sources = diag.get("knowledge_sources", [])

    # Primary Fault display
    if primary_fault:
        if hasattr(primary_fault, "fault_id"):
            sim_str = f" (Similarity: {primary_fault.similarity:.4f})" if primary_fault.similarity else ""
            print(f"Primary Fault:    [{primary_fault.fault_id}] {primary_fault.title}{sim_str}")
        else:
            print(f"Primary Fault:    {primary_fault}")
    else:
        print("Primary Fault:    None / Insufficient Evidence")

    # Confidence display
    if confidence:
        if hasattr(confidence, "level"):
            print(f"Confidence Level: {confidence.level.upper()} ({confidence.reason})")
        else:
            print(f"Confidence:       {confidence}")

    # Possible causes
    if possible_causes:
        print(f"Possible Causes ({len(possible_causes)}):")
        for idx, cause in enumerate(possible_causes, 1):
            print(f"  {idx}. {cause}")

    # Recommended actions / checks
    if recommended_checks:
        print(f"Recommended Actions ({len(recommended_checks)}):")
        for idx, check in enumerate(recommended_checks, 1):
            print(f"  {idx}. {check}")

    # Knowledge sources
    if knowledge_sources:
        print(f"Knowledge Sources Grounding ({len(knowledge_sources)}):")
        for ks in knowledge_sources:
            if hasattr(ks, "document_id"):
                print(f"  • [{ks.document_id}] {ks.title} (Chunk: {ks.chunk_id}, Similarity: {ks.similarity:.4f})")
            elif isinstance(ks, dict):
                print(f"  • {ks.get('document_id')}: {ks.get('title')}")

    print(f"Total Latency:    {event.latency_seconds:.2f}s")
    print("==================================================")


def cmd_listen(args):
    """Start MQTT diagnosis listener."""
    config = MQTTConfig(
        host=args.host,
        port=args.port,
        topic=args.topic,
        client_id=args.client_id,
        qos=args.qos,
        queue_size=args.queue_size,
        top_k=args.top_k,
        model=args.model,
        base_url=args.base_url
    )

    message_count = 0
    max_msgs = args.max_messages

    def on_diagnosis(event: MQTTDiagnosisEvent):
        nonlocal message_count
        message_count += 1
        if args.json:
            print(event.to_json())
        else:
            format_event_output(event)

    print("==================================================")
    print("P13 MQTT + AI Diagnosis Service")
    print("==================================================")
    print(f"Broker:           {config.host}:{config.port}")
    print(f"Topic:            {config.topic}")
    print(f"Client ID:        {config.client_id}")
    print(f"Queue Size:       {config.queue_size}")
    print(f"AI Model:         {config.model}")
    print(f"Ollama URL:       {config.base_url}")
    print(f"Top-K Retrieval:  {config.top_k}")
    print("--------------------------------------------------")
    print("Connecting to broker and waiting for telemetry...")
    print("Press Ctrl+C to stop.")
    print("==================================================")

    service = MQTTDiagnosisService(config=config, on_diagnosis=on_diagnosis)

    # Intercept SIGINT / SIGTERM for graceful shutdown
    running = True

    def signal_handler(sig, frame):
        nonlocal running
        print("\n\nShutting down MQTT diagnosis service...")
        running = False

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    try:
        service.start()
        while running:
            time.sleep(0.5)
            if max_msgs is not None and message_count >= max_msgs:
                print(f"\nReached maximum message limit ({max_msgs}). Stopping.")
                break
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(f"\n❌ Service error: {e}", file=sys.stderr)
    finally:
        service.stop()
        stats = service.get_status()
        print("\n--------------------------------------------------")
        print("Service Run Summary:")
        print(f"  Processed Messages: {stats['processed_count']}")
        print(f"  Dropped Messages:   {stats['dropped_count']}")
        print(f"  Errors Encountered: {stats['error_count']}")
        print("==================================================")

    return 0


def cmd_serve(args):
    """Start HTTP bridge server for Spring Boot / external REST clients."""
    from server import run_bridge_server
    run_bridge_server(
        host=args.host,
        port=args.port,
        top_k=args.top_k,
        model=args.model,
        base_url=args.base_url
    )
    return 0


def main():
    parser = argparse.ArgumentParser(
        description="P13/P14 MQTT & AI Diagnosis CLI for IoT Fault Diagnosis Assistant"
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    listen_p = subparsers.add_parser("listen", help="Listen on MQTT topic and run AI fault diagnosis")
    listen_p.add_argument("--host", type=str, default=DEFAULT_MQTT_HOST, help=f"MQTT broker host (default: {DEFAULT_MQTT_HOST})")
    listen_p.add_argument("--port", type=int, default=DEFAULT_MQTT_PORT, help=f"MQTT broker port (default: {DEFAULT_MQTT_PORT})")
    listen_p.add_argument("--topic", type=str, default=DEFAULT_MQTT_TOPIC, help=f"MQTT topic (default: {DEFAULT_MQTT_TOPIC})")
    listen_p.add_argument("--client-id", type=str, default=DEFAULT_MQTT_CLIENT_ID, help="MQTT client ID")
    listen_p.add_argument("--qos", type=int, default=DEFAULT_MQTT_QOS, help="MQTT QoS (default: 0)")
    listen_p.add_argument("--queue-size", type=int, default=DEFAULT_QUEUE_SIZE, help="Queue size (default: 50)")
    listen_p.add_argument("--top-k", type=int, default=DEFAULT_TOP_K, help="Top-K chunks (default: 3)")
    listen_p.add_argument("--model", type=str, default=DEFAULT_LLM_MODEL, help="Generative LLM model")
    listen_p.add_argument("--base-url", type=str, default=DEFAULT_OLLAMA_BASE_URL, help="Ollama base URL")
    listen_p.add_argument("--max-messages", type=int, default=None, help="Stop after N messages")
    listen_p.add_argument("--json", action="store_true", help="Output pure JSON")

    serve_p = subparsers.add_parser("serve", help="Run HTTP bridge server for Spring Boot REST API")
    serve_p.add_argument("--host", type=str, default="0.0.0.0", help="HTTP host (default: 0.0.0.0)")
    serve_p.add_argument("--port", type=int, default=5001, help="HTTP port (default: 5001)")
    serve_p.add_argument("--top-k", type=int, default=DEFAULT_TOP_K, help="Top-K chunks (default: 3)")
    serve_p.add_argument("--model", type=str, default=DEFAULT_LLM_MODEL, help="Generative LLM model")
    serve_p.add_argument("--base-url", type=str, default=DEFAULT_OLLAMA_BASE_URL, help="Ollama base URL")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    if args.command == "listen":
        sys.exit(cmd_listen(args))
    elif args.command == "serve":
        sys.exit(cmd_serve(args))


if __name__ == "__main__":
    main()
