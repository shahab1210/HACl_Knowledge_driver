# Temperature Sensor in Industrial IoT Fault Diagnosis

## 1. What the Sensor Measures
An industrial IoT temperature sensor measures the thermal state of machinery components, process fluids, or ambient operating environments. In electro-mechanical equipment—such as electric induction motors, centrifugal pumps, and gearboxes—temperature sensors are typically positioned at bearing housings, stator winding end-turns, pump casing volutes, mechanical seal glands, and cooling air discharge paths. Common transducer technologies include Resistance Temperature Detectors (RTDs, e.g., PT100/PT1000), thermocouples (Type K, J), thermistors, and digital infrared surface temperature sensors. The sensor converts thermal energy into a calibrated electrical signal (such as resistance, millivoltage, or an ADC digital count) transmitted via IoT telemetry.

## 2. What a Normal Reading Generally Represents
A normal temperature reading indicates that the equipment has reached thermal equilibrium where internal heat generation (caused by normal electrical $I^2R$ copper losses, iron core magnetic hysteresis, and nominal mechanical friction) is effectively balanced by cooling mechanisms (forced air fans, cooling fins, or circulating process fluids). Under steady-state normal operating conditions, temperatures remain stable within rated insulation limits and manufacturer-specified bearing lubricant thermal envelopes.

> **Important Operational Note:**
> Actual limits depend on the equipment specification, sensor location, operating conditions, and manufacturer recommendations.

For example, in a standard continuous-duty industrial induction motor with Class F insulation, a casing temperature between 40 °C and 70 °C might represent normal operation depending on ambient temperature, whereas exceeding 90 °C to 100 °C indicates thermal distress.

## 3. What Abnormal Readings Can Indicate
Abnormal temperature readings can manifest as sustained elevations, sudden steep upward slopes, or atypical localized thermal gradients:
- **Excessive Mechanical Friction:** Severe heating at bearing caps or shaft seals pointing to inadequate, degraded, or excessive lubrication, or misalignment.
- **Electrical Overload:** Widespread stator frame heating resulting from continuous overcurrent, phase unbalance, or under-voltage operation.
- **Cooling Impairment:** Gradual temperature rise caused by blocked cooling fan cowls, fouled motor fins, or degraded ambient heat exchange.
- **Hydraulic Friction / Dead-heading:** Steep temperature surge inside a pump casing caused by churning liquid when the discharge line is choked or closed.
- **Implausible Values (Extremes/Steps):** Broken thermocouple junctions, disconnected RTDs, or open circuits that register maximum scale, negative values, or erratic steps.

## 4. Which Faults the Sensor Can Help Identify
Temperature telemetry serves as a primary or strong confirmatory indicator for several industrial faults:
- **[FAULT-001: Bearing Overheating](../faults/bearing-overheating.md):** Rapid or continuous temperature rise localized at motor or pump bearing housings.
- **[FAULT-002: Bearing Wear](../faults/bearing-wear.md):** Secondary thermal rise accompanying elevated vibration as surface micro-pitting and spalling degrade raceways.
- **[FAULT-003: Motor Overheating](../faults/motor-overheating.md):** General thermal escalation across motor frame and stator windings.
- **[FAULT-007: Pump Dry Running](../faults/pump-dry-running.md):** Extreme thermal spike at mechanical seal face and pump stuffing box due to lack of liquid lubrication.
- **[FAULT-009: High Pressure](../faults/high-pressure.md):** High casing temperature caused by dead-headed centrifugal pump recirculating fluid.
- **[FAULT-010: Sensor Anomaly](../faults/sensor-anomaly.md):** Disconnected or malfunctioning sensor reporting out-of-range temperatures.

## 5. Limitations of Using That Sensor Alone
While temperature monitoring is vital for machinery health, relying solely on temperature telemetry has significant engineering limitations:
- **Thermal Lag and Inertia:** Machinery components possess substantial thermal mass. Mechanical faults (such as severe bearing cage failure, misalignment, or cavitation) can cause severe structural damage long before sufficient heat propagates to an external sensor probe.
- **Lack of Kinematic Specificity:** An elevated temperature indicates thermal dissipation, but cannot independently differentiate between insufficient grease, excessive grease, shaft misalignment, electrical winding overload, or cooling duct blockage.
- **Sensitivity to Ambient Conditions:** Temperature measurements fluctuate with seasonal variations, day/night thermal cycles, and ventilation drafts, which can mask minor internal fault progression or generate false alarms unless ambient compensation is applied.
- **Requirement for Multi-Sensor Fusion:** Accurate root-cause diagnosis requires cross-correlating temperature with vibration (mechanical dynamics), current (electrical and shaft load), and pressure (hydraulic conditions).
