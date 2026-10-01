---
id: FAULT-010
title: Sensor Anomaly
category: instrumentation
equipment: sensor
severity: medium
sensors:
  - temperature
  - vibration
  - current
  - pressure
  - humidity
---

# Sensor Anomaly

## Description
A sensor anomaly occurs when an industrial IoT instrumentation channel generates readings that are physically implausible, frozen, erratic, corrupted, or statistically disconnected from actual machine physics. Such anomalies stem from hardware degradation, loose wiring, signal grounding loops, environmental moisture ingress, analog-to-digital converter (ADC) saturation, or telemetry packet corruption. Failing to distinguish sensor anomalies from genuine machinery faults leads to false alarms, unnecessary emergency shutdowns, or masked catastrophic failures.

## Typical Symptoms
- Unrealistic step changes (e.g., instantaneous jump from 30 °C to 120 °C or zero within one sampling period).
- Flatline or frozen values where dynamic variance drops to exactly zero over extended operating windows.
- Out-of-bounds readings exceeding physical sensor limits (e.g., negative pressures on absolute gauges or current exceeding breaker capacity without trip).
- High-frequency white noise, random telemetry spikes, or dropped MQTT packet payloads.
- Disagreement between redundant sensors or physical contradictions (e.g., motor current reading zero while discharge pressure and vibration indicate full-speed operation).

## Possible Causes
- Loose terminal wiring, loose screw connections, or oxidized wire terminations on sensor terminal blocks.
- Sensor power supply fluctuation, low battery voltage in wireless IoT nodes, or electrical ground loops.
- Mechanical shock or moisture ingress compromising transducer internal electronics or piezoresistive diaphragms.
- Electromagnetic interference (EMI) or radio-frequency interference (RFI) induced by unshielded VFD motor cables.
- Physical detachment or improper mounting: Accelerometer stud loose, thermocouple pulled out of thermowell, or clogged pressure impulse tube.
- Sensor drift resulting from thermal aging, membrane fouling, or mechanical strain beyond transducer limits.

## Sensor Indicators

| Sensor Parameter | Observed Pattern | Diagnostic Significance | Correlation with Other Readings |
| :--- | :--- | :--- | :--- |
| **All Sensors (General)** | Flatline, instantaneous step-jump, or value stuck at full-scale rail (min or max) | Core indicator of instrumentation failure rather than machine physics | Contradicted by related physical parameters |
| **Temperature** | Instantaneous infinite reading (open thermocouple circuit) or negative full-scale | Open or shorted RTD / thermocouple circuit | Motor casing cool to touch while sensor reports extreme thermal trip |
| **Vibration** | Flat zero or constant saturated rail (+/- full scale g) | Disconnected piezo cable, loose mounting stud, or amplifier saturation | Zero vibration while motor current shows machine is fully loaded |
| **Current** | Zero reading or fluctuating noise floor during known running state | CT open circuit, loose burden resistor, or disconnected ADC lead | Zero current while pump generates steady fluid pressure |
| **Pressure** | Static flatline regardless of valve modulation or machine state | Clogged impulse tubing, frozen transducer diaphragm, or zero-shift | Pressure constant despite pump start/stop cycle |
| **Humidity** | 0% or 100% saturation reading | Condensation bridging sensing electrode or disconnected capacitive sensor | Unchanging regardless of ambient seasonal shifts |

## Recommended Checks
1. Validate against secondary instrumentation: Compare IoT telemetry reading with local analog dial gauges, hand-held thermal pyrometers, or clamp meters.
2. Cross-correlate multi-sensor physics: Check if related physical indicators make sense (e.g., does motor current match running state indicated by pressure and vibration?).
3. Inspect physical mounting: Check accelerometer mounting torque, thermowell contact paste, pressure snubber, and impulse line cleanliness.
4. Verify wiring integrity: Inspect signal cable shielding, check for ground loops, test loop resistance, and verify 4-20 mA / 0-10 V analog signals.
5. Check microcontroller / ADC node: Inspect edge compute node (e.g., ESP32) power rail voltage, ADC reference stability, and firmware health.
6. Perform sensor calibration: Apply certified zero and span reference test signals (e.g., hydraulic deadweight tester, temperature dry-well calibrator).

## Safety
- False sense of security: Never ignore a sensor anomaly; a disabled or erroneous sensor can mask an actual developing machine disaster.
- Accidental trip hazard: Bypassing or troubleshooting instrumentation on live safety interlocks can cause unexpected process trips.
- Electrical Safety: Follow safe isolation and low-voltage electrical safety guidelines when probing sensor wires and terminal blocks inside control panels.

## Related Faults
- [FAULT-008: Low Pressure](low-pressure.md)
- [FAULT-009: High Pressure](high-pressure.md)
- [FAULT-003: Motor Overheating](motor-overheating.md)
