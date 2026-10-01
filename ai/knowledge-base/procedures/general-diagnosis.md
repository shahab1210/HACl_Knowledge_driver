# General Industrial IoT Fault Diagnosis Workflow

## Purpose and Scope
This procedure defines the standardized, multi-stage diagnostic reasoning workflow for industrial rotating machinery (electric motors, centrifugal pumps, and mechanical drives) monitored via industrial IoT telemetry. The goal is to provide a systematic methodology for moving from real-time sensor anomalies to validated root-cause diagnosis and corrective maintenance recommendations without premature conclusions.

---

## Diagnostic Workflow Architecture

```
   +-----------------------------------------------------------+
   | Stage 1: Continuous Telemetry Ingestion & Anomaly Triage  |
   | (Rule/Threshold Violation, Rate-of-Change, Signal Health)  |
   +-----------------------------+-----------------------------+
                                 |
                                 v
   +-----------------------------------------------------------+
   | Stage 2: Signal Integrity & Sensor Anomaly Verification   |
   | (Check for Flatlines, Implausible Values, Power/Wiring)   |
   +-----------------------------+-----------------------------+
                                 | Valid Physics Confirmed
                                 v
   +-----------------------------------------------------------+
   | Stage 3: Multi-Sensor Cross-Correlation & Pattern Mapping |
   | (Correlate Temp + Vib + Current + Pressure + Humidity)    |
   +-----------------------------+-----------------------------+
                                 |
                                 v
   +-----------------------------------------------------------+
   | Stage 4: Differential Diagnosis & Candidate Ranking       |
   | (Evaluate Hypotheses: Mechanical vs Electrical vs Fluid)  |
   +-----------------------------+-----------------------------+
                                 |
                                 v
   +-----------------------------------------------------------+
   | Stage 5: Safe Physical Inspection & On-Site Verification  |
   | (LOTO, Visual, Thermography, Dial Indicators, Gauges)     |
   +-----------------------------+-----------------------------+
                                 |
                                 v
   +-----------------------------------------------------------+
   | Stage 6: Corrective Action, Verification & Baseline Reset |
   +-----------------------------------------------------------+
```

---

## Step-by-Step Procedure

### Stage 1: Telemetry Ingestion & Anomaly Triage
1. **Detect Out-of-Envelope Readings:** Continuously compare incoming sensor telemetry against established baseline thresholds, operating envelopes, and statistical trend boundaries.
2. **Evaluate Rate of Change ($\Delta / \Delta t$):** Distinguish between instantaneous step changes (often instrumentation artifacts) and progressive exponential or linear drifts (indicative of true physical degradation).
3. **Assess Severity Tier:**
   - **Informational / Low:** Minor baseline drift within allowable operating tolerance.
   - **Medium / Warning:** Approaching operational boundary; accelerated monitoring and trending required.
   - **Critical / Danger:** Exceeded maximum safe operational threshold; high risk of catastrophic equipment damage or personnel hazard.

### Stage 2: Signal Integrity & Sensor Validation
Before declaring a mechanical or electrical machinery breakdown, eliminate instrumentation errors:
1. **Physical Plausibility Check:** Evaluate whether the reading violates thermodynamic or electrical laws (e.g., stator temperature jumping 50 °C within 1 second, or negative fluid pressure on a standard gauge).
2. **Dynamic Variance Check:** Detect frozen signals where sensor values remain perfectly constant down to micro-decimals across varying operational duty cycles.
3. **Cross-Check Complementary Sensors:**
   - If motor current indicates running state, vibration and pressure should reflect operational dynamics.
   - If one sensor contradicts all other physical channels, isolate the issue under [FAULT-010: Sensor Anomaly](../faults/sensor-anomaly.md).

### Stage 3: Multi-Sensor Cross-Correlation Matrix
Correlate simultaneous telemetry parameters to classify the problem domain:

| Temperature | Vibration | Current | Pressure | Primary Diagnostic Hypothesis |
| :--- | :--- | :--- | :--- | :--- |
| **High** | **High** | **Moderate/High** | Normal | [FAULT-001: Bearing Overheating](../faults/bearing-overheating.md) or [FAULT-002: Bearing Wear](../faults/bearing-wear.md) |
| **High** | Normal/Mod | **High** | High/Normal | [FAULT-003: Motor Overheating](../faults/motor-overheating.md) or [FAULT-004: Motor Overcurrent](../faults/motor-overcurrent.md) |
| Normal | **High** | Normal | Normal | [FAULT-005: Excessive Motor Vibration](../faults/motor-vibration.md) (Unbalance, Misalignment) |
| Normal/Mod | **High (Broadband)**| Erratic/Low | **Depressed/Swinging** | [FAULT-006: Pump Cavitation](../faults/pump-cavitation.md) |
| **Spike** | Squeal / Friction | **Very Low** | **Zero / Ambient** | [FAULT-007: Pump Dry Running](../faults/pump-dry-running.md) |
| Normal | Normal | Low / High | **Low** | [FAULT-008: Low Pressure](../faults/low-pressure.md) (Pipe leak or wear ring clearance) |
| **High (Casing)** | Moderate | High / Low | **High** | [FAULT-009: High Pressure](../faults/high-pressure.md) (Discharge blockage / Dead-heading) |

### Stage 4: Differential Diagnosis & Candidate Hypotheses
1. Avoid forcing a single premature diagnosis. In many industrial failure modes, identical telemetry symptoms can originate from different mechanisms:
   - Example: A rise in motor temperature and current could indicate an electrical supply issue (under-voltage), a mechanical issue (failing bearings), or a hydraulic issue (jammed pump impeller).
2. Maintain a ranked list of candidate faults ordered by probability and criticality.
3. Determine what specific physical inspections or offline tests are required to confirm or rule out each hypothesis.

### Stage 5: Physical Inspection & Verification
Transfer the digital diagnosis to the physical asset safely:
1. Refer to equipment-specific inspection guides:
   - For electric motor symptoms, execute [Motor Inspection Procedure](motor-inspection.md).
   - For pump and hydraulic symptoms, execute [Pump Inspection Procedure](pump-inspection.md).
2. Utilize secondary diagnostic instruments:
   - Hand-held infrared pyrometer / thermal camera.
   - True-RMS clamp meter.
   - Handheld tri-axial vibration analyzer.
   - Calibrated analog test pressure gauges.

### Stage 6: Corrective Action & Baseline Reset
1. Perform corrective maintenance (lubrication, mechanical alignment, seal replacement, valve adjustment, or sensor rewiring).
2. Verify system recovery under observed test run.
3. Record root cause, corrective measures, and parts replaced in the CMMS (Computerized Maintenance Management System).
4. Update baseline operational profiles in the IoT diagnostic system.
