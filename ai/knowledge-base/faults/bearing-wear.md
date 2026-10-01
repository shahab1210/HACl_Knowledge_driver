---
id: FAULT-002
title: Bearing Wear
category: mechanical
equipment: motor
severity: high
sensors:
  - vibration
  - temperature
  - current
---

# Bearing Wear

## Description
Bearing wear represents the progressive mechanical deterioration and loss of material from the rolling elements, inner raceway, outer raceway, or cage of an industrial bearing. Typically initiated by fatigue, particulate contamination, inadequate lubrication, or electrical discharge machining (EDM) currents, bearing wear manifests as micro-spalling, flaking, pitting, and looseness. Progression leads to severe mechanical clearance expansion, shaft eccentricity, catastrophic cage collapse, and motor rotor jamming.

## Typical Symptoms
- Sustained increase in mechanical vibration levels, especially in peak and velocity profiles.
- Persistent rattling, rumbling, growling, or clicking acoustic emission originating from the bearing cavity.
- Increased radial or axial shaft looseness detected during operation or coast-down.
- Elevated localized housing temperature arising from raceway roughness and micro-impacts.
- Presence of metallic particles or dark discoloration in grease or oil sampling residue.

## Possible Causes
- Normal lifecycle fatigue wear (L10 bearing life reached or exceeded).
- Abrasive or particulate contamination introduced during maintenance or seal degradation.
- Sustained operation under excessive vibration, unbalance, or external mechanical shock loads.
- Lubrication film breakdown (insufficient viscosity, excessive operating heat, or water contamination).
- Shaft misalignment causing asymmetric load distribution across rolling elements.
- Fluting or pitting caused by parasitic stray shaft currents (VFD-induced capacitive coupling).

## Sensor Indicators

| Sensor Parameter | Observed Pattern | Diagnostic Significance | Correlation with Other Readings |
| :--- | :--- | :--- | :--- |
| **Vibration** | High overall vibration; progressive rise in peak acceleration and velocity | Strongest and earliest indicator of raceway defects and mechanical wear | Precedes severe temperature rise in early-to-mid degradation stages |
| **Temperature** | Gradual upward baseline drift; localized hot spots on bearing housing | Secondary indicator resulting from micro-friction and impact dissipation | Tracks with vibration progression as surface degradation intensifies |
| **Current** | Small, high-frequency torque ripples; subtle increase in RMS current | Micro-variations in rotational drag reflected through the air gap and stator | Correlates with mechanical dragging in advanced wear stages |
| **Pressure** | Steady or nominal unless pump shaft eccentricity compromises seal/impeller | Secondary effect in fluid pumps | Cavitation-induced vibration may mimic or accelerate bearing wear |
| **Humidity** | Ambient; elevated humidity accelerates corrosive pitting | Environmental contributor | Prolonged high humidity leads to rust and premature spalling |

## Recommended Checks
1. Perform high-resolution spectral vibration analysis: check for Ball Pass Frequency Outer race (BPFO), Ball Pass Frequency Inner race (BPFI), Ball Spin Frequency (BSF), and Fundamental Train Frequency (FTF) harmonics.
2. Check crest factor and peak-to-peak acceleration to detect impulsive impacts from surface spalls.
3. Isolate motor, tag out power, and manually test shaft for radial and axial play using a dial indicator.
4. Extract lubricant sample and inspect under magnification or perform ferrographic oil analysis for metal debris.
5. Inspect mechanical seals and oil deflectors for wear, contamination ingress, or oil leakage.
6. Verify alignment and soft foot conditions across motor foundation and coupling.

## Safety
- Mechanical failure risk: Severely worn bearings risk sudden cage failure, shaft seizure, and catastrophic motor stall under load.
- Lockout/Tagout (LOTO): Machine must be fully de-energized, locked, and tagged out prior to physical contact, dial indicator mounting, or manual shaft rotation.
- Eye and Hand Protection: Wear protective goggles and gloves when handling contaminated lubricant samples and rotating components.

## Related Faults
- [FAULT-001: Bearing Overheating](bearing-overheating.md)
- [FAULT-005: Excessive Motor Vibration](motor-vibration.md)
- [FAULT-004: Motor Overcurrent](motor-overcurrent.md)
