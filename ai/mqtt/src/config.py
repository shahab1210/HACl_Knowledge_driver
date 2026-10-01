"""
Configuration settings for P13 MQTT + AI Integration Layer.
"""

import os
from dataclasses import dataclass

DEFAULT_MQTT_HOST = "localhost"
MQTT_HOST = os.getenv("MQTT_HOST", os.getenv("MQTT_BROKER", DEFAULT_MQTT_HOST))

DEFAULT_MQTT_PORT = 1883
MQTT_PORT = int(os.getenv("MQTT_PORT", DEFAULT_MQTT_PORT))

DEFAULT_MQTT_TOPIC = "iot/ESP32_001/telemetry"
MQTT_TOPIC = os.getenv("MQTT_TOPIC", DEFAULT_MQTT_TOPIC)

DEFAULT_MQTT_CLIENT_ID = "ai-diagnosis-subscriber"
MQTT_CLIENT_ID = os.getenv("MQTT_CLIENT_ID", DEFAULT_MQTT_CLIENT_ID)

DEFAULT_MQTT_QOS = 0
MQTT_QOS = int(os.getenv("MQTT_QOS", DEFAULT_MQTT_QOS))

DEFAULT_QUEUE_SIZE = 50
QUEUE_SIZE = int(os.getenv("AI_QUEUE_SIZE", DEFAULT_QUEUE_SIZE))

DEFAULT_OLLAMA_BASE_URL = "http://localhost:11434"
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", DEFAULT_OLLAMA_BASE_URL)

DEFAULT_LLM_MODEL = "qwen2.5:1.5b"
LLM_MODEL = os.getenv("LLM_MODEL", DEFAULT_LLM_MODEL)

DEFAULT_TOP_K = 3
TOP_K = int(os.getenv("RAG_TOP_K", DEFAULT_TOP_K))


@dataclass
class MQTTConfig:
    """
    Encapsulates all runtime configuration for the MQTT consumer and AI worker.
    """
    host: str = DEFAULT_MQTT_HOST
    port: int = DEFAULT_MQTT_PORT
    topic: str = DEFAULT_MQTT_TOPIC
    client_id: str = DEFAULT_MQTT_CLIENT_ID
    qos: int = DEFAULT_MQTT_QOS
    queue_size: int = DEFAULT_QUEUE_SIZE
    base_url: str = DEFAULT_OLLAMA_BASE_URL
    model: str = DEFAULT_LLM_MODEL
    top_k: int = DEFAULT_TOP_K

    @classmethod
    def from_env(cls) -> "MQTTConfig":
        return cls(
            host=os.getenv("MQTT_HOST", os.getenv("MQTT_BROKER", DEFAULT_MQTT_HOST)),
            port=int(os.getenv("MQTT_PORT", DEFAULT_MQTT_PORT)),
            topic=os.getenv("MQTT_TOPIC", DEFAULT_MQTT_TOPIC),
            client_id=os.getenv("MQTT_CLIENT_ID", DEFAULT_MQTT_CLIENT_ID),
            qos=int(os.getenv("MQTT_QOS", DEFAULT_MQTT_QOS)),
            queue_size=int(os.getenv("AI_QUEUE_SIZE", DEFAULT_QUEUE_SIZE)),
            base_url=os.getenv("OLLAMA_BASE_URL", DEFAULT_OLLAMA_BASE_URL),
            model=os.getenv("LLM_MODEL", DEFAULT_LLM_MODEL),
            top_k=int(os.getenv("RAG_TOP_K", DEFAULT_TOP_K))
        )
