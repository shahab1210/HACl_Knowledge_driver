"""
P13 MQTT + AI Integration - MQTT Client Wrapper

Manages connection, subscription, callback registration, and network loop
using the modern Paho MQTT Callback API Version 2.
"""

import logging
from typing import Optional, Callable, Any

try:
    import paho.mqtt.client as mqtt
    HAS_PAHO = True
except ImportError:
    HAS_PAHO = False
    mqtt = None

from exceptions import MQTTConnectionError, MQTTConfigError

logger = logging.getLogger("MQTT_Client")


class MQTTTelemetryClient:
    """
    Manages MQTT connection and message dispatching using Paho MQTT v2.
    """

    def __init__(
        self,
        host: str = "localhost",
        port: int = 1883,
        topic: str = "iot/ESP32_001/telemetry",
        client_id: str = "ai-diagnosis-subscriber",
        qos: int = 0,
        on_message_callback: Optional[Callable[[str, bytes], None]] = None,
        custom_mqtt_client: Optional[Any] = None
    ):
        self.host = host
        self.port = port
        self.topic = topic
        self.client_id = client_id
        self.qos = qos
        self.on_message_callback = on_message_callback
        self._connected = False

        if custom_mqtt_client is not None:
            self._client = custom_mqtt_client
        else:
            if not HAS_PAHO:
                raise MQTTConnectionError("paho-mqtt library is not installed. Run 'pip install paho-mqtt>=2.0.0'.")
            self._client = mqtt.Client(
                mqtt.CallbackAPIVersion.VERSION2,
                client_id=self.client_id
            )

        self._setup_callbacks()

    def _setup_callbacks(self) -> None:
        """Register Paho MQTT event callbacks."""
        if not hasattr(self._client, "on_connect"):
            return

        def _on_connect(client, userdata, flags, reason_code, properties=None):
            if hasattr(reason_code, "is_failure") and reason_code.is_failure:
                logger.error(f"MQTT connection failed with reason code: {reason_code}")
                self._connected = False
            elif isinstance(reason_code, int) and reason_code != 0:
                logger.error(f"MQTT connection failed with return code: {reason_code}")
                self._connected = False
            else:
                logger.info(f"Connected to MQTT broker at {self.host}:{self.port}")
                self._connected = True
                client.subscribe(self.topic, qos=self.qos)
                logger.info(f"Subscribed to topic: '{self.topic}' (QoS {self.qos})")

        def _on_disconnect(client, userdata, flags, reason_code, properties=None):
            logger.warning(f"Disconnected from MQTT broker: {reason_code}")
            self._connected = False

        def _on_message(client, userdata, msg):
            logger.debug(f"MQTT message received on topic '{msg.topic}' ({len(msg.payload)} bytes)")
            if self.on_message_callback:
                try:
                    self.on_message_callback(msg.topic, msg.payload)
                except Exception as e:
                    logger.error(f"Unhandled error in message callback: {e}", exc_info=True)

        self._client.on_connect = _on_connect
        self._client.on_disconnect = _on_disconnect
        self._client.on_message = _on_message

    def is_connected(self) -> bool:
        """Return true if client is connected to broker."""
        return self._connected

    def connect(self) -> None:
        """Connect to the MQTT broker and start the background network event loop."""
        try:
            self._client.connect(self.host, self.port, keepalive=60)
            if hasattr(self._client, "loop_start"):
                self._client.loop_start()
            self._connected = True
        except Exception as e:
            self._connected = False
            raise MQTTConnectionError(f"Failed to connect to MQTT broker at {self.host}:{self.port}: {e}") from e

    def disconnect(self) -> None:
        """Stop network loop and cleanly disconnect from the broker."""
        try:
            if hasattr(self._client, "loop_stop"):
                self._client.loop_stop()
            if hasattr(self._client, "disconnect"):
                self._client.disconnect()
        except Exception as e:
            logger.warning(f"Error during MQTT disconnect: {e}")
        finally:
            self._connected = False
