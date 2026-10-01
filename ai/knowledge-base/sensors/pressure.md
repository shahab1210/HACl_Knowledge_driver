# Pressure Sensor in Industrial IoT Fault Diagnosis

## 1. What the Sensor Measures
An industrial IoT pressure sensor measures static or dynamic fluid pressure exerted by liquids or gases within pipelines, pump suction lines, discharge manifolds, or vessel chambers. Common industrial sensing technologies include piezoresistive strain gauges, ceramic capacitive diaphragms, and piezoelectric pressure transducers. The sensor measures pressure relative to atmospheric pressure (gauge pressure, in bar, PSI, or kPa), absolute zero (absolute pressure), or the difference between two measurement ports (differential pressure, $\Delta P$). The transducer produces an analog signal (e.g., 4–20 mA, 0–10 V) or digital I2C/SPI telemetry transmitted across the IoT edge network.

## 2. What a Normal Reading Generally Represents
A normal pressure reading indicates stable hydraulic or pneumatic equilibrium conforming to the system's design operating point on the pump performance curve (Head vs. Capacity). Normal discharge pressure confirms that the pump is adequately primed, operating at correct speed, overcoming system pipe friction, and delivering the designated process flow rate without hydraulic choking or starvation.

> **Important Operational Note:**
> Actual limits depend on the equipment specification, sensor location, operating conditions, and manufacturer recommendations.

For example, a municipal water booster pump designed for a 3.0 bar network operating normally between 2.8 bar and 3.4 bar demonstrates steady delivery. Dropping below 1.5 bar signals line rupture or starvation, whereas exceeding 4.5 bar signals line blockage or closed isolation valves.

## 3. What Abnormal Readings Can Indicate
Abnormal pressure readings reveal severe hydraulic disruptions, mechanical degradation, or pipeline integrity breaches:
- **Low Pressure / Pressure Loss:** Can indicate pipe ruptures, open drain valves, internal fluid recirculation, severe impeller wear, suction strainer blockage, or pump dry running.
- **High Pressure / Hydraulic Overpressure:** Indicates downstream valve closure, line blockages, clogged filters/strainers, or dead-head pump operation.
- **High-Frequency Pressure Fluctuations:** Characteristic of pump cavitation (vapor cavity collapse), air entrainment, or severe fluid pulsation from reciprocating components.
- **Static Flatline Reading:** Clogged impulse line, sediment-packed sensing diaphragm, or frozen transmitter electronics unresponsive to system state changes.

## 4. Which Faults the Sensor Can Help Identify
Pressure telemetry is the primary diagnostic indicator for hydraulic health and process delivery:
- **[FAULT-008: Low Pressure](../faults/low-pressure.md):** Sustained drop in system delivery pressure below minimum threshold.
- **[FAULT-009: High Pressure](../faults/high-pressure.md):** Dangerous hydraulic overpressure threatening piping and equipment integrity.
- **[FAULT-006: Pump Cavitation](../faults/pump-cavitation.md):** Erratically swinging discharge pressure coupled with depleted suction head.
- **[FAULT-007: Pump Dry Running](../faults/pump-dry-running.md):** Immediate drop to zero or ambient pressure coinciding with motor no-load current.
- **[FAULT-004: Motor Overcurrent](../faults/motor-overcurrent.md):** Correlates whether high motor current is driven by high hydraulic discharge head.
- **[FAULT-010: Sensor Anomaly](../faults/sensor-anomaly.md):** Constant pressure reading despite motor stop/start cycles.

## 5. Limitations of Using That Sensor Alone
While pressure is essential for hydraulic assessment, using pressure sensors in isolation has distinct limitations:
- **Upstream/Downstream Locational Dependence:** A single pressure sensor reflects conditions only at its specific tapping point. A high discharge pressure sensor cannot distinguish between a closed manual valve 2 meters downstream versus a blocked filter 50 meters away without differential pressure taps.
- **Susceptibility to Impulse Line Plugging:** Industrial process fluids carrying slurry, scale, crystallization, or particulate matter easily clog small-bore impulse tubing and snubbers, causing the sensor to display a frozen or sluggish pressure reading.
- **Blindness to Rotating Mechanical Wear:** A pump can maintain normal discharge pressure while its bearings are actively failing, vibrating violently, or overheating, right up until mechanical seizure occurs.
- **Need for Cross-System Correlation:** Diagnosing hydraulic vs. mechanical vs. electrical root causes requires correlating pressure with motor current, bearing vibration, and temperature.
