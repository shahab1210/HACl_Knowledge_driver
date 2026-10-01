"""
P9 RAG Pipeline - Query Builder

Converts IoT telemetry or user-provided information
into a clean textual query suitable for semantic retrieval.
"""

from typing import Any, Dict


def build_telemetry_query(telemetry: Dict[str, Any]) -> str:
    """
    Convert telemetry data into a natural-language retrieval query.

    Example input:
        {
            "device_id": "MOTOR_01",
            "temperature": 92.4,
            "humidity": 43.2,
            "vibration": 8.1,
            "current": 12.7,
            "pressure": 2.4
        }

    Example output:
        Device MOTOR_01 has temperature 92.4°C,
        humidity 43.2%, vibration 8.1,
        current 12.7 A, and pressure 2.4 bar.
        Identify relevant industrial faults.
    """

    if not isinstance(telemetry, dict):
        raise TypeError("Telemetry must be provided as a dictionary.")

    if not telemetry:
        raise ValueError("Telemetry cannot be empty.")

    device_id = telemetry.get("device_id", "UNKNOWN")

    parts = [f"Device {device_id} has"]

    sensor_values = []

    if "temperature" in telemetry:
        sensor_values.append(
            f"temperature {telemetry['temperature']}°C"
        )

    if "humidity" in telemetry:
        sensor_values.append(
            f"humidity {telemetry['humidity']}%"
        )

    if "vibration" in telemetry:
        sensor_values.append(
            f"vibration {telemetry['vibration']}"
        )

    if "current" in telemetry:
        sensor_values.append(
            f"current {telemetry['current']} A"
        )

    if "pressure" in telemetry:
        sensor_values.append(
            f"pressure {telemetry['pressure']} bar"
        )

    if sensor_values:
        query = parts[0] + " " + ", ".join(sensor_values) + "."
    else:
        query = parts[0] + " no sensor readings."

    query += " Identify relevant industrial faults."

    return query