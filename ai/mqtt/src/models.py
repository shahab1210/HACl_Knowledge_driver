"""
Data models for P13 MQTT + AI Integration Layer.

Defines containers for validated IoT telemetry messages, query formatting,
and asynchronous diagnosis event payloads.
"""

import json
import time
from dataclasses import dataclass, field, asdict
from typing import Optional, Dict, Any, Union


@dataclass
class TelemetryMessage:
    """
    Standardized representation of an IoT sensor telemetry payload received via MQTT.
    Matches the actual schema used by ESP32 sensor simulator and Spring Boot subscriber.
    """
    device_id: str
    temperature: Optional[float] = None
    humidity: Optional[float] = None
    vibration: Optional[float] = None
    current: Optional[float] = None
    pressure: Optional[float] = None
    recorded_at: Optional[str] = None
    received_at: float = field(default_factory=time.time)
    raw_payload: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: Dict[str, Any], received_at: Optional[float] = None) -> "TelemetryMessage":
        # Extract device ID with aliases
        dev_id = (
            data.get("device_id")
            or data.get("deviceId")
            or data.get("device")
            or data.get("id")
            or data.get("node_id")
            or ""
        )

        # Extract temperature
        temp = data.get("temperature")
        if temp is None:
            temp = data.get("temp") or data.get("temperature_c")

        # Extract humidity
        hum = data.get("humidity")
        if hum is None:
            hum = data.get("hum") or data.get("humidity_pct")

        # Extract vibration
        vib = data.get("vibration")
        if vib is None:
            vib = data.get("vib") or data.get("vibration_mms")

        # Extract current
        curr = data.get("current")
        if curr is None:
            curr = data.get("currentValue") or data.get("current_value") or data.get("curr") or data.get("amps")

        # Extract pressure
        press = data.get("pressure")
        if press is None:
            press = data.get("press") or data.get("pressure_bar")

        # Extract recorded_at
        rec_at = data.get("recorded_at") or data.get("timestamp") or data.get("time") or data.get("recordedAt")

        return cls(
            device_id=str(dev_id).strip(),
            temperature=float(temp) if temp is not None else None,
            humidity=float(hum) if hum is not None else None,
            vibration=float(vib) if vib is not None else None,
            current=float(curr) if curr is not None else None,
            pressure=float(press) if press is not None else None,
            recorded_at=str(rec_at) if rec_at is not None else None,
            received_at=received_at if received_at is not None else time.time(),
            raw_payload=data
        )

    def to_dict(self) -> Dict[str, Any]:
        d: Dict[str, Any] = {"device_id": self.device_id}
        if self.temperature is not None:
            d["temperature"] = self.temperature
        if self.humidity is not None:
            d["humidity"] = self.humidity
        if self.vibration is not None:
            d["vibration"] = self.vibration
        if self.current is not None:
            d["current"] = self.current
        if self.pressure is not None:
            d["pressure"] = self.pressure
        if self.recorded_at:
            d["recorded_at"] = self.recorded_at
        return d

    def to_diagnosis_query(self) -> str:
        """
        Convert telemetry values into a descriptive natural-language query
        for P12/P11 semantic retrieval and LLM diagnosis.
        """
        parts = [f"Device {self.device_id} telemetry observation:"]

        readings = []
        if self.temperature is not None:
            readings.append(f"temperature is {self.temperature} °C")
        if self.vibration is not None:
            readings.append(f"vibration is {self.vibration} mm/s")
        if self.current is not None:
            readings.append(f"current is {self.current} A")
        if self.pressure is not None:
            readings.append(f"pressure is {self.pressure} bar")
        if self.humidity is not None:
            readings.append(f"humidity is {self.humidity} %")

        if readings:
            parts.append(", ".join(readings) + ".")
        else:
            parts.append("no numeric sensor parameters reported.")

        parts.append("What is the equipment fault diagnosis, root cause, and recommended action?")
        return " ".join(parts)


@dataclass
class MQTTDiagnosisEvent:
    """
    Encapsulates the complete result of an asynchronous MQTT telemetry diagnosis.
    """
    device_id: str
    topic: str
    telemetry: TelemetryMessage
    diagnosis: Any  # StructuredDiagnosis object or dict
    received_at: float
    diagnosis_started_at: float
    diagnosis_completed_at: float
    latency_seconds: float

    def to_dict(self) -> Dict[str, Any]:
        diag_dict = self.diagnosis.to_dict() if hasattr(self.diagnosis, "to_dict") else self.diagnosis
        return {
            "device_id": self.device_id,
            "topic": self.topic,
            "telemetry": self.telemetry.to_dict(),
            "diagnosis": diag_dict,
            "latency": {
                "received_at": self.received_at,
                "started_at": self.diagnosis_started_at,
                "completed_at": self.diagnosis_completed_at,
                "total_latency_seconds": round(self.latency_seconds, 3)
            }
        }

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent)
