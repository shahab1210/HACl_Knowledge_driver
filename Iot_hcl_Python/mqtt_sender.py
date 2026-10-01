
import paho.mqtt.client as mqtt
import json
import time
import random

broker = "localhost"
port = 1883
topic = "iot/ESP32_001/telemetry"

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
client.connect(broker, port)

print("Connected to MQTT broker!")
print("Starting IoT sensor simulation...")
print("Press Ctrl+C to stop.\n")

try:
    while True:

        payload = {
            "device_id": "ESP32_001",
            "temperature": round(random.uniform(24.0, 35.0), 2),
            "humidity": round(random.uniform(45.0, 75.0), 2),
            "vibration": round(random.uniform(1.0, 5.0), 2),
            "current": round(random.uniform(4.0, 8.0), 2),
            "pressure": round(random.uniform(1.5, 3.5), 2)
        }

        message = json.dumps(payload)

        client.publish(topic, message)

        print("Published:", message)

        time.sleep(5)

except KeyboardInterrupt:
    print("\nStopping sensor simulation...")

finally:
    client.disconnect()
    print("Disconnected from MQTT broker.")

# # import paho.mqtt.client as mqtt
# # import json
# # import time

# # broker = "localhost"
# # port = 1883

# # topic = "sender/temp"

# # payload = {
# #     "device_id": "ESP32_001",
# #     "temperature": 25.4,
# #     "humidity": 60
# # }

# # # Create MQTT client using the latest Callback API
# # client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)

# # # Connect to MQTT broker
# # client.connect(broker, port)

# # # Convert Python dictionary to JSON string
# # message = json.dumps(payload)

# # # Start timer
# # start = time.time()

# # # Publish message
# # info = client.publish(topic, message)

# # # Wait until message is published
# # info.wait_for_publish()

# # # End timer
# # end = time.time()

# # print("Message published successfully!")
# # print("Time:", round((end - start) * 1000, 2), "ms")

# # # Disconnect
# # client.disconnect()



# import paho.mqtt.client as mqtt
# import json
# import time

# # MQTT Broker
# broker = "localhost"
# port = 1883

# # P_311 MQTT topic
# topic = "iot/ESP32_001/telemetry"

# # Sensor data
# payload = {
#     "device_id": "ESP32_001",
#     "temperature": 25.4,
#     "humidity": 60.0,
#     "vibration": 2.1,
#     "current": 5.8,
#     "pressure": 2.5
# }

# # Create MQTT client
# client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)

# # Connect to Mosquitto
# client.connect(broker, port)

# # Convert Python dictionary → JSON
# message = json.dumps(payload)

# print("Sending:", message)

# # Publish
# start = time.time()

# info = client.publish(topic, message)
# info.wait_for_publish()

# end = time.time()

# print("Message published successfully!")
# print("Topic:", topic)
# print("Time:", round((end - start) * 1000, 2), "ms")

# # Disconnect
# client.disconnect()