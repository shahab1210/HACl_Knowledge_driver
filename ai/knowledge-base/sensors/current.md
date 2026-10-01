# Current Sensor in Industrial IoT Fault Diagnosis

## 1. What the Sensor Measures
An industrial IoT current sensor measures the electrical current (amperage) flowing through one or more power supply conductors feeding an electric motor or electrical asset. Typical measurement hardware includes non-invasive Current Transformers (CTs), Hall-effect transducers, Rogowski coils, or shunt resistors coupled to high-speed analog-to-digital converters (ADCs). The sensor captures root-mean-square (RMS) current, instantaneous alternating current waveforms, and harmonic frequency components across the three-phase electrical supply.

## 2. What a Normal Reading Generally Represents
A normal current reading indicates that the electric motor is operating comfortably within its rated electrical design parameters and delivering mechanical shaft torque commensurate with the driven load. The current level tracks the mechanical load on the motor shaft, operating below or at the motor nameplate Full Load Amperage (FLA) multiplied by its permissible Service Factor (SF).

> **Important Operational Note:**
> Actual limits depend on the equipment specification, sensor location, operating conditions, and manufacturer recommendations.

For example, an electric motor rated at 10 A FLA operating a centrifugal pump will normally draw between 6.0 A and 9.5 A under steady-state fluid delivery. Drawing less than 3 A often indicates an uncoupled or dry-running pump, whereas drawing continuously above 10.5 A indicates an overload condition.

## 3. What Abnormal Readings Can Indicate
Deviations in electrical current indicate either electrical power supply anomalies or changes in driven mechanical and hydraulic load:
- **Driven Load Overload:** Current exceeding rated FLA caused by high fluid viscosity, jammed impellers, mechanical binding, or excessive flow rate.
- **Under-Voltage or Phase Unbalance:** Operating on degraded line voltage or unbalanced three-phase supply causes the motor to draw higher current to produce rated shaft torque.
- **Low-Load / Unloaded State:** Abrupt drop in current to near no-load baseline, indicating pump dry running, broken coupling, sheared key, or snapped drive belt.
- **Electrical Rotor/Stator Faults:** Low-frequency amplitude modulation (sidebands) around supply frequency caused by broken rotor bars, air-gap eccentricity, or turn-to-turn insulation degradation (Motor Current Signature Analysis - MCSA).
- **Instrumentation Disconnection:** A reading of zero current while the machine is running indicates an open CT circuit, defective burden resistor, or disconnected telemetry wiring.

## 4. Which Faults the Sensor Can Help Identify
Current telemetry provides vital insight into motor electromechanical health and driven load coupling:
- **[FAULT-004: Motor Overcurrent](../faults/motor-overcurrent.md):** Sustained electrical current exceeding nameplate FLA limits.
- **[FAULT-003: Motor Overheating](../faults/motor-overheating.md):** High current directly drives $I^2R$ copper losses that lead to motor thermal overheating.
- **[FAULT-007: Pump Dry Running](../faults/pump-dry-running.md):** Sudden drop in current toward no-load amperage confirms loss of hydraulic load.
- **[FAULT-006: Pump Cavitation](../faults/pump-cavitation.md):** Rapid, erratic current fluctuations caused by fluctuating fluid density across impeller vanes.
- **[FAULT-001: Bearing Overheating](../faults/bearing-overheating.md) & [FAULT-002: Bearing Wear](../faults/bearing-wear.md):** Moderate current increase caused by excessive friction and mechanical drag.
- **[FAULT-010: Sensor Anomaly](../faults/sensor-anomaly.md):** Contradictory current readings (such as zero current when the pump is producing hydraulic pressure).

## 5. Limitations of Using That Sensor Alone
Current monitoring alone cannot provide comprehensive fault diagnosis without integration with mechanical and hydraulic telemetry:
- **Inability to Pinpoint Mechanical Root Causes:** A motor overcurrent alert clearly indicates that the motor is working harder than designed, but current alone cannot differentiate whether the cause is a downstream pipe blockage, bearing seizure, impeller fouling, low line voltage, or severe shaft misalignment.
- **Blindness to Localized Mechanical Faults:** Localized bearing spalls, lubrication dry-out, or minor mechanical unbalance produce negligible changes in overall RMS current until catastrophic failure is imminent.
- **Transient Fluctuations:** Inrush current during motor startup (often 5 to 8 times FLA) and sudden process load surges cause brief, normal current spikes that can trigger false alarms if thresholding lacks duration filtering.
- **Requires Systemic Correlation:** To confirm whether a current change is electrical, mechanical, or hydraulic, current data must be correlated with temperature, vibration, and discharge pressure.
