package com.iot.iotfaultdiagnosis;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.iot.iotfaultdiagnosis.entity.SensorReading;
import com.iot.iotfaultdiagnosis.repository.SensorReadingRepository;
import jakarta.annotation.PostConstruct;
import org.eclipse.paho.client.mqttv3.*;
import org.springframework.stereotype.Component;

@Component
public class MqttSubscriber {

    private static final String BROKER = "tcp://localhost:1883";
    private static final String TELEMETRY_TOPIC = "iot/ESP32_001/telemetry";
    private static final String DIAGNOSIS_TOPIC = "iot/+/diagnosis";
    private static final String CLIENT_ID = "spring-boot-subscriber";

    private final SensorReadingRepository sensorReadingRepository;
    private final ObjectMapper objectMapper;
    private final com.iot.iotfaultdiagnosis.service.DiagnosisService diagnosisService;
    private final com.iot.iotfaultdiagnosis.service.alert.AlertDetectionService alertDetectionService;

    public MqttSubscriber(
            SensorReadingRepository sensorReadingRepository,
            ObjectMapper objectMapper,
            com.iot.iotfaultdiagnosis.service.DiagnosisService diagnosisService,
            com.iot.iotfaultdiagnosis.service.alert.AlertDetectionService alertDetectionService) {
        this.sensorReadingRepository = sensorReadingRepository;
        this.objectMapper = objectMapper;
        this.diagnosisService = diagnosisService;
        this.alertDetectionService = alertDetectionService;
    }

    @PostConstruct
    public void startMqtt() {

        try {

            String clientId = CLIENT_ID + "-" + java.util.UUID.randomUUID().toString().substring(0, 8);
            MqttClient client = new MqttClient(BROKER, clientId);

            MqttConnectOptions options = new MqttConnectOptions();
            options.setCleanSession(true);
            options.setAutomaticReconnect(true);

            client.connect(options);

            System.out.println("=================================");
            System.out.println("Connected to MQTT broker!");
            System.out.println("=================================");

            // 1. Subscribe to sensor telemetry topic
            client.subscribe(TELEMETRY_TOPIC, (topic, message) -> {
                try {
                    String payload = new String(message.getPayload());

                    System.out.println("=================================");
                    System.out.println("MQTT Telemetry Received");
                    System.out.println("Topic: " + topic);
                    System.out.println("Payload: " + payload);

                    // Convert JSON into SensorReading object
                    SensorReading sensorReading = objectMapper.readValue(payload, SensorReading.class);

                    // Save data into PostgreSQL
                    sensorReadingRepository.save(sensorReading);

                    System.out.println("Sensor data saved to PostgreSQL!");
                    System.out.println("=================================");

                    // Lightweight real-time alert evaluation
                    alertDetectionService.checkTelemetry(sensorReading);

                } catch (Exception e) {
                    System.err.println("Error processing MQTT telemetry message:");
                    e.printStackTrace();
                }
            });

            // 2. Subscribe to AI diagnosis topic
            client.subscribe(DIAGNOSIS_TOPIC, (topic, message) -> {
                try {
                    String payload = new String(message.getPayload());
                    System.out.println("MQTT Diagnosis Event Received on " + topic);
                    com.iot.iotfaultdiagnosis.dto.response.DiagnosisResponse ingested =
                            diagnosisService.ingestMqttDiagnosis(payload);
                    if (ingested != null) {
                        alertDetectionService.checkDiagnosis(ingested);
                    }
                } catch (Exception e) {
                    System.err.println("Error processing MQTT diagnosis message: " + e.getMessage());
                }
            });

            System.out.println("Subscribed to: " + TELEMETRY_TOPIC + " and " + DIAGNOSIS_TOPIC);

        } catch (MqttException e) {

            System.err.println("MQTT connection failed!");
            e.printStackTrace();
        }
    }
}

// // package com.iot.iotfaultdiagnosis;

// // import org.eclipse.paho.client.mqttv3.*;

// // public class MqttSubscriber {

// // private static final String BROKER = "tcp://localhost:1883";
// // private static final String TOPIC = "iot/ESP32_001/telemetry";
// // private static final String CLIENT_ID = "spring-boot-subscriber";

// // public static void main(String[] args) {

// // try {

// // MqttClient client = new MqttClient(BROKER, CLIENT_ID);

// // MqttConnectOptions options = new MqttConnectOptions();
// // options.setCleanSession(true);

// // client.connect(options);

// // System.out.println("Connected to MQTT broker!");

// // client.subscribe(TOPIC, (topic, message) -> {

// // String payload = new String(message.getPayload());

// // System.out.println("Message received!");
// // System.out.println("Topic: " + topic);
// // System.out.println("Payload: " + payload);
// // });

// // System.out.println("Subscribed to: " + TOPIC);

// // } catch (MqttException e) {

// // e.printStackTrace();
// // }
// // }
// // }

// package com.iot.iotfaultdiagnosis;

// import jakarta.annotation.PostConstruct;
// import org.eclipse.paho.client.mqttv3.*;
// import org.springframework.stereotype.Component;

// @Component
// public class MqttSubscriber {

// private static final String BROKER = "tcp://localhost:1883";
// private static final String TOPIC = "iot/ESP32_001/telemetry";
// private static final String CLIENT_ID = "spring-boot-subscriber";

// @PostConstruct
// public void startMqtt() {

// try {

// MqttClient client = new MqttClient(BROKER, CLIENT_ID);

// MqttConnectOptions options = new MqttConnectOptions();
// options.setCleanSession(true);

// client.connect(options);

// System.out.println("=================================");
// System.out.println("Connected to MQTT broker!");
// System.out.println("=================================");

// client.subscribe(TOPIC, (topic, message) -> {

// String payload = new String(message.getPayload());

// System.out.println("=================================");
// System.out.println("MQTT Message Received");
// System.out.println("Topic: " + topic);
// System.out.println("Payload: " + payload);
// System.out.println("=================================");
// });

// System.out.println("Subscribed to: " + TOPIC);

// } catch (MqttException e) {

// System.err.println("MQTT connection failed!");
// e.printStackTrace();
// }
// }
// }
